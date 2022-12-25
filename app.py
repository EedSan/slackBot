import logging
import os
import re

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from event_handlers.user_joined_workspace_handler import user_joined_workspace_event_handler
from message_handlers.channel_creation import channel_creation
from message_handlers.channel_invitation import channel_invitation_by_user_tags
from message_handlers.display_help import display_helps
from workspace_invitation.invite_to_workspace import invite_to_workspace
from message_handlers.onboarding import send_onboarding

logger = logging.getLogger(__name__)

load_dotenv()
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
# SLACK_APP_TOKEN = "xapp-1-A040XPVNLCX-4049127177031-80b77da6d0c368718db227f67094f7e161df6f3978a5edc38dfebe5e5c31f3a7"
# SLACK_BOT_TOKEN = "xoxb-4048814839236-4046337972595-8iqTuueX0IcxxmUC5WOg528C"
slack_app = App(token=SLACK_BOT_TOKEN, name="Automation Bot")


@slack_app.message(re.compile(r"^create channel[\s+](.+?)$"))  # type: ignore
def create_channel(message, client):
    channel_creation(message, client, logger)


@slack_app.message(re.compile(r"^invite to[\s+](.+?)$"))  # type: ignore
def invite_to_channel(message, client):
    channel_invitation_by_user_tags(message, client)


@slack_app.message(re.compile("^start$"))  # type: ignore
def onboarding(message, client):
    send_onboarding(message, client)


@slack_app.message(re.compile(r"^help\s*(.*)$", flags=re.IGNORECASE))  # type: ignore
def display_help(message, client):
    display_helps(message, client)


@slack_app.message(re.compile(r"^(.*)join.slack.com/t/(.*)$"))  # type: ignore
def workspace_invitation(message, client):
    invite_to_workspace(message, client)


# @slack_app.event("reaction_added")
# def if_reacted_update_emoji(event, client):
#     update_emoji(event, client)


@slack_app.event("channel_created")
def channel_created_events_handler(body):
    logger.info(body)


@slack_app.event("message")
def message_events_handler(body):
    logger.info(body)


@slack_app.event("file_shared")
def handle_file_shared_events(body):
    logger.info(body)


@slack_app.event("team_joined")
def handle_user_joined_workspace_event(event, client):
    user_joined_workspace_event_handler(event, client)
    logger.info(event)


@slack_app.event("member_joined_channel")
def handle_user_joined_channel_event(event, client):
    logger.info(event)


def main():
    handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
    handler.start()
