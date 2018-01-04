import boto3
import requests
import config
from flask import Flask, Response, request
from requests_aws4auth import AWS4Auth

app = Flask(__name__)

PROXY_REQ_HEADERS_WHITELIST = ["content-type"]
PROXY_RESP_HEADERS_BLACKLIST = ["connection", "content-length",
                                "content-encoding"]


@app.route("/", defaults={'path': ''}, methods=["GET", "POST", "PUT"])
@app.route('/<path:path>')
def elastic(path):
    proxy_header = {}
    response = Response()
    auth = AWS4Auth(config.aws_access_key,
                    config.aws_secret_key, config.aws_region,
                    config.aws_service)
    endpoint = config.aws_endpoint + request.path + "?" +\
        request.query_string.decode("utf-8")

    for header in request.headers:
        if header[0].lower() in PROXY_REQ_HEADERS_WHITELIST:
            proxy_header[header] = request.headers[header]

    if request.method == "GET":
        requests_response = requests.get(endpoint, auth=auth,
                                         headers=proxy_header)

    response.set_data(requests_response.content)

    for header in requests_response.headers:
        if header.lower() not in PROXY_RESP_HEADERS_BLACKLIST:
            response.headers[header] = requests_response.headers[header]
    return response


def start():
    app.run(debug=True)
