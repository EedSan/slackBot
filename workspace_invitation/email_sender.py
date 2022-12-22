import hashlib
from string import Template

from mailchimp3 import MailChimp

from workspace_invitation.html import html_data

MAILCHIMP_API_KEY = "6fb3b3f970f46ad44321452f69ad6f4c-us21"
MAILCHIMP_USERNAME = "slackautomatizationproject@gmail.com"


def send_mail(emails_list_, url_to_send_):
    client = MailChimp(mc_api=MAILCHIMP_API_KEY, mc_user=MAILCHIMP_USERNAME)
    campaign = process_campaign(client, emails_list_, url_to_send_)
    return client.campaigns.actions.send(campaign_id=campaign['id'])


def process_campaign(cli, emails_list_, url_to_send_):
    list_id = update_list(cli, emails_list_)
    created_campaign = campaign_creation(cli, list_id)
    update_campaign_content(cli, created_campaign['id'], url_to_send_)
    return created_campaign


def get_list_id(lst_data):
    return lst_data["lists"][0]['id'] if lst_data["total_items"] != 0 else 0


def update_list(cli, emails_list):
    """

    :param cli: mailchimp client
    :param emails_list: list of emails to add to audience
    :return: audience_id
    """
    list_id = get_list_id(cli.lists.all())
    drop_list_members(cli, list_id)
    add_members_to_list(cli, list_id, emails_list)
    return list_id


def drop_list_members(cli, audience_id):
    # delete members of mailchimp client list(audience, id given)
    list_members_ = cli.lists.members.all(audience_id, get_all=True)["members"]
    members_emails_to_drop = [member["email_address"] for member in list_members_]
    for email_to_drop in members_emails_to_drop:
        hashed_email = hashlib.md5(email_to_drop.encode('utf-8')).hexdigest()
        cli.lists.members.delete(list_id=audience_id, subscriber_hash=hashed_email)


def add_members_to_list(cli, audience_id, emails_list):
    # add member to mailchimp client list(audience, id given)
    for email_to_add in emails_list:
        cli.lists.members.create(list_id=audience_id, data={"status": 'subscribed', 'email_address': email_to_add})


def campaign_creation(cli, audience_id, url_to_send="google.com"):
    subject_line = "Slack_invitation_test"
    title = "Slack Workspace Invitation Test"
    reply_to = "slackautomatizationproject@gmail.com"
    from_name = "something 1from names1 test"
    campaign = cli.campaigns.create(data={"recipients": {"list_id": audience_id},
                                          "settings": {"subject_line": subject_line,
                                                       "title": title,
                                                       "reply_to": reply_to,
                                                       "from_name": from_name, },
                                          "tracking": {"text_clicks": True},
                                          "type": "plaintext"})  # todo rewrite using regular
    update_campaign_content(cli, campaign['id'], url_to_send)
    return campaign


def update_campaign_content(cli, campaign_id, url_to_send):
    html_code = html_data
    template = Template(html_code).safe_substitute()
    return cli.campaigns.content.update(campaign_id=campaign_id,
                                        data={'message': url_to_send})
