from rippling_cli.config.config import get_client_id


class OAuthClient:
    @classmethod
    def get_client_credentials(cls):
        return get_client_id()
