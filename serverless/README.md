# Serverless

## Description

Folder that contains code for AWS resources.
Deployed using [serverless framework](https://www.serverless.com/framework/docs).
Each subfolder pertains to a different CloudFormation stack and resource.

## Set up

1. Install [Serverless CLI](https://www.serverless.com/framework/docs/getting-started)
2. Set up AWS credentials in `~/.aws/credentials`
3. Now we should be good to run Serverless commands

## How to Deploy

1. Set up `serverless.yml`
2. Run `serverless deploy` in the subfolder that you want to deploy
3. Wait for Serverless to finish deploying stack to CloudFormation

## How to Uninstall a Stack

1. Run `serverless remove` in the subfolder that you want to uninstall

## Descriptions

There is a architecture graph in documents/ in the root directory which will be helpful for you to understand these Lambda functions.

### dynamodb/

Set up the Member and Rounds table. Must be deployed before the other lambda functions since they make changes to the database.

- serverless.yml

### admin/

All the files in this folder are for setting up all the lambda functions and connecting the lambda functions to the admin-gateway. So please make sure that the files in admin-gateway/ have been deployed before deploying the files in this folder.

- auth.py: return auth policy.
- index.py: return home page for administrator operations.
- login.py: authenticate users and set Cookie.
- match.py: maintain match/. Used to match students and notify everyone after matched. It will change data in databases.
- newRound.py: maintain new-round/. Used to start a new round and notify everyone. It will change data in databases.
- status.py: maintain status/. Used by index page to get current round and matched status.
- serverless.yml

### admin-gateway/

Apply for AWS Gateway resources for the admin part.

- serverless.yml

### member/

All the files in this folder are for setting up all the lambda functions and connecting the lambda functions to the member-gateway. So please make sure that the files in member-gateway/ have been deployed before deploying the files in this folder.

- optin.py: update member opted_in status.
- register.py: inserts a new member into Member table.
- sendEmail.py: notifies members about who're they matched with.
- sendOptIn.py: send an email with a url brings user to a new web page that allows user to update their opted_in status.
- submit.py: return web page for user to update their opted_in status.
- env.json: stores environment variables to be used in the lambda functions.
- serverless.yml

### admin-gateway/

Apply for AWS Gateway resources for the member part.

- serverless.yml

## Known Issues

The matching algorithm is migrated over from the clients code, so there is a known issue with the matching algorithm for small samples.

- When there is a small number of people who opted in (~3 or less), the matching algorithm might fail.
- When there is a small number of people who opted in (but some having the same departments/schools), the matching algorithm might fail.
- When there is a small number of people who opted in and they were previously matched before, the matching algorithm might fail.

The reason being that the matching algorithm tries to match in groups of 3/4, tries to match people of different majors, and tries to match people who have not been matched before.
