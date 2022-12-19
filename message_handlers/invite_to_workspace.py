from email_sender import send_emails
from file_parsers import parse_file
from helper import is_private_message, is_user_admin


def invite_to_workspace(message, client):
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        return

    invitation_link_ = message["text"]
    if 'files' in message:
        url = message['files']['permalink']
        user_file_type = message['files']['filetype']
        file_types_options = ['csv', 'xlsx']

        if user_file_type in file_types_options:
            emails_list_ = parse_file(url, user_file_type)
            msg = 'File parsed.'
            send_emails(emails_list_, invitation_link_)
            msg += ' Emails sent!'
        else:
            msg = "Unknown filetype"
        print(msg)
        return

    else:
        print('No files attached. Please repeat command')
        return
