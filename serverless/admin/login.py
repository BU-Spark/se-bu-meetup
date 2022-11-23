import json
import time

def process_body(body):
    print(body)
    if (body['username'] == "bumeetup" and body['password'] == "bumeetupadminpassword"):
        return True
    return False

def lambda_handler(event, context):
    print(event)
    body = json.loads(event['body'])
    
    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
    }
    
    if process_body(body):
        print("PASSED AUTH")
        # set cookie
        response['headers'] = {
            'Set-Cookie': "Session=bumeetup,bumeetupadminpassword," + str(time.time())
        }
        return response
    else:
        print("FAILED AUTH")
        # clear cookie
        response['statusCode'] = 401
        response['headers'] = {
            'Set-Cookie': ""
        }
        return response