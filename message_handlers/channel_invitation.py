import itertools
import re

from db_helper import db_connection_open
from slack_helper import is_private_message, is_user_admin, get_user_id_from_email, get_channel_id_from_name


def channel_invitation_by_user_tags(message, client):
    """
    It implements inviting users who have a certain tag to the channel.

    @param message: Query result with information about the current chat.
    @param client: Slack connection instance.

    *Works only with private chats and non-admin users
    """
    print(message)
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        return

    expr = r"^invite to[\s+]\[(.+?)\][\s+]\[(.+?)\]$"
    channels_names_ = re.search(expr, message["text"]).group(1).split(", ")
    channels_ids_ = [get_channel_id_from_name(client, channel_name_) for channel_name_ in channels_names_]
    given_tag_names_list = re.search(expr, message["text"]).group(2).split(", ")  # todo check if elements are tags
    if len(given_tag_names_list) == 1:
        given_tag_names_list.append(given_tag_names_list[0])
    given_tag_names_list = tuple(given_tag_names_list)

    my_db = db_connection_open()
    my_cursor = my_db.cursor()

    my_cursor.execute("select distinct u.user_id from users_channels "
                      "join channels c on c.channel_id = users_channels.channel_id "
                      "join users u on u.user_id = users_channels.user_id join users_tags ut on u.user_id = ut.user_id "
                      "join tags t on t.tag_id = ut.tag_id where tag_name in {t_name};"
                      .format(t_name=given_tag_names_list))
    user_ids_by_given_tag_ = list(itertools.chain(*my_cursor.fetchall()))
    print(f"user ids: {user_ids_by_given_tag_}")
    if len(user_ids_by_given_tag_) == 1:
        my_cursor.execute("select distinct user_id from users where is_present is TRUE and user_id = {u_ids}"
                          .format(u_ids=user_ids_by_given_tag_[0]))
        present_user_ids_ = tuple(itertools.chain(*my_cursor.fetchall()))
    else:
        my_cursor.execute("select distinct user_id from users where is_present is TRUE and user_id in {u_ids}"
                          .format(u_ids=tuple(user_ids_by_given_tag_)))
        present_user_ids_ = tuple(itertools.chain(*my_cursor.fetchall()))
    not_present_user_ids_ = list(set(user_ids_by_given_tag_).symmetric_difference(set(present_user_ids_)))

    presented_emails_ = []
    for presented_user in present_user_ids_:
        my_cursor.execute("select user_email from users where user_id = {u_id}".format(u_id=presented_user))
        presented_emails_.append(list(itertools.chain(*my_cursor.fetchall()))[0])
    print(f"emails: {presented_emails_}")
    slack_user_ids = [get_user_id_from_email(client, email) for email in presented_emails_]
    for channel_id_ in channels_ids_:
        client.conversations_invite(channel=channel_id_, users=slack_user_ids)

    if len(channels_ids_) == 1:
        my_cursor.execute("select channel_id from channels where slack_channel_id like '{s_ch_id}'"
                          .format(s_ch_id=channels_ids_[0]))
    else:
        my_cursor.execute("select channel_id from channels where slack_channel_id in {s_ch_ids}"
                          .format(s_ch_ids=tuple(channels_ids_)))
    channel_db_ids_ = list(my_cursor.fetchone())
    data_to_add_to_db_ = list(itertools.product(not_present_user_ids_, channel_db_ids_))
    my_cursor.executemany("insert into users_channels (user_id, channel_id) VALUE (%s, %s)", data_to_add_to_db_)
    my_db.commit()
    my_cursor.close()
    my_db.close()


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
    user_id_ = get_user_id_from_email(client, user_email_)
    for channel_id in channels_list_:
        client.conversations_invite(channel=channel_id, users=[user_id_])
