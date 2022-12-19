import logging
from twilio.rest import Client

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    link = req.params.get('link')
    round = req.params.get('round')

    client = Client('AC7f96f8dbf944b2f115d5a6097050d878', '510bb3ee7c8c3efd9ec33da4acec0e56')

    message = client.messages.create(
        body=f'Please update your opt-in preference for Round {round} using this link: {link}',
        from_='+18057494946',
        to='+16176500219'
    )

    return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )    