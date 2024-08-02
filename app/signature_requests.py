import os
import datetime
import uuid
from flask import Blueprint, render_template, request, current_app, redirect, url_for, abort, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import SignatureRequest, Signatory
from . import db
from .utils import create_embedded_signature_request, generate_sign_url

signature_requests = Blueprint('signature_requests', __name__)

ALLOWED_EXTENSIONS = { 'pdf' }

# Check if filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Show all requests
@signature_requests.route('/')
@login_required
def index():
    # Query signature requests where the current user is the initiator
    sent_requests = SignatureRequest.query.filter_by(initiator_id=current_user.user_id).all()
    
    # Query signature requests where the current user is a signatory
    received_requests = SignatureRequest.query.filter(SignatureRequest.signatories.any(Signatory.email == current_user.email)).all()
    
    return render_template('signatureRequests/index.html', sent_requests=sent_requests, received_requests=received_requests)

# Create a signature request
@signature_requests.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('signatureRequests/create.html')
    
    if request.method == 'POST':
        # Extract data from the request body
        title = request.form.get('title')
        description = request.form.get('description')
        signatory_names = request.form.getlist('signatory_name[]')
        signatory_emails = request.form.getlist('signatory_email[]')
        signatory_positions = request.form.getlist('signatory_position[]')

        # Save the document to file system
        if 'document' not in request.files:
            return 'Document is required'

        file = request.files['document']

        if file.filename == '':
            return 'No selected file'

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']

            # Create the directory if it doesn't exist
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Generate a unique filename using timestamp and uuid
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            random_chars = str(uuid.uuid4())[:8]
            unique_filename = f"{timestamp}_{random_chars}_{filename}"

            file.save(os.path.join(upload_folder, unique_filename))

            # Save the signature request details to the database
            new_signature_request = SignatureRequest(
                title=title,
                description=description,
                document_url=unique_filename,
                initiator_id=current_user.user_id,
                status='pending',
                reference_id="" # Will be updated later
            )

            db.session.add(new_signature_request)
            db.session.commit()

            # Save the signatories to DB and create signers list
            signers = []

            for name, email, position in zip(signatory_names, signatory_emails, signatory_positions):
                new_signatory = Signatory(
                    name=name,
                    email=email,
                    position=position,
                    signature_request_id=new_signature_request.request_id,
                    status='pending',
                    ds_signature_id="" # Will be updated later
                )

                db.session.add(new_signatory)

                # Append to signers list
                signer = {
                    'name': name,
                    'email': email
                }
                signers.append(signer)

            db.session.commit()

            #  Create embedded signature request on Dropbox Sign
            response = create_embedded_signature_request(
                title=title,
                description=description,
                signers=signers,
                filepath=os.path.join(upload_folder, unique_filename)
            )

            # Update the signature request reference ID in the DB
            new_signature_request.reference_id = response['signature_request']['signature_request_id']
            db.session.commit()

            # Update the signatories ds_signature_id
            signatures = response['signature_request']['signatures']

            for signer in signers:
                for signature in signatures:
                    if signature['signer_email_address'] == signer['email'] and signature['signer_name'] == signer['name']:
                        # Update ds_signature_id for matching signatory
                        db.session.query(Signatory)\
                            .filter(Signatory.email == signer['email'], Signatory.name == signer['name'])\
                            .update({"ds_signature_id": signature['signature_id']})

            db.session.commit()

            # Redirect home
            return redirect(url_for('signature_requests.index'))

# View the details of a signature request
@signature_requests.route('/signature-requests/<string:request_id>')
@login_required
def view(request_id):
     # Retrieve the signature request from the database
    signature_request = SignatureRequest.query.filter_by(request_id=request_id).first()

    # If signature request does not exist
    if not signature_request:
        abort(404)

    # Check if the current user is authorized to view this request
    if (signature_request.initiator_id != current_user.user_id and
            not any(signatory.email == current_user.email for signatory in signature_request.signatories)):
        abort(403)

    # If the current user is a signatory, generate a signing URL
    sign_url = None
    for signatory in signature_request.signatories:
        if signatory.email == current_user.email:
            response = generate_sign_url(signatory.ds_signature_id)
            sign_url = response['embedded']['sign_url']
            break

    return render_template('signatureRequests/details.html', signature_request=signature_request, sign_url=sign_url)

# Serve uploaded files
@signature_requests.route('/uploads/<filename>')
def uploaded_file(filename):
    # Get the base directory of the application
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Combine the base directory with the relative upload folder
    upload_folder = os.path.join(basedir, current_app.config['UPLOAD_FOLDER'])

    # Construct the full file path
    filepath = os.path.join(upload_folder, filename)

    # Check if the file exists
    if not os.path.isfile(filepath):
        abort(404, description="File not found")

    # Send the file
    return send_from_directory(directory=upload_folder, path=filename)