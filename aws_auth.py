from requests.auth import AuthBase
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


class AWSAuth(AuthBase):
    def __init__(self, credentials, region):
        self.credentials = credentials
        self.region = region

    def __call__(self, request):
        aws_request = AWSRequest(method=request.method.upper(),
                                 url=request.url, data=request.body)
        SigV4Auth(self.credentials, "es", self.region).add_auth(aws_request)
        request.headers.update(dict(aws_request.headers.items()))
        return request
