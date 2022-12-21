import json
import boto3

client = boto3.resource("dynamodb")
memberTable = client.Table("Member")
roundsTable = client.Table("Rounds")


def get_current():
    rounds = roundsTable.scan()
    items = rounds["Items"]
    lastKey = 0
    matched = False
    if items:

        def get_round_numb(round):
            return int(round.get("round_number"))

        items.sort(key=get_round_numb, reverse=True)
        lastKey = int(items[0]["round_number"])
        matched = len(items[0]["groups"]) != 0
    return lastKey, matched


def lambda_handler(event, context):
    try:
        current_round, matched_status = get_current()
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "statusCode": 200,
                    "message": "success",
                    "data": {"round": current_round, "status": matched_status},
                }
            ),
        }
    except Exception:
        return {
            "isBase64Encoded": False,
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"statusCode": 500, "message": f" wrong on server: {Exception}"}
            ),
        }
