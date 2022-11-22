import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main(event, context):
    try:
        logger.info(f"Triggered event: {event}")
        resource = boto3.resource("dynamodb")
        membersTable = resource.Table("Member")
        roundsTable = resource.Table("Rounds")

        # Get latest round number
        rounds = roundsTable.scan()
        items = rounds["Items"]
        if not items:
          raise Exception("There are no rounds.")
        items.sort(key=get_round_numb, reverse=True)
        lastKey = items[0]['round_number']

        body = json.loads(event["body"])
        user_id = body["id"]
        optedIn = body["opted_in"]

        if type(optedIn) != bool:
          raise Exception("opted_in must be a boolean")

        # find member with the id and then update their opted_in status
        membersTable.update_item(
            Key={'id': user_id},
            UpdateExpression='SET round.#key.#opted = :optedIn',
            ExpressionAttributeNames={'#key': lastKey, "#opted": "opted_in"},
            ExpressionAttributeValues={':optedIn': optedIn},
            ConditionExpression='attribute_exists(id)'
        )

        response = {
            "statusCode": 200,
            "body": json.dumps({"statusCode": 200, "message": "Success!"}),
        }
    except Exception as e:
        logger.error(f"Exception: {e}")
        response = {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "statusCode": 400,
                    "message": f"Something went wrong! Check it out: {e}",
                }
            ),
        }
    return response

def get_round_numb(round):
    return int(round.get('round_number'))