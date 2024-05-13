import http.server
import socketserver
import threading
from datetime import datetime
from http import HTTPStatus
from urllib.parse import parse_qs

import click
import requests  # type: ignore

from rippling_cli.config.config import get_oauth_token_data
from rippling_cli.constants import RIPPLING_API, RIPPLING_BASE_URL


class OAuthToken:
    class OAuthTokenRequestHandler(http.server.BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.token = kwargs.pop('token')
            super().__init__(*args, **kwargs)

        def log_message(self, format, *args):
            pass  # Suppress access log messages

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Authorization successful. You can close this window.")
            parsed_path = self.parse_path()
            self.token.authorization_code = parse_qs(parsed_path.query).get("code")
            self.token.authorization_code_received.set()
            self.token.stop_server()

        def parse_path(self):
            import urllib.parse
            return urllib.parse.urlparse(self.path)

    def __init__(self, client_id=None, code_challenge=None, code_challenge_method=None):
        self.client_id = client_id
        self.code_challenge = code_challenge
        self.code_challenge_method = code_challenge_method
        self.authorization_code = None
        self.server_thread = None
        self.authorization_code_received = threading.Event()
        self.authorization_code_timeout = 300  # seconds
        self.expires_in = 3600
        self.httpd = None

    def start_authorization_flow(self):
        if not self.client_id or not self.code_challenge or not self.code_challenge_method:
            raise ValueError("Missing required parameters")

        url = f"{RIPPLING_BASE_URL}/oauth?clientId={self.client_id}" \
              f"&codeChallenge={self.code_challenge}&codeChallengeMethod={self.code_challenge_method}"
        click.launch(url)

        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

        if self.authorization_code_received.wait(self.authorization_code_timeout):
            return self.authorization_code
        else:
            raise TimeoutError("Authorization code not received within the timeout period.")

    def run_server(self):
        with socketserver.TCPServer(("localhost", 2000),
                                    lambda *args, **kwargs: self.OAuthTokenRequestHandler(*args, **kwargs,
                                                                                          token=self)) as httpd:
            self.httpd = httpd
            self.httpd.serve_forever()

    def stop_server(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.server_thread.join()

    def exchange_for_token(self, code_verifier):
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": self.authorization_code,
            "code_verifier": code_verifier,
            "Content-Type": "application/json"
        }
        response = requests.post(f"{RIPPLING_API}/o/token/", data=data, allow_redirects=False)
        if response.status_code != HTTPStatus.OK:
            raise Exception(f"Failed to exchange authorization code for token: {response.text}")
        self.expires_in = response.json()["expires_in"]
        return response.json()["access_token"]

    @staticmethod
    def is_token_expired():
        # Read token data from the oauth_token.json file
        token_data = get_oauth_token_data()

        # Extract expiration timestamp from token data
        expiration_timestamp = token_data and token_data.get('expiration_timestamp')

        if not expiration_timestamp:
            return True
        # Compare with the current time
        current_timestamp = datetime.now().timestamp()
        return current_timestamp > expiration_timestamp
