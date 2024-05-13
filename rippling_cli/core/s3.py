from dataclasses import dataclass


@dataclass
class S3UploadFileCredentials:
    url: str
    key: str
    s3_build_url: str
    policy: str
    x_amz_algorithm: str
    x_amz_credential: str
    x_amz_date: str
    x_amz_security_token: str
    x_amz_signature: str
