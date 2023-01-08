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

load_dotenv()
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
slack_app = App(token=SLACK_BOT_TOKEN, name="Automation Bot")


@slack_app.message(re.compile(r"^create channel[\s+](.+?)$"))  # type: ignore
def create_channel(message, client):
    """
    Creates workspace channel with given information.

    :param message: Request with all information about channel, to be created.
    :param client: Slack connection instance.
    """
    logger = logging.getLogger("channel creation")
    channel_creation(message, client, logger)


@slack_app.message(re.compile(r"^invite to[\s+](.+?)$"))  # type: ignore
def invite_to_channel(message, client):
    """
    Invites specified user to specified channel.

    :param message: Request with all information about user and channel, to be invited in.
    :param client: Slack connection instance.
    """
    logger = logging.getLogger("channel invitation")
    channel_invitation_by_user_tags(message, client, logger)


@slack_app.message(re.compile("^start$"))  # type: ignore
def onboarding(message, client):
    """
    Sends a welcome message to the new user, which contains all the necessary instructions.

    :param message: Request with all information about user and the instructions, to be sent.
    :param client: Slack connection instance.
    """
    logger = logging.getLogger("onboarding help")
    send_onboarding(message, client, logger)


@slack_app.message(re.compile(r"^help\s*(.*)$", flags=re.IGNORECASE))  # type: ignore
def display_help(message, client):
    """
    Displays instructions on the general use of the bot, listing its main features and limitations.

    :param message: Request with all information about user and the instructions, to be sent.
    :param client: Slack connection instance.
    """
    logger = logging.getLogger("general help")
    display_helps(message, client, logger)


@slack_app.message(re.compile(r"^(.*)join.slack.com/t/(.*)$"))  # type: ignore
def workspace_invitation(message, client):
    """
    Sends an invitation to the user using email.

    :param message: Request with all information about user email and the invitation, to be sent.
    :param client: Slack connection instance.
    """
    logger = logging.getLogger("workspace invitation")
    invite_to_workspace(message, client, logger)


@slack_app.event("channel_created")
def channel_created_events_handler(body):
    """
    Tracks the channel creation event and records it in the logs.

    :param body: JSON with all the basic information about the event.
    """
    logger = logging.getLogger("channel created event")
    logger.info(body)


@slack_app.event("message")
def message_events_handler(body):
    """
    Tracks the message sending event and records it in the logs.

    :param body: JSON with all the basic information about the event.
    """
    logger = logging.getLogger("message received event")
    logger.info(body)


@slack_app.event("file_shared")
def handle_file_shared_events(body):
    """
    Tracks the file sharing event and records it in the logs.

    :param body: JSON with all the basic information about the event.
    """
    logger = logging.getLogger("file shared event")
    logger.info(body)


@slack_app.event("team_joined")
def handle_user_joined_workspace_event(event, client):
    """
    Tracks the workspace user joining event and records it in the logs.

    :param event: JSON with all the basic information about the event.
    :param client: Slack connection instance.
    """
    logger = logging.getLogger("user joined workspace event")
    user_joined_workspace_event_handler(event, client, logger)
    logger.info(event)


@slack_app.event("member_joined_channel")
def handle_user_joined_channel_event(event, _):
    """
    Tracks the channel user joining event and records it in the logs.

    :param event: JSON with all the basic information about the event.
    :param client:Slack connection instance.
    """
    logger = logging.getLogger("user joined channel event")
    logger.info(event)


def main():
    """
    Entry point into the program. Initializes the connection to the workspace by the specified environment variables.
    """
    handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
    handler.start()
