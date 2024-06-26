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
    return render_template('signatureRequests/index.html')

# Create a signature request
@signature_requests.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('signatureRequests/create.html')
    
    if request.method == 'POST':
        pass

# View the details of a signature request
@signature_requests.route('/signature-requests/<string:request_id>')
@login_required
def view(request_id):
    pass

# Serve uploaded files
@signature_requests.route('/uploads/<filename>')
def uploaded_file(filename):
    pass