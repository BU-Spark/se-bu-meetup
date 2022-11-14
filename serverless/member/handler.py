import boto3
import json

def main(event, context):
    try:
        print(f"Triggered event: {event}")
        resource = boto3.resource('dynamodb')
        membersTable = resource.Table('Member')
        body = json.loads(event["body"])
        print(f"Inserting into table: {body}")
        membersTable.put_item(Item={
            **body, 
            "id": body["timestamp"] + "|" + body["email"],
            "prior_matches": [],
            "round": {}
            }
        )
        response = {"statusCode": 200, "body": "Success!"}
    except Exception as e:
        response = {"statusCode": 400, "body": f"Something went wrong! Check it out: {e}" }
    return response


