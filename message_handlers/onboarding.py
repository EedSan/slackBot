from slack_helper import is_private_message, is_user_admin

DIVIDER_BLOCK = {"type": "divider"}

onboarding_sent = {}


def onboarding_data(user_id):
    general_text_ = {"type": "section",
                     "text": {"type": "mrkdwn",
                              "text": ("Welcome to Slack and SlackAutomationBot! :wave: "
                                       "We're so glad you're here. :blush:\n\n"
                                       "*Get started by completing the steps below:*"), }, }
    divider_ = {"type": "divider"}
    invite_to_workspace_ = {"type": "section",
                            "text": {"type": "mrkdwn",
                                     "text": ("Firstly invite users to this workspace by sending us your invitation "
                                              "link and csv/xlsx file with list of user emails and "
                                              "tags of groups they're belong to\n"), }, }
    invitation_link_ = {"type": "section",
                        "text": {"type": "mrkdwn",
                                 "text": ("\t:question:Where do I get the invitation link from?\n"
                                          "\t You can reach invitation link to your slack-workspace by following "
                                          "this simple instruction:\n"
                                          "\t1) Click on your workspace name at the top left corner.\n"
                                          "\t2) Click on 'invite people to -your workspace name-' field\n"
                                          "\t3) Click on ':link: Copy invite link' field"), }, }
    invitation_file_ = {"type": "section",
                        "text": {"type": "mrkdwn",
                                 "text": ("\t:question:What should the invitation file look like?\n"
                                          "\tSuch file should be csv/xlsx and and "
                                          "must have columns named `email` and `group`. If your file have some another"
                                          "columns except these two, it's not a problem, they are not taken into "
                                          "account while processing.\n"
                                          "\t Here is an example on such file:"), }, }
    file_img_ = {
        "type": "image",
        "title": {
            "type": "plain_text",
            "text": "Example of invitation file",
        },
        "image_url": "https://i.ibb.co/bgX4tHx/invitation-file-example.png",
        "alt_text": "marg"
    }
    return {"channel": user_id, "blocks": [general_text_, divider_, invite_to_workspace_, divider_, invitation_link_,
                                           divider_, invitation_file_, file_img_], }


def start_onboarding(user_id, client):
    onboarding_text_ = onboarding_data(user_id)
    client.chat_postMessage(**onboarding_text_)


def send_onboarding(message, client):
    if not is_private_message(message) or not is_user_admin(client, message['user']):
        return

    user_id = message["user"]
    start_onboarding(user_id, client)
