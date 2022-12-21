import boto3
import json
import logging
import os
from email.message import EmailMessage
import ssl
import smtplib
import base64

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

        # go through each user, send optin information
        members = membersTable.scan()

        membersItems = members["Items"]

        users = []

        for member in membersItems:
            if member["round"].get(lastKey):
                users.append(member)

        send_emails(users, lastKey)

        response = {
            "statusCode": 200,
            "body": json.dumps({"statusCode": 200, "message": "Success!"}),
        }
    except Exception as e:
        logger.error(f"Exception: {e}")
        response = {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "statusCode": 500,
                    "message": f"Something went wrong! Check it out: {e}",
                }
            ),
        }
    return response


def get_round_numb(round):
    return int(round.get("round_number"))


def send_emails(members, round_num):
    logger.info("Sending emails...")

    email_sender = os.environ["EMAIL_SENDER"]
    email_password = os.environ["EMAIL_PASSWORD"]
    api_endpoint = os.environ["API_ENDPOINT"]

    subject = "BU Meetup Round %s Opt-in" % round_num
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        for member in members:
            member_id = member["id"]
            member_name = member["first_name"]
            member_email = member["email"]

            link = (
                api_endpoint
                + "dev/submit?id="
                + base64.b64encode(member_id.encode()).decode()
            )

            body = """Hello %s,
        <br>
        <br>
    Please update your opt-in preference for round %s using this link: <a href="%s">%s</a>
  <br>
  <br>
    Feel free to reach out with any questions and we’ll do our best to answer them for you.
<br>
<br>
    ~BU Meetup (Eric Wellers & Will Saunders)""" % (
                member_name,
                round_num,
                link,
                link,
            )

            em = EmailMessage()
            em["From"] = email_sender
            em["To"] = member_email
            em["Subject"] = subject
            em.set_content(body, subtype="html")

            logger.info(f"email recipient: {member_email}")
            smtp.sendmail(email_sender, member_email, em.as_string())

    logger.info("Emails sent...")
