import json
import base64
import time
import hashlib
md5 = hashlib.md5()

def process_cookie(cookie):
    try:
        if cookie.startswith("Session="):
            cookie = cookie[8:]
        list = cookie.split(",")
        hashed = list[0]
        timestamp = list[1]
        print("timestamp: " + timestamp)
        if (isExpire(timestamp)):
            return False
        # not expire
        str = "bumeetup,bumeetupadminpassword"
        md5.update(str)
        standard = md5.hexdigest()
        if (standard == hashed):
            return True
        return False
    except:
        return False

def isExpire(start):
    end = time.time()
    duration = end - float(start)
    return duration > 86400

def lambda_handler(event, context):
    print(event)
    headers = event['headers']
    if ('Cookie' in headers.keys()) and process_cookie(headers['Cookie']):
        print("PASSED AUTH")
        authResponse = { 
            "principalId": "admin",
            "policyDocument": { 
                "Version": "2012-10-17", 
                "Statement": [{
                    "Action": "execute-api:Invoke", 
                    "Resource": ["arn:aws:execute-api:us-east-1:947610578306:cmhnb3jd1m/*/*"], 
                    "Effect": "Allow"
                }]
            }
        }
        return authResponse
    else:
        print("FAILED AUTH")
        # clear cookie
        # response = {
        #     "isBase64Encoded": False,
        #     "statusCode": 401,
        #     "headers": {
        #         "Content-Type": "application/json",
        #         'Set-Cookie': ""
        #     },
        #     "body": json.dumps({
        #         "statusCode": 401,
        #         "message": "auth fail",
        #     })
        # }
        resp = { 
            "policyDocument": { 
                "Version": "2012-10-17", 
                "Statement": [{
                    "Action": "execute-api:Invoke", 
                    "Resource": ["arn:aws:execute-api:us-east-1:947610578306:cmhnb3jd1m/*/*"], 
                    "Effect": "Deny"
                }]
            }
        }
        # return response 
        return resp
