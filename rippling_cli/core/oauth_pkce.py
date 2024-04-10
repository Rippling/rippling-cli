import pkce

from rippling_cli.constants import CODE_CHALLENGE_METHOD


class PKCE:
    @staticmethod
    def generate_code_verifier(length=43):
        code_verifier = pkce.generate_code_verifier(length=length)
        return code_verifier

    @staticmethod
    def get_code_challenge(code_verifier, method=CODE_CHALLENGE_METHOD):
        if method == CODE_CHALLENGE_METHOD:
            code_challenge = pkce.get_code_challenge(code_verifier)
            return code_challenge
        else:
            raise ValueError("Unsupported code challenge method")

    @staticmethod
    def generate_pkce_pair(code_verifier_length=43):
        code_verifier, code_challenge = pkce.generate_pkce_pair(code_verifier_length)
        return code_verifier, code_challenge
