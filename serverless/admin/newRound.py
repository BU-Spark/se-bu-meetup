import json
import boto3

client = boto3.resource('dynamodb')
memberTable = client.Table('Member')
roundsTable = client.Table('Rounds')

def write_to_rounds(next):
    # { round_number: number; groups: {}} 
    print('write_to_rounds')
    roundsTable.put_item(Item={
        'round_number': next,
        'groups': {}
    })
    
def write_to_member(next):
    # for each member {  }
    print('write_to_member')
    members = memberTable.scan() 
    items = members['Items'] 
    for m in items:
        round = m['round']
        # print(m)
        round[next] = {
            'opted_in': False, 
            'group': -1
        }
        # print(round)
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
        def get_round_numb(round):
            return int(round.get('round_number'))
        items.sort(key=get_round_numb, reverse=True)
        lastKey = items[0]['round_number']
    # if empty then we know it’s round 1 else lastkey + 1 
    next = str(lastKey + 1)
    print(next)

    try:
        # 2.  add a empty object in table rounds
        write_to_rounds(next)
        # 3. read all member and add round
        write_to_member(next)
    except Exception:
        return {
            "statusCode": 500, 
            "body": json.dumps({
                "statusCode": 500,
                "message": f" wrong on server: {Exception}"
            })
        }
        
    # succeed return 
    return {
        "statusCode": 200, 
        "body": json.dumps({
            "statusCode": 200,
            "message": "Success!"
        })
    }