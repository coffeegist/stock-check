import os
from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = os.environ['TWILIO_ACCOUNT']
# Your Auth Token from twilio.com/console
auth_token  = os.environ['TWILIO_AUTH']

class TwilioMessenger(object):
    def __init__(self):
        self._client = Client(account_sid, auth_token)

    def send_message(self, msg_to, msg_from, msg_body):
        return self._client.messages.create(
            to=msg_to,
            from_=msg_from,
            body=msg_body)
