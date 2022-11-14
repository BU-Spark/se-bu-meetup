import json
import boto3

client = boto3.resource('dynamodb')
memberTable = client.Table('Member')
roundsTable = client.Table('Rounds')

def write_to_rounds(next):
    # { round_number: number; groups: {}} 
    roundsTable.put_item(Item={
        'round_number': next,
        'groups': {}
    })
    
def write_to_member(next):
    # for each member {  }
    members = memberTable.scan() 
    items = members['Items'] 
    for m in items:
        round = m['round']
        round[next] = {
            'opted_in': False, 
            'group': -1
        }
        memberTable.update_item(
            Key={'id': m['id']},
            UpdateExpression='SET round = :val',
            ExpressionAttributeValues={':val': round}
        )
    

def lambda_handler(event, context):
    # 1. get next round number
    # read all keys in the Rounds table. and sort
    rounds = roundsTable.scan()
    items = rounds['Items']
    lastKey = 0
    if items:
        items.sort(key=items['round_number'], reverse=True)
        lastKey = items[0]['round_number']
    # if empty then we know it’s round 1 else lastkey + 1 
    next = lastKey + 1

    # 2.  add a empty object in table rounds
    try:
        write_to_rounds(next)
    except Exception:
        return {
            'statusCode': 500,
            'body': Exception
        }
    # 3. read all member and add round
    try:
        write_to_member(next)
    except Exception:
        return {
            'statusCode': 500,
            'body': Exception
        }
        
    # succeed return 
    return {
        'statusCode': 200
    } 
