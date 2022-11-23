import json
import base64
import time

def process_cookie(cookie):
    try:
        if cookie.startswith("Session="):
            cookie = cookie[8:]
        list = cookie.split(",")
        username = list[0]
        password = list[1]
        timestamp = list[2]
        print("username: " + username)
        print("password: " + password)
        print("timestamp: " + timestamp)
        if (isExpire(timestamp)):
            return False
        # not expire
        if (username == "bumeetup" and password == "bumeetupadminpassword"):
            return True
        return False
    except:
        return False

def isExpire(start):
    end = time.time()
    duration = end - float(start)
    return duration > 86400

def create_policy():
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

def lambda_handler(event, context):
    print(event)
    headers = event['headers']
    if process_cookie(headers['Cookie']):
        print("PASSED AUTH")
        return create_policy()
    else:
        print("FAILED AUTH")
        # clear cookie
        response = {}
        response['statusCode'] = 401
        response['headers'] = {
            'Set-Cookie': ""
        }
        return response 
