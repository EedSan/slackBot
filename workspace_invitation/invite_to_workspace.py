from file_parsers import parse_file
from slack_helper import is_private_message, is_user_admin
from workspace_invitation.email_sender import send_mail


def invite_to_workspace(message, client, logger):
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        return

    invitation_link_ = message["text"]
    if 'files' in message:
        url = message['files']['permalink']
        user_file_type = message['files']['filetype']
        file_types_options = ['csv', 'xlsx']

        if user_file_type in file_types_options:
            emails_list_, groups_list_ = parse_file(url, user_file_type)
            print('File parsed.')
            print('Emails sending. It might take some time.')
            send_mail(emails_list_, invitation_link_)
            print('Emails sent.')
        else:
            print("Unknown filetype")
        return

    else:
        print('No files attached. Please repeat command')
        return
