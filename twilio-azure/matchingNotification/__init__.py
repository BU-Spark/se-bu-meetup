import logging
from twilio.rest import Client
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:

    match = req.params.get('match')

    client = Client('ACCOUNT_SID', 'AUTH_TOKEN')

    message = client.messages.create(
        body=match,
        from_='+18057494946',
        to='+16176500219'
    )

    return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
    )   
