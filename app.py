import config
from urllib.parse import parse_qs, urlencode, quote
from requests import session as requests_session
from flask import Flask, Response, request
from aws_auth import AWSAuth

app = Flask(__name__)

PROXY_REQ_HEADERS_WHITELIST = ["content-type"]
PROXY_RESP_HEADERS_BLACKLIST = ["connection", "content-length",
                                "content-encoding", "transfer-encoding"]


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["HEAD", "GET", "POST", "PUT", "DELETE"])
def elastic(path):
    proxy_request_headers = {"kbn-xsrf": "reporting"}
    requests_response = None
    response = Response()
    session = requests_session()
    session.headers["Connection"] = "close"

    auth = AWSAuth(config.aws_credentials, config.aws_region)
    query_string = urlencode(
        parse_qs(request.query_string.decode("utf-8"), keep_blank_values=True),
        quote_via=quote, doseq=True
    )
    endpoint = config.aws_endpoint + "/" + path + "?" + query_string

    for header, value in request.headers.items():
        if header.lower() in PROXY_REQ_HEADERS_WHITELIST:
            proxy_request_headers[header] = value

    if request.method == "HEAD":
        session_response = session.head(endpoint, auth=auth,
                                        cookies=request.cookies,
                                        headers=proxy_request_headers)
    elif request.method == "GET":
        session_response = session.get(endpoint, auth=auth,
                                       cookies=request.cookies,
                                       headers=proxy_request_headers)
    elif request.method == "POST":
        session_response = session.post(endpoint, cookies=request.cookies,
                                        auth=auth, data=request.get_data(),
                                        headers=proxy_request_headers)
    elif request.method == "PUT":
        session_response = session.put(endpoint, cookies=request.cookies,
                                       auth=auth, data=request.get_data(),
                                       headers=proxy_request_headers)
    elif request.method == "DELETE":
        session_response = session.delete(endpoint, auth=auth,
                                          cookies=request.cookies,
                                          headers=proxy_request_headers)
    else:
        return "Method is not allowed!"

    if request.method != "HEAD":
        response.set_data(session_response.content)
    response.status_code = session_response.status_code

    for header, value in session_response.headers.items():
        if header.lower() not in PROXY_RESP_HEADERS_BLACKLIST:
            response.headers[header] = value

    return response


def start():
    app.run(host=config.app_host, port=config.app_port, debug=config.is_debug)
