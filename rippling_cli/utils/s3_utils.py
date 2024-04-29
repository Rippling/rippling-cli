from http import client
from typing import Optional

from rippling_cli.core.s3 import S3UploadFileCredentials
from rippling_cli.utils.login_utils import get_api_client_with_role_company


def get_s3_upload_url_credentials(content_type, module, oauth_token) -> Optional[S3UploadFileCredentials]:
    """
    Get S3 upload URL credentials for the given content type and module
    :param content_type:
    :param module:
    :param oauth_token:
    :return: S3UploadFileCredentials
    """
    api_client = get_api_client_with_role_company(oauth_token)
    endpoint = f"/hub/api/get_upload_url?contentType={content_type}&module={module}&preview_url=true"
    response = api_client.get(endpoint)
    if response.status_code != client.OK:
        return None
    data = response.json().get("data")
    return S3UploadFileCredentials(url=data.get("url", ""),
                                   key=data.get("fields", {}).get("key", ""),
                                   policy=data.get("fields", {}).get("policy", ""),
                                   x_amz_algorithm=data.get("fields", {}).get("x-amz-algorithm", ""),
                                   x_amz_credential=data.get("fields", {}).get("x-amz-credential", ""),
                                   x_amz_date=data.get("fields", {}).get("x-amz-date", ""),
                                   x_amz_security_token=data.get("fields", {}).get("x-amz-security-token", ""),
                                   x_amz_signature=data.get("fields", {}).get("x-amz-signature", ""),
                                   s3_build_url=data.get("finalUrl", {}).get("url", ""))
