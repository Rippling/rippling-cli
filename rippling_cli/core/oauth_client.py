from rippling_cli.config.config import get_oauth_credentials


class OAuthClient:
    @classmethod
    def get_client_credentials(cls):
        return get_oauth_credentials()
