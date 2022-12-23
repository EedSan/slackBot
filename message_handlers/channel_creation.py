import re

from slack_sdk.errors import SlackApiError

from slack_helper import is_private_message, is_user_admin
from db_helper import db_connection_open


def channel_creation(message, client, logger):
    print(f"msg passed to channel_creation: {message}")
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        return

    user_id = message["user"]
    channel_name = re.search(r'channel[\s+](.+?)$', message['text']).group(1)
    try:
        client.conversations_create(name=channel_name, is_private=False)
        for item in client.conversations_list()["channels"]:
            if item["name"] == channel_name:
                channel_id_ = item['id']
                break
        msg_created = f"Channel <#{channel_id_}> is created :white_check_mark:"

        my_db = db_connection_open()
        my_cursor = my_db.cursor()
        my_cursor.execute("INSERT INTO channels (slack_channel_id) value ('{ch_id}')".format(ch_id=channel_id_))
        my_db.commit()
        my_cursor.close()
        my_db.close()
    except SlackApiError as e:
        logger.error("Channel probably exists. Error creating channel: {}".format(e))
        client.chat_postMessage(channel=user_id,
                                text=f"Can't create channel `{channel_name}`. Check if it's exist already")
    else:
        msg_to_add = 'To invite other users to channel type `invite to [channel_name] [users_emails]`'
        msg_info = "For detailed information type `help invite to channel`"
        client.chat_postMessage(channel=user_id, text=f'{msg_created}. \n{msg_to_add}. {msg_info}')
        client.conversations_invite(channel=channel_id_, users=[user_id])
