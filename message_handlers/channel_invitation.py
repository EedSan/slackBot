import itertools
import re

from db_helper import db_connection_open
from slack_helper import is_private_message, is_user_admin, get_user_id_by_email, get_channel_id_by_name


def channel_invitation_by_user_tags(message, client, logger):
    """
    It implements inviting users who have a certain tag to the channel.

    @param message: Query result with information about the current chat.
    @param client: Slack connection instance.
    @param logger: logger instance

    *Works only within private chat with admin users
    """
    logger.info(f"Message from user passed to channel_invitation_by_user_tags: `{message}`")
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        logger.warning(f"Message from user passed to channel_creation wasn't private / from admin.")
        return

    expr = r"^invite to[\s+](.*)$"
    user_given_data_ = re.search(expr, message["text"]).group(1)
    [temp_channels_names_, temp_given_tag_names_list_] = re.split(r"[\s+]![\s+]", user_given_data_)
    channels_names_ = [s for s in temp_channels_names_.split(", ")]
    given_tag_names_list_ = [s for s in temp_given_tag_names_list_.split(", ")]

    channels_ids_ = [get_channel_id_by_name(client, channel_name_) for channel_name_ in channels_names_]
    # todo  given_tag_names_list_ elements are tags validator
    if len(given_tag_names_list_) == 1:
        given_tag_names_list_ += given_tag_names_list_
    given_tag_names_list_ = tuple(given_tag_names_list_)

    my_db = db_connection_open()
    my_cursor = my_db.cursor()
    logger.info(f"Database connection established")

    my_cursor.execute("select distinct u.user_id from users_channels "
                      "join channels c on c.channel_id = users_channels.channel_id "
                      "join users u on u.user_id = users_channels.user_id join users_tags ut on u.user_id = ut.user_id "
                      "join tags t on t.tag_id = ut.tag_id where tag_name in {t_name};"
                      .format(t_name=given_tag_names_list_))
    db_user_ids_by_given_tags_ = list(itertools.chain(*my_cursor.fetchall()))
    logger.info(f"All database user ids by tags: {given_tag_names_list_} -> {db_user_ids_by_given_tags_}")
    if len(db_user_ids_by_given_tags_) == 1:
        my_cursor.execute("select distinct user_id from users where is_present is TRUE and user_id = {u_ids}"
                          .format(u_ids=db_user_ids_by_given_tags_[0]))
    else:
        my_cursor.execute("select distinct user_id from users where is_present is TRUE and user_id in {u_ids}"
                          .format(u_ids=tuple(db_user_ids_by_given_tags_)))
    present_user_ids_ = tuple(itertools.chain(*my_cursor.fetchall()))
    logger.info(f"All database user ids for users present in workspace: {present_user_ids_}")
    not_present_user_ids_ = list(set(db_user_ids_by_given_tags_).symmetric_difference(set(present_user_ids_)))
    logger.info(f"All database user ids for users not present in workspace: {not_present_user_ids_}")

    presented_emails_ = []
    for presented_user in present_user_ids_:
        my_cursor.execute("select user_email from users where user_id = {u_id}".format(u_id=presented_user))
        presented_emails_.append(list(itertools.chain(*my_cursor.fetchall()))[0])
    logger.info(f"All emails from database for users present in workspace by database user id: {presented_emails_}")
    slack_user_ids_ = [get_user_id_by_email(client, email) for email in presented_emails_]
    for channel_id_ in channels_ids_:
        res_of_invitation_ = client.conversations_invite(channel=channel_id_, users=slack_user_ids_)
        logger.info(f"result of inviting users {slack_user_ids_} to channel {channel_id_}: {res_of_invitation_}")

    if len(channels_ids_) == 1:
        my_cursor.execute("select channel_id from channels where slack_channel_id like '{s_ch_id}'"
                          .format(s_ch_id=channels_ids_[0]))
    else:
        my_cursor.execute("select channel_id from channels where slack_channel_id in {s_ch_ids}"
                          .format(s_ch_ids=tuple(channels_ids_)))
    channel_db_ids_ = list(my_cursor.fetchone())
    logger.info(f"All database channel ids for channels to add users not present in workspace to: {channel_db_ids_}")

    data_to_add_to_db_ = list(itertools.product(not_present_user_ids_, channel_db_ids_))
    logger.info(f"Data to add to users_channels table in database: {data_to_add_to_db_}")
    my_cursor.executemany("insert into users_channels (user_id, channel_id) VALUE (%s, %s)", data_to_add_to_db_)
    my_db.commit()
    logger.info(f"Data committed into database")
    my_cursor.close()
    my_db.close()
    logger.info(f"Database connection closed")
    final_msg_ = ("Invitation complete. Some users might not have been invited to channels, "
                  "they will be invited automatically after joining workspace.")
    client.chat_postMessage(channel=message["user"], text=final_msg_)
    logger.info(f"Message `{final_msg_}` is send to user {message['user']}")
    logger.info(f"Status: SUCCESSFUL. Invitation `{user_given_data_}` complete.")


def invite_user_to_channel_by_email_via_db(client, user_email_, cursor):
    """
    Sends an invitation to the channel using pending entries from the database.

    @param client: Slack connection instance.
    @param user_email_: Invites specified user to specified channel.
    @param cursor: Database connection cursor.
    """
    cursor.execute("select slack_channel_id from users_channels join users u on u.user_id = users_channels.user_id "
                   "join channels c on c.channel_id = users_channels.channel_id where user_email like '{u_mail}'"
                   .format(u_mail=user_email_))
    channels_list_ = list(sum((cursor.fetchall()), ()))
    user_id_ = get_user_id_by_email(client, user_email_)
    for channel_id in channels_list_:
        client.conversations_invite(channel=channel_id, users=[user_id_])
