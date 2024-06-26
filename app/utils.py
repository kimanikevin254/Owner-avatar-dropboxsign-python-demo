from dropbox_sign import ApiClient, ApiException, Configuration, apis, models
import os

configuration = Configuration( username = os.getenv('DS_API_KEY') )

# Create an Embedded Signature Request
def create_embedded_signature_request(title, description, signers, filepath):
    pass

# Generate a sign_url
def generate_sign_url(signature_id):
    pass