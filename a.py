# import logging
# import os
# import re
#
# from dotenv import load_dotenv
# from slack_bolt import App
# from slack_bolt.adapter.socket_mode import SocketModeHandler
# from slack_sdk.web import WebClient
# from onboarding_tutorial import OnboardingTutorial
#
# load_dotenv()
#
# SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
# SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
#
# app = App(token=SLACK_BOT_TOKEN, name="Joke bot")
# logger = logging.getLogger(__name__)
#
# onboarding_tutorials_sent = {}
#
#
# @app.message(re.compile("^start$"))  # type: ignore
# def onboarding_message(msg, client):
#     channel_type = msg["channel_type"]
#     if channel_type != "im":
#         return
#
#     user_id = msg["user"]
#     response = client.conversations_open(users=user_id)
#     channel = response["channel"]["id"]
#     start_onboarding(user_id, channel, client)
#
#
# @app.message(re.compile("^create channels$"))  # type: ignore
# def create_channel(msg, say):
#     channel_type = msg["channel_type"]
#     if channel_type != "im":
#         return
#
#     dm_channel = msg["channel"]
#     user_id = msg["user"]
#
#     joke = "Channel is created :clown_face:"
#     logger.info(f"Sent joke < {joke} > to user {user_id}")
#
#     say(text=joke, channel=dm_channel)
#
#
# def start_onboarding(user_id: str, channel: str, client: WebClient):
#     onboarding_tutorial = OnboardingTutorial(channel)
#     msg = onboarding_tutorial.get_message_payload()
#     response = client.chat_postMessage(**msg)
#     onboarding_tutorial.timestamp = response["ts"]
#
#     if channel not in onboarding_tutorials_sent:
#         onboarding_tutorials_sent[channel] = {}
#     onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial
#
#
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
#     updated_message = client.chat_update(**msg)
#
#
# @app.event("pin_added")
# def update_pin(event, client):
#     channel_id = event.get("channel_id")
#     user_id = event.get("user")
#     onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]
#     onboarding_tutorial.pin_task_completed = True
#     msg = onboarding_tutorial.get_message_payload()
#     updated_message = client.chat_update(**msg)
#
#
# @app.event("message")
# def message(event, client):
#     channel_id = event.get("channel")
#     user_id = event.get("user")
#     text = event.get("text")
#
#     if text and text.lower() == "start":
#         return start_onboarding(user_id, channel_id, client)
#
#
# def main():
#     handler = SocketModeHandler(app, SLACK_APP_TOKEN)
#     handler.start()
#
#
# if __name__ == "__main__":
#     main()
