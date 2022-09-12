import logging
import os
import re

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from onboarding_tutorial import OnboardingTutorial

load_dotenv()

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

app = App(token=SLACK_BOT_TOKEN, name="Joke Bot")
logger = logging.getLogger(__name__)

onboarding_tutorials_sent = {}


@app.message(re.compile("^create channel[\s+](.+?)$"))  # type: ignore
def create_channel(message, client):
    print(message)
    if message["channel_type"] != "im":
        return

    user_id = message["user"]

    joke = "Channel is created :clown_face:"
    logger.info(f"Sent joke < {joke} > to user {user_id}")
    channel_name = re.search('channel[\s+](.+?)$', message['text']).group(1)
    try:
        client.conversations_create(name=channel_name)
        client.chat_postMessage(channel=user_id, text='created :white_check_mark:')
    except SlackApiError as e:
        logger.error("Channel probably exists. Error creating channel: {}".format(e))
        client.chat_postMessage(channel=user_id,
                                text=f"Can't create channel {channel_name}. Check if it's exists already")
    else:
        channels_list = client.conversations_list()["channels"]
        print(channels_list)
        for item in channels_list:
            if item["name"] == channel_name:
                channel_id = item['id']
                client.conversations_invite(channel=channel_id, users=[user_id])
                client.chat_postMessage(channel=user_id, text='created & invited :white_check_mark:')
                break


@app.message(re.compile("^start$"))  # type: ignore
def onboarding_message(message, client):
    channel_type = message["channel_type"]
    if channel_type != "im":
        return

    user_id = message["user"]
    response = client.conversations_open(users=user_id)
    channel = response["channel"]["id"]
    start_onboarding(user_id, channel, client)


def start_onboarding(user_id: str, channel: str, client: WebClient):
    onboarding_tutorial = OnboardingTutorial(channel)
    msg = onboarding_tutorial.get_message_payload()
    response = client.chat_postMessage(**msg)
    onboarding_tutorial.timestamp = response["ts"]

    if channel not in onboarding_tutorials_sent:
        onboarding_tutorials_sent[channel] = {}
    onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial


# @app.event("reaction_added")
# def update_emoji(event, client):
#     channel_id = event.get("item", {}).get("channel")
#     user_id = event.get("user")
#
#     if channel_id not in onboarding_tutorials_sent:
#         return
#
#     onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]
#     onboarding_tutorial.reaction_task_completed = True
#     msg = onboarding_tutorial.get_message_payload()
#     client.chat_update(**msg)
#
#
# @app.event("pin_added")
# def update_pin(event, client):
#     channel_id = event.get("channel_id")
#     user_id = event.get("user")
#     onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]
#     onboarding_tutorial.pin_task_completed = True
#     msg = onboarding_tutorial.get_message_payload()
#     client.chat_update(**msg)


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


def main():
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    main()
