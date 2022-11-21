import json
import boto3

client = boto3.resource('dynamodb')
memberTable = client.Table('Member')
roundsTable = client.Table('Rounds')

def get_current():
    rounds = roundsTable.scan()
    items = rounds['Items']
    lastKey = 0
    matched = False
    if items:
        def get_round_numb(round):
            return int(round.get('round_number'))
        items.sort(key=get_round_numb, reverse=True)
        lastKey = int(items[0]['round_number'])
        matched = len(items[0]['groups']) != 0
    return lastKey, matched

def lambda_handler(event, context):
    f = open("template/index.html", "r")
    html = f.read()
    current_round, matched_status = get_current()
    data = "Current Round: " + str(current_round) + " " + "Matched Status: " + str(matched_status)
    print(data)
    final = html.replace("$REPLACE", data)
    return {
        "statusCode": 200,
        "body": final.replace("\n", ""),
        "headers": {
            "Content-Type": "text/html"
        }
    }