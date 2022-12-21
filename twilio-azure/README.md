# BU Meetup Text Notification Channel

## Description

Folder that contains code for Azure resources.
Deployed using [Visual Studio Code Azure Extension to Azure Function App](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack).
Each subfolder pertains to a different Azure HTTP Trigger function.

## Set up and Deployment

1. Clone the repository and deploy the `twilio-azure` folder to a function app in Azure.
2. Set up Twilio credentials with ACCOUNT_SID and AUTH_TOKEN in `./twilio-azure/matchingNotification/__init__.py`, `./twilio-azure/newRoundText/__init__.py`, and `./twilio-azure/signUpTrigger/__init__.py`
3. Add the webhooks to the Twilio active number.
4. Verify your numbers on Twilio portal.
4. Test using the specific HTTP Trigger endpoints.

Demo Video:
https://user-images.githubusercontent.com/74674789/208802942-1fed5a9b-bc32-41ae-bd15-f076c6d43174.mp4

Azure Function App URL:
https://cs519azuremessager.azurewebsites.net

