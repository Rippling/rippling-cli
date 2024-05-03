import pkce


class PKCE:
    """
    PKCE class for generating PKCE code verifier and code challenge
    """
    @staticmethod
    def generate_pkce_pair(code_verifier_length=43):
        """
        Generate PKCE code verifier and code challenge pair
        :param code_verifier_length:
        :return:
        """
        code_verifier, code_challenge = pkce.generate_pkce_pair(code_verifier_length)
        return code_verifier, code_challenge
