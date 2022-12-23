import itertools
import re

from db_helper import db_connection_open
from slack_helper import is_private_message, is_user_admin, get_user_id_from_email, get_channel_id_from_name


def channel_invitation_by_user_tags(message, client):
    print(message)
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        return

    expr = r"^invite to[\s+](.+?)[\s+]((.+?))$"
    channel_name_ = re.search(expr, message["text"]).group(1)
    tags_list_ = re.search(expr, message["text"]).group(2).split(" ")  # todo check if elements are tags

    given_tag_names_list = tuple(tags_list_)
    my_db = db_connection_open()
    my_cursor = my_db.cursor()

    my_cursor.execute("select distinct u.user_id from users_channels "
                      "join channels c on c.channel_id = users_channels.channel_id "
                      "join users u on u.user_id = users_channels.user_id join users_tags ut on u.user_id = ut.user_id "
                      "join tags t on t.tag_id = ut.tag_id where tag_name in '{t_name}';"
                      .format(t_name=given_tag_names_list))
    user_ids_ = list(zip(*my_cursor.fetchall()))[0]
    slack_channel_id_ = get_channel_id_from_name(client, channel_name_)
    my_cursor.execute("select channel_id from channels where slack_channel_id like '{s_ch_id}'"
                      .format(s_ch_id=slack_channel_id_))
    channel_db_id_ = list(my_cursor.fetchone())
    data_to_add_to_db_ = list(itertools.product(user_ids_, channel_db_id_))
    my_cursor.executemany("insert into users_channels (user_id, channel_id) VALUE (%s, %s)", data_to_add_to_db_)
    my_db.commit()
    my_cursor.close()
    my_db.close()


def invite_user_to_channel_by_email_via_db(client, user_email_, cursor):
    cursor.execute("select slack_channel_id from users_channels join users u on u.user_id = users_channels.user_id "
                   "join channels c on c.channel_id = users_channels.channel_id where user_email like '{u_mail}'"
                   .format(u_mail=user_email_))
    channels_list_ = list(sum((cursor.fetchall()), ()))
    user_id_ = get_user_id_from_email(client, user_email_)
    for channel_id in channels_list_:
        client.conversations_invite(channel=channel_id, users=[user_id_])
