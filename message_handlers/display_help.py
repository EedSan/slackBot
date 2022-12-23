import re

from slack_helper import is_private_message, is_user_admin


def help_invite_to_channel(user_id):
    """
    :return: message to given user with help description on invite users to channels
    """
    general_invite_ = {"type": "section",
                       "text": {"type": "mrkdwn",
                                "text": ('To invite users channel, type: `invite to [-channel-name-] [-user-tag-]`\n'
                                         '*channel-name*: parameter to specify the channel name.\n'
                                         '*user-tag*: parameter to specify group the users belong to \n NOTE. names '
                                         'of channels and user tags must be wrapped in separate squared brackets'), }, }
    invite_one_ = {"type": "section",
                   "text": {"type": "mrkdwn",
                            "text": ('\tE. g.: `invite to [Data-Science] [KM-91]`\n'
                                     '\t\tIn this particular case, users from the _KM-91_ group will be added '
                                     ' to the channel called _Data-Science_'), }, }
    invite_several_ = {"type": "section",
                       "text": {"type": "mrkdwn",
                                "text": ('You can invite many users to many channels with one command, for this, '
                                         'please list the channel names separated by commas.\n'
                                         '\tE. g. `create channel Data-Science, Data-Analysis, Machine-Learning`\n'
                                         '\t\tIn this particular case, channels named '
                                         '_Data-Science_, _Data-Analysis_, _Machine-Learning_ '
                                         'will be created and you will be added to them.'), }, }
    divider_ = {"type": "divider"}
    return {"channel": user_id, "blocks": [general_invite_, divider_, invite_one_, divider_, invite_several_], }


def help_create_channel(user_id):
    """
    :return: message to given user with help description on create channels
    """
    general_create_ = {"type": "section",
                       "text": {"type": "mrkdwn",
                                "text": ('To create channel, type: `create channel -channel-name-`\n'
                                         '*channel-name*: parameter to specify the channel name.\n'), }, }
    create_one_ = {"type": "section",
                   "text": {"type": "mrkdwn",
                            "text": ('\tE. g.: `create channel Data-Science`\n'
                                     '\t\tIn this particular case, a channel called '
                                     '_Data-Science_ will be created '
                                     'and you will be added to it.'), }, }
    create_several_ = {"type": "section",
                       "text": {"type": "mrkdwn",
                                "text": ('You can create several channels with one command, for this, '
                                         'please list the channel names separated by commas.\n'
                                         '\tE. g. `create channel Data-Science, Data-Analysis, Machine-Learning`\n'
                                         '\t\tIn this particular case, channels named '
                                         '_Data-Science_, _Data-Analysis_, _Machine-Learning_ '
                                         'will be created and you will be added to them.'), }, }

    divider_ = {"type": "divider"}
    return {"channel": user_id, "blocks": [general_create_, divider_, create_one_, divider_, create_several_], }


def general_help(user_id):
    """
    :return: message to given user with general help description
    """
    help_text_ = ('Welcome to SlackBOT help utility! \n'
                  '`*Write some thank words one first time usage`. *'
                  '\nIf you want to ask for help on a particular process, you can type "help _subject_". '
                  'E.g. "help create channel" or "help invite to channel"')
    return {"channel": user_id, "text": help_text_, }


def display_helps(message, client):
    print(message)
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        return

    user_id = message["user"]
    if message['text'].lower() == 'help':
        help_text_data_ = general_help(user_id)
    else:
        help_kind = re.search(r'^help[\s+](.+?)$', message['text']).group(1).split(" ")
        if all(elem in help_kind for elem in ['invite', 'channel']):
            help_text_data_ = help_invite_to_channel(user_id)
        elif all(elem in help_kind for elem in ['create', 'channel']):
            help_text_data_ = help_create_channel(user_id)
        else:
            help_text_data_ = {"channel": user_id, "text": f"unknown argument: <{' '.join(help_kind)}>"}
    client.chat_postMessage(**help_text_data_)
