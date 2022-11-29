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

        createMatch(df1, roundsItems)

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
  

def get_possible_matches(df, member):
    # determines all the possible matches for each person in the program
    non_previous_matches = df.id.to_numpy()[~np.in1d(df.id.to_numpy(), member['prior_matches'])] 
    non_same_department = df.id.to_numpy()[~(member['department'] == df['department'])]
    intersect = np.intersect1d(non_previous_matches, non_same_department)
    len_intersect = -1 if len(intersect) == 0 else len(intersect)
    return intersect.tolist(), len_intersect

def createMatch(df, rounds):
    # calls the matching loop up to 1000 times to create the match
    counter = 0
    out = 0

    # try: 
    #     while out == 0:
    #         counter += 1
    #         out = perform_random_loop(membersItems, roundsItems, lastKey)
    #         # use data to populate hr_data, full_data, and hr_full_data
    #         # hr_data['group' + str(round_widget.value)] = data['current_group']
    #         # hr_full_data = pd.merge(hr_full_data, hr_data, how='left')
    #         # full_data.loc[data.index, :] = data[:].copy()
    #         if counter >= 1000:
    #             raise Exception("match failed, not possible")
    # except Exception as e:
    #     raise Exception(e)

def perform_random_loop(members, rounds, round_num):
    # the loop that attempts to do the matching
    out = 0 # variable to determine when we've succeeded
    # clear any attempts to match that failed
    curRound = rounds[0]
    for member in members:
      member_group_num = member["round"][round_num]["group"]
      if member_group_num != -1:
        curRound["groups"][member_group_num] = []
        member_group_num= -1
    logger.info(f"members: {members}")
    # create a random column 
    # df.loc[:, 'randint'] = np.random.choice(np.arange(0, len(df)), size=len(df), replace=False)

    groupnum = 1 # a counter for the group number
    return 1

def get_size_prev_match(member, lastRound, lastKey):
    if member["round"].get(str(lastKey-1)):
        group_num = member["round"][str(lastKey-1)]["group"]
        if group_num != -1:
            return len(lastRound["groups"][str(group_num)])
    return 0



def get_round_numb(round):
    return int(round.get("round_number"))