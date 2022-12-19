import logging
from twilio.rest import Client
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    client = Client('ACCOUNT_SID', 'AUTH_TOKEN')

    message = client.messages.create(
        body='Hello! Thank you for signing up for BU Meetup. You will receieve text notifications when a new round has opened up!',
        from_='+18057494946',
        to='+16176500219'
    )

    logging.info('Python HTTP trigger function processed a request.')

    return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )