import json


def lambda_handler(event, context):
    f = open("template/index.html", "r")
    html = f.read()
    return {
        "statusCode": 200,
        "body": html.replace("\n", ""),
        "headers": {"Content-Type": "text/html"},
    }
