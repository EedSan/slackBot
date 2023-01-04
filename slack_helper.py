def is_user_admin(client, user_id):
    """
    Checks whether the user from the request is the admin/owner of the current workspace.

    @param client: Slack connection instance.
    @param user_id: The ID of the user to be checked for administration privileges.
    @return: Check result boolean.
    """
    user_info = client.users_info(user=user_id)['user']
    return user_info['is_admin'] or user_info['is_owner']


def is_private_message(message):
    """
    Checks if the current chat is private or public.

    @param message: Query result with information about the current chat.
    @return: Check result boolean.
    """
    return message["channel_type"] == "im"


def get_user_id_from_email(client, email_):
    """
    Gets the user's Slack ID from his or her email address, if such a user exists.

    @param client: Slack connection instance.
    @param email_: Email address of the user whose ID you want to get.
    @return: User ID.
    """

    users_list_ = client.users_list()['members']
    for user in users_list_:
        if user['profile']['email'] == email_:
            return user['id']
        return


def get_channel_id_from_name(client, channel_name_):
    """
    Gets the Slack channel ID by its name, if such a channel exists.

    *

    @param client: Slack connection instance.
    @param channel_name_: The name of the channel whose ID you want to get.
    @return: Channel ID.
    """
    channels_list_ = client.conversations_list()['channels']
    for channel_ in channels_list_:
        if channel_['name'] == channel_name_:
            return channel_['id']
    return
