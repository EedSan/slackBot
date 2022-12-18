import logging
import os
import re

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from event_handlers.channel_creation import channel_creation
from event_handlers.channel_invitation import channel_invitation
from event_handlers.display_help import disp_helps
from event_handlers.emoji_handlers import update_emoji
from event_handlers.onboarding_tutorial import send_onboarding

logger = logging.getLogger(__name__)

load_dotenv()
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
slack_app = App(token=SLACK_BOT_TOKEN, name="Automation Bot")


@slack_app.message(re.compile(r"^create channel[\s+](.+?)$"))  # type: ignore
def create_channel(message, client):
    channel_creation(message, client, logger)


@slack_app.message(re.compile(r"^invite to[\s+](.+?)$"))  # type: ignore
def invite_to_channel(message, client):
    channel_invitation(message, client, logger)


@slack_app.message(re.compile("^start$"))  # type: ignore
def onboarding(message, client):
    send_onboarding(message, client)


@slack_app.message(re.compile(r"^write msg to channel #[\s+](.+?)$"))  # type: ignore
def write_to_channel(message, client):
    print(message)
    if message["channel_type"] != "im":
        return
    user_id = message["user"]
    channel_name = re.search(r'channel #[\s+](.+?)$', message['text']).group(1)
    comm = f"write to channel {channel_name}"
    logger.info(f"Command: < {comm} > from user {user_id}")
    channel_id = None
    for result in client.conversations_list():
        if channel_id is not None:
            break
        for channel in result["channels"]:
            if channel["name"] == channel_name:
                channel_id = channel["id"]
                try:
                    # env_xoxp_token = ""
                    client.chat_postMessage(channel=channel_id,
                                            text=f"some text sample")
                    client.chat_postMessage(channel=user_id, text='post msg "hello channel" :white_check_mark:')
                except SlackApiError as e:
                    print(f"Error: {e}")
                break


@slack_app.message(re.compile(r"^help\s*(.*)$", flags=re.IGNORECASE))  # type: ignore
def display_help(message, client):
    disp_helps(message, client)


@slack_app.event("reaction_added")
def if_reacted_update_emoji(event, client):
    update_emoji(event, client)


@slack_app.event("pin_added")
def if_pinned_update_pin(event, client):
    update_emoji(event, client)


@slack_app.event("channel_created")
def channel_created_events_handler(body):
    logger.info(body)


@slack_app.event("message")
def message_events_handler(body):
    logger.info(body)


def main():
    handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
    handler.start()
