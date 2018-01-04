import boto3
import requests
import config
from flask import Flask, request
from requests_aws4auth import AWS4Auth

app = Flask(__name__)

PROXY_REQ_HEADERS_WHITELIST = ["content-type"]


@app.route("/", defaults={'path': ''}, methods=["GET", "POST", "PUT"])
@app.route('/<path:path>')
def elastic(path):
    auth = AWS4Auth(config.aws_access_key,
                    config.aws_secret_key, config.aws_region,
                    config.aws_service)
    endpoint = config.aws_endpoint + request.path + "?" +\
        request.query_string.decode("utf-8")
    print(request.query_string.decode("utf-8"))
    proxy_header = {}
    for header in request.headers:
        if header[0].lower() in PROXY_REQ_HEADERS_WHITELIST:
            proxy_header[header] = request.headers[header]

    if request.method == "GET":
        requests_response = requests.get(endpoint, auth=auth,
                                         headers=proxy_header)
    return requests_response.content


def start():
    app.run(debug=True)
