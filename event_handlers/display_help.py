import re


def help_invite_to_channel(user_id):
    """
    :return: message to given user with help description
    """
    text_ = "Some help on channel invitation."
    return {"channel": user_id, "text": text_, }


def help_create_channel(user_id):
    """
    :return: message to given user with help description
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
    :return: message to given user with help description
    """
    help_text_ = ('Welcome to SlackBOT help utility! \n'
                  '`*Write some thank words one first time usage`. *'
                  '\nIf you want to ask for help on a particular process, you can type "help _subject_". '
                  'E.g. "help create channel" or "help invite to channel"')
    return {"channel": user_id, "text": help_text_, }


def disp_helps(message, client):
    print(message)
    if message["channel_type"] != "im":
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
