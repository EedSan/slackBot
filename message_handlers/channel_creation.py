import re

from slack_sdk.errors import SlackApiError

from helper import is_private_message, is_user_admin


def channel_creation(message, client, logger):
    print(message)
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        return

    user_id = message["user"]
    channel_name = re.search(r'channel[\s+](.+?)$', message['text']).group(1)
    try:
        client.conversations_create(name=channel_name, is_private=False)
    except SlackApiError as e:
        logger.error("Channel probably exists. Error creating channel: {}".format(e))
        client.chat_postMessage(channel=user_id,
                                text=f"Can't create channel `{channel_name}`. Check if it's exist already")
    else:
        msg_to_add = 'To invite other users to channel type `invite to [channel_name] [users_emails]`'
        msg_to_add_info = "For detailed information type `help invite to channel`"
        channels_list = client.conversations_list()["channels"]
        for item in channels_list:
            if item["name"] == channel_name:
                channel_id = item['id']
                msg_created = f"Channel <#{channel_id}> is created :white_check_mark:"
                client.conversations_invite(channel=channel_id, users=[user_id])
                client.chat_postMessage(channel=user_id, text=f'{msg_created}. \n{msg_to_add}. {msg_to_add_info}')
                break
