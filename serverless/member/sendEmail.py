import boto3
import json
import logging
import os
from email.message import EmailMessage
import ssl
import smtplib

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main(event, context):
    try:
        logger.info(f"Triggered event: {event}")
        resource = boto3.resource("dynamodb")
        membersTable = resource.Table("Member")
        roundsTable = resource.Table("Rounds")

        # Get latest round number
        rounds = roundsTable.scan()
        items = rounds["Items"]
        if not items:
            raise Exception("There are no rounds.")
        items.sort(key=get_round_numb, reverse=True)
        lastKey = items[0]["round_number"]
        groups = items[0]["groups"]

        if len(groups) == 0:
            raise Exception("There are no groups.")

        for members in groups.values():
            send_emails(members, lastKey, membersTable)

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


def get_round_numb(round):
    return int(round.get("round_number"))


def send_emails(members, round_num, membersTable):
    logger.info("Sending emails...")

    email_recipients = []
    names = []

    for member_id in members:
        response = membersTable.get_item(Key={"id": member_id})
        user = response["Item"]
        email_recipients.append(user["email"])
        names.append(user["first_name"])

    email_sender = os.environ["EMAIL_SENDER"]
    email_password = os.environ["EMAIL_PASSWORD"]

    greeting = ", ".join(names[:-1] + ["and " + names[-1]])

    subject = "BU Meetup Round %s" % round_num

    body = """Hello %s,

You all are a group for round %s of BU Meetup. Please figure out amongst yourselves what day, time, \
and place would work to meet up for at least 45 minutes sometime in the next 2 weeks. \
You might find it helpful to use a tool like When2Meet to share your availability: \
https://www.when2meet.com/.

Some suggestions: get coffee/tea, go for a walk on the esplanade, visit the BU Pub, or just sit on the BU Beach and chat. \
These meetups are meant to be whatever you make of it, so be kind to each other and enjoy yourselves! 

Feel free to reach out with any questions and we’ll do our best to answer them for you.

~BU Meetup (Eric Wellers & Will Saunders)""" % (
        greeting,
        round_num,
    )

    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_recipients
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    logger.info(f"email recipients: {email_recipients}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_recipients, em.as_string())

    logger.info("Emails sent...")
