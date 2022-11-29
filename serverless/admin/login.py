import json
import time
import hashlib

def process_body(body):
    print(body)
    if (body['username'] == "bumeetup" and body['password'] == "bumeetupadminpassword"):
        return True
    return False

def lambda_handler(event, context):
    print(event)
    body = json.loads(event['body'])
    
    if process_body(body):
        print("PASSED AUTH")
        # set cookie
        key = "bumeetup,bumeetupadminpassword"
        encoded = key.encode(encoding='UTF-8', errors='strict')
        md5 = hashlib.md5()
        md5.update(encoded)
        cookie = md5.hexdigest()
        response = {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                'Set-Cookie': "Session=" + cookie + "," + str(time.time())
            },
            "body": json.dumps({
                "statusCode": 200,
                "message": "success",
            })
        }
        return response
    else:
        print("FAILED AUTH")
        # clear cookie
        response = {
            "isBase64Encoded": False,
            "statusCode": 401,
            "headers": {
                "Content-Type": "application/json",
                'Set-Cookie': ""
            },
            "body": json.dumps({
                "statusCode": 401,
                "message": "auth fail",
            })
        }
        return response 
