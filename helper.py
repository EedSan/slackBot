def is_user_admin(client, user_id):
    user_info = client.users_info(user=user_id)
    return user_info['is_admin'] or user_info['is_owner']


def is_private_message(message):
    return message["channel_type"] == "im"
