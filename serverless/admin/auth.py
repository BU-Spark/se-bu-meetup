import json
import base64
def process_password(headers):
    try:
        password_encoded = headers['Authorization']
        print(password_encoded)
        if password_encoded.startswith("Basic"):
            password_encoded = password_encoded[6:]
        password_decoded = base64.b64decode(password_encoded).decode()
        print(password_decoded)
        username, password = password_decoded.split(":")
        if (username == "bumeetup" and password == "bumeetupadminpassword"):
            return True
    except:
        return False
    return False

def create_policy():
    authResponse = { 
        "policyDocument": { 
            "Version": "2012-10-17", 
            "Statement": [{
                "Action": "execute-api:Invoke", 
                "Resource": ["arn:aws:execute-api:us-east-1:947610578306:cmhnb3jd1m/*/*/*"], 
                "Effect": "Allow"
            }]
        }
    }
    return authResponse

def lambda_handler(event, context):
    print(event)
    if process_password(event['headers']):
        print("PASSED AUTH")
        return create_policy()
    else:
        print("FAILED AUTH")
        result = {}
        result['status'] = 401
        return result
