from json import load
from unittest import TestCase

import mock
from slack_sdk import WebClient

from slack_helper import is_user_admin, is_private_message, get_user_id_by_email, get_channel_id_by_name

slack_web_client_ = WebClient()


class TestSlackHelper(TestCase):

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(open(
                           'resources/slack_helper_resources/users_info_successful_response_admin.json')))
    def test_check_is_user_admin_true_(self, _):
        usr_id = '123456'
        result = is_user_admin(slack_web_client_, usr_id)
        assert result is True

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(open(
                           'resources/slack_helper_resources/users_info_successful_response_not_admin.json')))
    def test_check_is_user_admin_false_(self, _):
        usr_id = '123456'
        result = is_user_admin(slack_web_client_, usr_id)
        assert result is False

    def test_check_is_private_message_true_(self):
        with open('resources/slack_helper_resources/private_message_data.json') as f:
            msg = load(f)
        result = is_private_message(msg)
        assert result is True

    def test_check_is_private_message_false_(self):
        with open('resources/slack_helper_resources/not_private_message_data.json') as f:
            msg = load(f)
        result = is_private_message(msg)
        assert result is False

    @mock.patch.object(slack_web_client_, 'users_list',
                       return_value=load(open(
                           'resources/slack_helper_resources/users_list_successful_response.json')))
    def test_get_user_id_by_email_(self, _):
        usr_email = '123456@gmail.com'
        result = get_user_id_by_email(slack_web_client_, usr_email)
        assert result == "W012A3CDE"

    @mock.patch.object(slack_web_client_, 'users_list',
                       return_value=load(open(
                           'resources/slack_helper_resources/users_list_successful_response.json')))
    def test_user_id_by_email_not_found_(self, _):
        usr_email = '1256@gmail.com'
        result = get_user_id_by_email(slack_web_client_, usr_email)
        assert result is None

    @mock.patch.object(slack_web_client_, 'conversations_list',
                       return_value=load(open(
                           'resources/slack_helper_resources/conversations_list_successful_response.json')))
    def test_get_channel_id_by_name_(self, _):
        channel_name = 'casdjvsd'
        result = get_channel_id_by_name(slack_web_client_, channel_name)
        assert result == "C012AB3CD"

    @mock.patch.object(slack_web_client_, 'conversations_list',
                       return_value=load(open(
                           'resources/slack_helper_resources/conversations_list_successful_response.json')))
    def test_channel_id_by_name_not_found_(self, _):
        channel_name = 'aaaaa'
        result = get_channel_id_by_name(slack_web_client_, channel_name)
        assert result is None
