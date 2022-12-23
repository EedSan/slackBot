def is_user_admin(client, user_id):
    user_info = client.users_info(user=user_id)
    return user_info['is_admin'] or user_info['is_owner']


def is_private_message(message):
    return message["channel_type"] == "im"


def get_user_id_from_email(client, email_):
    users_list_ = client.users_list()['members']
    for user in users_list_:
        if user['profile']['email'] == email_:
            return user['id']
        return


def get_channel_id_from_name(client, channel_name_):
    channels_list_ = client.conversations_list()['channels']
    for channel_ in channels_list_:
        if channel_['name'] == channel_name_:
            return channel_['id']
    return
