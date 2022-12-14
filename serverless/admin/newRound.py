import json
import boto3

client = boto3.resource("dynamodb")
memberTable = client.Table("Member")
roundsTable = client.Table("Rounds")
clientLambda = boto3.client("lambda")


def write_to_rounds(next):
    # { round_number: number; groups: {}}
    print("write_to_rounds")
    roundsTable.put_item(Item={"round_number": next, "groups": {}})


def write_to_member(next):
    # for each member {  }
    print("write_to_member")
    members = memberTable.scan()
    items = members["Items"]
    for m in items:
        round = m["round"]

        round[next] = {"opted_in": False, "group": -1}

        memberTable.update_item(
            Key={"id": m["id"]},
            UpdateExpression="SET round = :val",
            ExpressionAttributeValues={":val": round},
        )


def update_prior_matches(key):
    optedMembers = memberTable.scan(
        FilterExpression="round.#key.#opted = :optedIn",
        ExpressionAttributeNames={"#key": key, "#opted": "opted_in"},
        ExpressionAttributeValues={":optedIn": True},
    )
    memberItems = optedMembers["Items"]
    table = roundsTable.get_item(
        Key={"round_number": key},
    )
    tableGroups = table["Item"]["groups"]
    for member in memberItems:
        lastGroupNum = member["round"][key]["group"]
        if lastGroupNum != -1:
            lastGroup = list(tableGroups[str(lastGroupNum)])
            lastGroup.remove(member["id"])
            member["prior_matches"].extend(lastGroup)
            prior_matches = list(set(member["prior_matches"]))
            memberTable.update_item(
                Key={"id": member["id"]},
                UpdateExpression="SET prior_matches = :mtch",
                ExpressionAttributeValues={":mtch": prior_matches},
                ConditionExpression="attribute_exists(id)",
            )


def lambda_handler(event, context):
    # 1. get next round number
    # read all keys in the Rounds table. and sort
    rounds = roundsTable.scan()
    items = rounds["Items"]

    lastKey = 0
    if items:

        def get_round_numb(round):
            return int(round.get("round_number"))

        items.sort(key=get_round_numb, reverse=True)
        lastKey = int(items[0]["round_number"])
    # if empty then we know it???s round 1 else lastkey + 1
    next = str(lastKey + 1)
    print(next)

    try:

        # before we create a new round, we want to move all the current_match to prior_matches, if next > 1 then we know there is a previous round which might have matches
        if lastKey + 1 > 1:
            update_prior_matches(str(lastKey))

        # 2.  add a empty object in table rounds
        write_to_rounds(next)
        # 3. read all member and add round
        write_to_member(next)
    except Exception:
        return json.dumps(
            {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"statusCode": 500, "message": f" wrong on server: {Exception}"}
                ),
            }
        )

    response = clientLambda.invoke(
        FunctionName="arn:aws:lambda:us-east-1:947610578306:function:member-lambda-dev-sendOptIn",
        InvocationType="RequestResponse",
        LogType="Tail",
    )

    print("notify status: " + str(response["StatusCode"]))
    if response["StatusCode"] != 200:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"statusCode": 500, "message": f" notify fail: {Exception}"}
            ),
        }

    # succeed return
    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "statusCode": 200,
                "message": "success",
                "data": {"round": next, "status": False},
            }
        ),
    }
    return response
