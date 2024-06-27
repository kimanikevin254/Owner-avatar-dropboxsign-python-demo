import os
from dropbox_sign import ApiClient, ApiException, Configuration, apis, models

configuration = Configuration( username = os.getenv('DS_API_KEY') )

# Create an Embedded Signature Request
def create_embedded_signature_request(title, description, signers, filepath):
    with ApiClient(configuration=configuration) as api_client:
        signature_request_api = apis.SignatureRequestApi(api_client=api_client)

        signing_options = models.SubSigningOptions(
            draw=True,
            type=True,
            upload=True,
            phone=True,
            default_type="draw",
        )

        # Create signers_list using list comprehension
        signers_list = [
            models.SubSignatureRequestSigner(
                email_address=signer.get('email'), 
                name=signer.get('name'), 
                order=index
            )
            for index, signer in enumerate(signers)
        ]

        data = models.SignatureRequestCreateEmbeddedRequest(
            client_id = os.getenv('DS_CLIENT_ID'),
            title = title,
            subject = title,
            message = description,
            signers = signers_list,
            cc_email_addresses = ["lawyer@example.com"],
            files = [open(file=filepath, mode="rb")],
            signing_options = signing_options,
            test_mode=True
        )

        try:
            return signature_request_api.signature_request_create_embedded(data)
        except ApiException as e:
            print("Exception when calling Dropbox Sign API: %s\n" % e)

# Generate a sign_url
def generate_sign_url(signature_id):
    with ApiClient(configuration=configuration) as api_client:
        embedded_api = apis.EmbeddedApi(api_client=api_client)

        try:
            return embedded_api.embedded_sign_url(signature_id=signature_id)
        except ApiException as e:
            print("Exception when calling Dropbox Sign API: %s\n" % e)
