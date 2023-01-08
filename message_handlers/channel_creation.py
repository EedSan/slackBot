import re

from slack_sdk.errors import SlackApiError

from slack_helper import is_private_message, is_user_admin
from db_helper import db_connection_open


def channel_creation(message, client, logger):
    """
    Creates a channel with specified characteristics.
    Uses templates to create two channels at once, one for lecture information and one for practical exercises.

    *Works only with private chats and admin users
    @param message: Query result with information about the current event.
    @param client: Slack connection instance.
    @param logger: Logger instance.
    """
    logger.info(f"Message from user passed to channel_creation: `{message}`")
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        logger.warning(f"Message from user passed to channel_creation wasn't private / from admin.")
        return

    # todo create single (untemplated) channel

    user_id_ = message["user"]
    unformatted_channels_names_list_ = re.search(r'create\s+(.+?)$', message['text']).group(1)
    temp_channels_names_list_ = list(map(str.lower, unformatted_channels_names_list_.split(" ")))
    channels_names_list_ = [s.strip(',') for s in temp_channels_names_list_]

    templates_ = ["course", "practice"]
    for channel_name_ in channels_names_list_:
        for template_ in templates_:
            templated_channel_name_ = channel_name_ + "-" + template_
            logger.info(f"Attempt to create channel `{templated_channel_name_}`")
            try:
                res_of_channel_creation_ = client.conversations_create(name=templated_channel_name_, is_private=False)
                logger.info(f"result of channel `{templated_channel_name_}` creation: {res_of_channel_creation_}")
                channel_id_ = res_of_channel_creation_['channel']['id']
                res_of_topic_setter_ = client.conversations_setTopic(
                    channel=channel_id_, topic=f"This channel is about {templated_channel_name_}")
                logger.info(f"result of setting topic for channel `{templated_channel_name_}`: {res_of_topic_setter_}")
                msg_created_ = f"Channel <#{channel_id_}> is created :white_check_mark:"
                client.chat_postMessage(channel=user_id_, text=f'{msg_created_}.')
                logger.info(f"Message `{msg_created_}` is send to user {user_id_}")
            except SlackApiError as e:
                logger.error(f"Channel creation attempt unsuccessful. Status: Error: {e}")
                msg_on_error_ = f"Status: FAILED. Error on channel `{templated_channel_name_}` creation."
                client.chat_postMessage(channel=user_id_, text=msg_on_error_)
                logger.info(f"Message `{msg_on_error_}` is send to user {user_id_}")
                break
            else:
                logger.info(f"Attempt to add channel `{templated_channel_name_}` instance to database")
                my_db = db_connection_open()
                my_cursor = my_db.cursor()
                logger.info(f"Database connection established")
                my_cursor.execute("INSERT INTO channels (slack_channel_id) value ('{ch_id}')".format(ch_id=channel_id_))
                my_db.commit()
                logger.info(f"Channel with slack channel id: {channel_id_} is committed into database")
                my_cursor.close()
                my_db.close()
                logger.info(f"Database connection closed")
                logger.info(f"Status: SUCCESSFUL. Addition channel `{templated_channel_name_}` instance to database.")

        else:
            msg_to_add_ = 'To invite users into specific channel type `invite to [channel_name] [users_emails]`'
            msg_info_ = "For detailed information use command `help invite to channel`"
            final_msg_ = msg_to_add_ + ". " + msg_info_
            client.chat_postMessage(channel=user_id_, text=final_msg_)
            logger.info(f"Message `{final_msg_}` is send to user {user_id_}")
            logger.info(f"Status: SUCCESSFUL. Channel(s) `{unformatted_channels_names_list_}` creation complete.")
            # todo add a parameter indicating whether to add admin who use the bot to the channel or not


def channel_deletion_handler(event):  # todo
    # my_db = db_connection_open()
    # my_cursor = my_db.cursor()
    # my_cursor.execute("delete from channels (slack_channel_id) value ('{ch_id}')".format(ch_id=channel_id_))
    # my_db.commit()
    # my_cursor.close()
    # my_db.close()
    pass
