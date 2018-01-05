import boto3
import requests
import config
import json
from flask import Flask, Response, request
from requests_aws4auth import AWS4Auth

app = Flask(__name__)

PROXY_REQ_HEADERS_WHITELIST = ["content-type"]
PROXY_RESP_HEADERS_BLACKLIST = ["connection", "content-length",
                                "content-encoding"]


@app.route("/", defaults={'path': ''}, methods=["GET", "POST", "PUT"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT"])
def elastic(path):
    proxy_request_headers = {}
    requests_response = None
    response = Response()
    auth = AWS4Auth(config.aws_access_key,
                    config.aws_secret_key, config.aws_region,
                    config.aws_service)
    endpoint = config.aws_endpoint + request.path + "?" +\
        request.query_string.decode("utf-8")

    for header in request.headers:
        if header[0].lower() in PROXY_REQ_HEADERS_WHITELIST:
            proxy_request_headers[header] = request.headers[header]

    if request.method == "GET":
        requests_response = requests.get(endpoint, auth=auth,
                                         headers=proxy_request_headers)
    elif request.method == "POST":
        data = json.dumps(request.get_data().decode("utf-8"))
        requests_response = requests.post(
            endpoint,
            auth=auth,
            data=data,
            headers=proxy_request_headers)
    elif request.method == "PUT":
        data = json.dumps(request.get_data().decode("utf-8"))
        requests_response = requests.put(
            endpoint,
            auth=auth,
            data=data,
            headers=proxy_request_headers)
    else:
        return "Method is not allowed!"

    response.set_data(requests_response.content)

    for header in requests_response.headers:
        if header.lower() not in PROXY_RESP_HEADERS_BLACKLIST:
            response.headers[header] = requests_response.headers[header]

    return response


def start():
    app.run(debug=True)
