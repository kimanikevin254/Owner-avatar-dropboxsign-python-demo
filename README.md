# Dropbox Embedded Signing Demo in Python

This demo shows how to embed document signing into your Python application using Dropbox Sign API.

It has 2 branches: `starter-template` and `main`. The `starter-template` branch contains the code to follow along with the article while the `main` branch contains the fully implemented application.

## Running the `starter-template` locally

1. Clone the repository:

    ```bash
    git clone --single-branch -b starter-template https://github.com/kimanikevin254/dropboxsign-python-demo.git
    ```

2. `cd` in the project folder:

    ```bash
    cd dropboxsign-python-demo
    ```

3. Create a virtual environment and activate it:

    ```bash
    python3 -m venv venv

    source venv/bin/activate
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Rename `.env.example` file to `.env`:

    ```bash
    mv .env.example .env
    ```

6. Set `FLASK_APP` and `FLASK_DEBUG` environment variables:

    ```bash
    export FLASK_APP=app
    export FLASK_DEBUG=1
    ```

7. Run the application:

    ```bash
    flask run
    ```
