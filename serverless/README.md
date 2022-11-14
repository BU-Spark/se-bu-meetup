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
