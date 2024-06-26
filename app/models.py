from datetime import datetime
import uuid
from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    signature_requests = db.relationship('SignatureRequest', backref='user', lazy=True)

    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f'<User {self.name}>'
    
class SignatureRequest(db.Model):
    request_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    document_url = db.Column(db.String(500), nullable=False)
    initiator_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    reference_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    signatories = db.relationship('Signatory', backref='signature_request', lazy=True)

    def __repr__(self):
        return f'<SignatureRequest {self.title}>'

class Signatory(db.Model):
    signatory_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    ds_signature_id = db.Column(db.String(50), nullable=False)
    signature_request_id = db.Column(db.String(36), db.ForeignKey('signature_request.request_id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Signatory {self.name}>'