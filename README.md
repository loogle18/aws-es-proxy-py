# aws-es-proxy-py

**aws-es-proxy-py** is a small web server application which allows you to get access to your Amazon ES instance using your AWS IAM user credentials. It will sign your requests using latest AWS Signature Version 4 before sending the request to Amazon instance and return response. Kibana's requests are supported as well.

It supports following HTTP methods: **HEAD, GET, POST, PUT, DELETE**. So you can fully manipulate your Elasticseach and Kibana services.

## Install common requirements

`pip install -r requirements.txt`

## Configuring Credentials

Before using **aws-es-proxy-py**, ensure that you've configured your AWS IAM user credentials.
You can use [aws cli](https://aws.amazon.com/cli/) to configure file with credentials or create it manually. Check `~/.aws/credentials` file before running app. It might look like:

```
[default]
aws_access_key_id = ${MY_ACCESS_KEY}
aws_secret_access_key = ${MY_SECRET_KEY}
```

Alternatively, just set following environment variables:

```
export AWS_ACCESS_KEY_ID=${MY_ACCESS_KEY}
export AWS_SECRET_ACCESS_KEY=${MY_SECRET_KEY}
```

## Run

`python3 aws_es_proxy_py --region ${AWS_SERVICE_REGION} --endpoint ${AWS_ES_ENDPOINT}`

You can specify local host and port to listen on. Example:

`python3 aws_es_proxy_py -r us-west-2 -e https://sample.us-west-2.es.amazonaws.com -lh 0.0.0.0 -p 9200`

Run `python3 aws_es_proxy_py -h` to see details

## Usage example:

```sh
python3 aws_es_proxy_py -r eu-west-1 -e https://test-es-somerandomvalue.eu-west-1.es.amazonaws.com
INFO:root:Proxy started
INFO:botocore.credentials:Found credentials in shared credentials file: ~/.aws/credentials
INFO:root:Successfully loaded AWS credentials from shared-credentials-file
INFO:werkzeug: * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
