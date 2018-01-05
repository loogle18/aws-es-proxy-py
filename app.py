import boto3
import requests
import config
import json
from flask import Flask, Response, request
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

app = Flask(__name__)

PROXY_REQ_HEADERS_WHITELIST = ["content-type"]
PROXY_RESP_HEADERS_BLACKLIST = ["connection", "content-length",
                                "content-encoding", "transfer-encoding"]


@app.route('/<path:path>', methods=["GET", "POST", "PUT"])
def elastic(path):
    proxy_request_headers = {}
    requests_response = None
    response = app.make_response("")

    aws_request = AWSRequest(method=request.method, url=request.path,
                             data=request.get_data())
    auth = SigV4Auth(config.aws_credentials, config.aws_service,
                     config.aws_region).add_auth(aws_request)

    endpoint = config.aws_endpoint + request.path + "?" +\
        request.query_string.decode("utf-8")

    for header, value in request.headers.items():
        if header.lower() in PROXY_REQ_HEADERS_WHITELIST:
            proxy_request_headers[header] = value

    if request.method == "HEAD":
        requests_response = requests.head(endpoint, auth=auth,
                                          cookies=request.cookies,
                                          headers=proxy_request_headers)
    elif request.method == "GET":
        requests_response = requests.get(endpoint, auth=auth,
                                         cookies=request.cookies,
                                         headers=proxy_request_headers)
    elif request.method == "POST":
        data = request.get_data()
        requests_response = requests.post(
            endpoint,
            cookies=request.cookies,
            auth=auth,
            data=data,
            headers=proxy_request_headers)
    elif request.method == "PUT":
        data = request.get_data()
        requests_response = requests.put(
            endpoint,
            cookies=request.cookies,
            auth=auth,
            data=data,
            headers=proxy_request_headers)
    else:
        return "Method is not allowed!"

    if request.method != "HEAD":
        response.set_data(requests_response.content)
    response.status_code = requests_response.status_code

    for header, value in requests_response.headers.items():
        if header.lower() not in PROXY_RESP_HEADERS_BLACKLIST:
            response.headers[header] = value

    if response.status_code == 200:
        return response
    else:
        return ""


def start():
    app.run(debug=True)
