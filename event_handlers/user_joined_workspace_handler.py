from db_helper import db_connection_open
from message_handlers.channel_invitation import invite_user_to_channel_by_email_via_db


def user_joined_workspace_event_handler(event, client, logger):
    """
    Handles the event of a new user joining the workspace. Enters information about him into the database.

    @param event:  User accession event instance.
    @param client: Slack connection instance.
    :param logger: logger instance
    """
    user_id_from_event_ = event['user']
    user_email_ = client.users_info(user_id_from_event_)['user']['profile']['email']

    my_db = db_connection_open()
    my_cursor = my_db.cursor()
    my_cursor.execute("SELECT COUNT(*) FROM users WHERE user_email LIKE '{u_email}';".format(u_email=user_email_))
    is_user_in_db = my_cursor.fetchone()[0]
    if is_user_in_db != 0:
        my_cursor.execute(
            "UPDATE users SET is_present = TRUE WHERE user_email LIKE '{u_email}';".format(u_email=user_email_))
        invite_user_to_channel_by_email_via_db(client, user_email_, my_cursor)
    else:
        my_cursor.execute(
            "INSERT INTO users (user_email, is_present) value ('{u_email}', TRUE);".format(u_email=user_email_))
        client.chat_postMessage(channel=user_id_from_event_,
                                text="Greetings. We suggest you join the channels if you please. :)")
        
    my_db.commit()
    my_cursor.close()
    my_db.close()
