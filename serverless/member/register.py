import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main(event, context):
    try:
        logger.info(f"Triggered event: {event}")
        resource = boto3.resource('dynamodb')
        membersTable = resource.Table('Member')
        body = json.loads(event["body"])
        item = {
            **body, 
            "id": body["timestamp"] + "|" + body["email"],
            "prior_matches": [],
            "round": {}
        }
        logger.info(f"Inserting into table: {item}")
        membersTable.put_item(Item=item)
        response = {"statusCode": 200, "body": json.dumps({
            "statusCode": 200,
            "message": "Success!"
        })}
    except Exception as e:
        logger.error(f"Exception: {e}")
        response = {"statusCode": 400, "body": json.dumps({
            "statusCode": 400,
            "message": f"Something went wrong! Check it out: {e}"
        }) }
    return response