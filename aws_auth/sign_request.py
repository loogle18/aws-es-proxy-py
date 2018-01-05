import sys, os, base64, datetime, hashlib, hmac 
import requests
from boto3 import session
from aws_auth import AwsAuth


method = "GET"
service = "es"
host = os.environ.get("AWS_ES_HOST")
region = "eu-west-1"
endpoint = "https://" + host
request_parameters = ""


# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(("AWS4" + key).encode("utf-8"), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, "aws4_request")
    return kSigning

access_key = session.Session().get_credentials().access_key
secret_key = session.Session().get_credentials().secret_key
if access_key is None or secret_key is None:
    print("No access key is available.")
    sys.exit()

timenow = datetime.datetime.utcnow()
amzdate = timenow.strftime("%Y%m%dT%H%M%SZ")
datestamp = timenow.strftime("%Y%m%d")


# http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
canonical_uri = "/" 
canonical_querystring = request_parameters
canonical_headers = "host:" + host + "\n" + "x-amz-date:" + amzdate + "\n"
signed_headers = "host;x-amz-date"
payload_hash = hashlib.sha256("".encode("utf-8")).hexdigest()
canonical_request = method + "\n" + canonical_uri + "\n" + canonical_querystring + "\n" + canonical_headers + "\n" + signed_headers + "\n" + payload_hash


algorithm = "AWS4-HMAC-SHA256"
credential_scope = datestamp + "/" + region + "/" + service + "/" + "aws4_request"
string_to_sign = algorithm + "\n" +  amzdate + "\n" +  credential_scope + "\n" +  hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()


signing_key = getSignatureKey(secret_key, datestamp, region, service)
signature = hmac.new(signing_key, (string_to_sign).encode("utf-8"), hashlib.sha256).hexdigest()


authorization_header = algorithm + " " + "Credential=" + access_key + "/" + credential_scope + ", " +  "SignedHeaders=" + signed_headers + ", " + "Signature=" + signature
headers = {"x-amz-date": amzdate}
auth = AwsAuth(authorization_header)

request_url = endpoint + "?" + canonical_querystring

print("\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++")
print("Request URL = " + request_url)
r = requests.get(request_url, auth=auth, headers=headers)

print("\nRESPONSE++++++++++++++++++++++++++++++++++++")
print("Response code: %d\n" % r.status_code)
print(r.text)