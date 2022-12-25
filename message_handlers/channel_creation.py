import re

from slack_sdk.errors import SlackApiError

from slack_helper import is_private_message, is_user_admin, get_channel_id_from_name
from db_helper import db_connection_open


def channel_creation(message, client, logger):
    print(f"msg passed to channel_creation: {message}")
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        return

    user_id = message["user"]
    channel_name_message_ = re.search(r'channel[\s+](.+?)$', message['text']).group(1)
    templates_ = ["course", "practice"]
    for template_ in templates_:
        channel_name_ = channel_name_message_ + "-" + template_
        try:
            client.conversations_create(name=channel_name_, is_private=False)
            channel_id_ = get_channel_id_from_name(client, channel_name_)
            msg_created = f"Channel <#{channel_id_}> is created :white_check_mark:"
            client.chat_postMessage(channel=user_id, text=f'{msg_created}.')
        except SlackApiError as e:
            logger.error("Channel probably exists. Error creating channel: {}".format(e))
            client.chat_postMessage(channel=user_id,
                                    text=f"Can't create channel `{channel_name_}`. Check if it's exist already")
        else:
            my_db = db_connection_open()
            my_cursor = my_db.cursor()
            my_cursor.execute("INSERT INTO channels (slack_channel_id) value ('{ch_id}')".format(ch_id=channel_id_))
            my_db.commit()
            my_cursor.close()
            my_db.close()
    else:
        msg_to_add = 'To invite users into specific channel type `invite to [channel_name] [users_emails]`'
        msg_info = "For detailed information use command `help invite to channel`"
        client.chat_postMessage(channel=user_id, text=f'{msg_to_add}. {msg_info}')
        # todo add a parameter indicating whether to add admin who use the bot to the channel or not
