import boto3
import json
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info("Matching...")
        resource = boto3.resource("dynamodb")
        membersTable = resource.Table("Member")
        roundsTable = resource.Table("Rounds")

        # Get latest round number
        rounds = roundsTable.scan()
        roundsItems = rounds["Items"]
        if not roundsItems:
            raise Exception("There are no rounds.")
        roundsItems.sort(key=get_round_numb, reverse=True)
        lastKey = roundsItems[0]["round_number"]

        # scan is expensive, but right now we don't have an index for querying (this needs to be changed in future)
        optedMembers = membersTable.scan(
            FilterExpression='round.#key.#opted = :optedIn',
            ExpressionAttributeNames={'#key': lastKey, "#opted": "opted_in"},
            ExpressionAttributeValues={':optedIn': True},
        )

        membersItems = optedMembers["Items"]
        logger.info(f"number items: {len(membersItems)}")

        # calculate the number of groups of 3 and 4 we will have 
        n = len(membersItems)
        number3groups = n // 3
        number4groups = n - (number3groups * 3)
        tmp = []

        for item in membersItems:
            tmp.append({
                "id": item["id"],
                "department": item["department"],
            })
        
        df = pd.DataFrame.from_records([d for d in tmp])
        df.set_index('id', inplace=True)
        
        data = []
        # round 1 pairing
        if lastKey == 1:
            for item in membersItems:
                possible_matches, num_possible_matches = get_possible_matches(df, item)
                data.append({
                    "id": item["id"],
                    "prior_matches": [],
                    "current_match": [],
                    "current_group": -1,
                    "num_prior_matches": 0,
                    "size_prev_match": 0,
                    "possible_matches": possible_matches, 
                    "num_possible_matches": num_possible_matches
                })
        # not round 1
        else:
            for item in membersItems:
                size_prev_match = get_size_prev_match(item, roundsItems[1], int(lastKey))
                possible_matches, num_possible_matches = get_possible_matches(df, item)
                data.append({              
                    "id": item["id"],
                    "prior_matches": item["prior_matches"],
                    "current_match": [],
                    "current_group": -1,
                    "num_prior_matches": len(item["prior_matches"]),
                    "size_prev_match": size_prev_match,
                    "possible_matches": possible_matches, 
                    "num_possible_matches": num_possible_matches
                })

        df1 = pd.DataFrame.from_records([d for d in data])
        df1.set_index('id', inplace=True)

        createMatch(df1, number4groups, membersTable, roundsTable, str(lastKey))
        clientLambda = boto3.client('lambda')
        # invoke notify lambda
        response = clientLambda.invoke(
            FunctionName='arn:aws:lambda:us-east-1:947610578306:function:member-lambda-dev-sendEmail',
            InvocationType='RequestResponse',
            LogType='Tail',
        )
        
        print('notify status: ' + str(response['StatusCode']))
        if (response['StatusCode'] != 200):
            return {
                "statusCode": 500, 
                "body": json.dumps({
                    "statusCode": 500,
                    "message": f" notify fail: {Exception}"
                })
            } 

        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "statusCode": 200, 
                "message": "Success!",
                "data": {
                    "round": lastKey,
                    "status": True 
                }
            }),
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

def get_possible_matches(df, member):
    # determines all the possible matches for each person in the program
    non_previous_matches = df.index.to_numpy()[~np.in1d(df.index.to_numpy(), member['prior_matches'])] 
    non_same_department = df.index.to_numpy()[~(member['department'] == df['department'])]
    intersect = np.intersect1d(non_previous_matches, non_same_department)
    len_intersect = -1 if len(intersect) == 0 else len(intersect)
    return intersect.tolist(), len_intersect

def createMatch(df, number4groups, membersTable, roundsTable, lastKey):
    # calls the matching loop up to 1000 times to create the match
    counter = 0
    out = 0

    try: 
        while out == 0:
            counter += 1
            out = perform_random_loop(df, number4groups)
            if counter >= 1000:
                raise Exception("match failed, not possible")
       
        pd.options.display.max_columns = None
        pd.options.display.max_rows = None
        df.reset_index(inplace=True)
        members = df.to_dict(orient='records')
        for member in members:
            # update table
            user_id = member['id']
            cur_group = member['current_group'] 
            cur_matches = member['current_match']
            membersTable.update_item(
                Key={'id': user_id},
                UpdateExpression='SET round.#key.#grp = :grpNum',
                ExpressionAttributeNames={'#key': lastKey, "#grp": "group"},
                ExpressionAttributeValues={':grpNum': cur_group},
                ConditionExpression='attribute_exists(id)'
            )
            roundsTable.update_item(                
                Key={'round_number': lastKey},
                UpdateExpression='SET groups.#grp = :matched',
                ExpressionAttributeNames={"#grp": str(cur_group)},
                ExpressionAttributeValues={':matched': cur_matches},
            )
    except Exception as e:
        raise Exception(e)

def perform_random_loop(df, number4groups):
    # the loop that attempts to do the matching
    out = 0 # variable to determine when we've succeeded
    # clear any attemps to match that failed
    df['current_match'] = [ [] for _ in range(len(df)) ]
    df['current_group'] = -1
    # create a random column 
    df.loc[:, 'randint'] = np.random.choice(np.arange(0, len(df)), size=len(df), replace=False)
    groupnum = 1 # a counter for the group number
    # iterate through, starting with the most number of possible matches 

    for i, (index, row) in enumerate(df.sort_values(['size_prev_match', 'num_possible_matches', 'randint']).iterrows()):
        # select possible matches for person1
        if i == 0:
            p1_possible = df.loc[index, 'possible_matches']
        elif i > 0 :
            if len(remaining) == 0:
                out = 1
                return out
            elif index not in remaining.index.tolist(): 
                continue
            else:
                p1_possible = np.intersect1d(remaining.loc[index, 'possible_matches'], \
                                             remaining.index.tolist())
        if len(p1_possible) <= 1:
            return out
        # pick a random person2
        p2 = df.loc[p1_possible].sample(1)
        p2_possible = p2['possible_matches'].tolist()
        # take person1 possible matches and remove person2 and all of person2's not possible matches
        p1p2_possible_step1 = np.array(p1_possible)[~np.isin(p1_possible, p2.index.tolist())] # remove p2
        p1p2_possible = p1p2_possible_step1[np.isin(p1p2_possible_step1, p2_possible)]

        if len(p1p2_possible) == 0:
            return out
        # pick a random person3
        p3 = df.loc[p1p2_possible].sample(1)
        p3_possible = p3['possible_matches'].tolist()

        if i < number4groups:
            # take person3 out oc p1p2_possible
            p1p2p3_possible_step1 = np.array(p1p2_possible)[~np.isin(p1p2_possible, p3.index.tolist())] 
            # keep only person3's possible matches 
            p1p2p3_possible = p1p2p3_possible_step1[np.isin(p1p2p3_possible_step1, p3_possible)]
            
            if len(p1p2p3_possible) == 0:
                return out
                break
            # pick a random person4
            p4 = df.loc[p1p2p3_possible].sample(1)

            # write the current match for all *4* group members
            df.loc[index, 'current_match'].extend([index, p2.index[0], p3.index[0], p4.index[0]])
            df.loc[p2.index[0], 'current_match'].extend([p2.index[0], index, p3.index[0], p4.index[0]])
            df.loc[p3.index[0], 'current_match'].extend([p3.index[0], index, p2.index[0], p4.index[0]])
            df.loc[p4.index[0], 'current_match'].extend([p4.index[0], index, p2.index[0], p3.index[0]])
            
            df.loc[index, 'current_group'] = groupnum
            df.loc[p2.index[0], 'current_group'] = groupnum
            df.loc[p3.index[0], 'current_group'] = groupnum
            df.loc[p4.index[0], 'current_group'] = groupnum
            
        else:
            # write the current match for all *3* group members
            df.loc[index, 'current_match'].extend([index, p2.index[0], p3.index[0]])
            df.loc[p2.index[0], 'current_match'].extend([p2.index[0], index, p3.index[0]])
            df.loc[p3.index[0], 'current_match'].extend([p3.index[0], index, p2.index[0]])
            
            df.loc[index, 'current_group'] = groupnum
            df.loc[p2.index[0], 'current_group'] = groupnum
            df.loc[p3.index[0], 'current_group'] = groupnum
        # create a new version of the overall df with the matches rows removed
        if i == 0:
            if i < number4groups:
                remaining = df.loc[df.index.difference((index, p2.index[0], p3.index[0], p4.index[0]))]
            else:
                remaining = df.loc[df.index.difference((index, p2.index[0], p3.index[0]))]
        if i > 0:
            if i < number4groups:
                remaining = remaining.loc[remaining.index.difference((index, p2.index[0], \
                                                                      p3.index[0], p4.index[0]))]
            else:
                remaining = remaining.loc[remaining.index.difference((index, p2.index[0], p3.index[0]))]

        if i == len(df) - 1:
            out = 1
            return out

        groupnum+=1


def get_size_prev_match(member, lastRound, lastKey):
    if member["round"].get(str(lastKey-1)):
        group_num = member["round"][str(lastKey-1)]["group"]
        if group_num != -1:
            return len(lastRound["groups"][str(group_num)])
    return 0

def get_round_numb(round):
    return int(round.get("round_number"))