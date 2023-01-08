import logging
import os
import re
from json import load
from unittest import TestCase

import mock
from slack_sdk import WebClient

from app import create_channel, invite_to_channel, onboarding, display_help

slack_web_client_ = WebClient()

logging.basicConfig(filename='test_logger.log', filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def get_last_line_from_logs(log_file):
    with open(log_file, 'rb') as f:
        try:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
    return last_line


class TestApp(TestCase):

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(
                           open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'conversations_create')
    @mock.patch.object(slack_web_client_, 'conversations_setTopic')
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    @mock.patch('psycopg2.connect')
    def test_create_single_templated_channel(self, *_):
        with open(
                'resources/create_channels_resources/message_from_user_to_create_single_templated_channel_data.json') as f:
            msg_data_from_user_to_create_channel_ = load(f)
        create_channel(message=msg_data_from_user_to_create_channel_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Channel(s) `channel-1` creation complete.")

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(
                           open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'conversations_create')
    @mock.patch.object(slack_web_client_, 'conversations_setTopic')
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    @mock.patch('psycopg2.connect')
    def test_create_multiple_templated_channel(self, *_):
        with open(
                'resources/create_channels_resources/message_from_user_to_create_multiple_templated_channel_data.json') as f:
            msg_data_from_user_to_create_channel_ = load(f)
        create_channel(message=msg_data_from_user_to_create_channel_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Channel(s) `channel-1, Channel2, channel-3 Channel4` creation complete.")

    @mock.patch.object(slack_web_client_, 'users_info', return_value=load(
        open('resources/slack_helper_resources/users_info_successful_response_not_admin.json')))
    @mock.patch.object(slack_web_client_, 'conversations_create')
    @mock.patch.object(slack_web_client_, 'conversations_setTopic')
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    @mock.patch('psycopg2.connect')
    def test_create_channel_not_admin(self, *_):
        with open(
                'resources/create_channels_resources/message_from_user_to_create_single_templated_channel_data.json') as f:
            msg_data_from_user_to_create_channel_ = load(f)
        create_channel(message=msg_data_from_user_to_create_channel_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'WARNING (.*)', last_line)[0],
                         "Message from user passed to channel_creation wasn't private / from admin.")

    @mock.patch.object(slack_web_client_, 'users_info', return_value=load(
        open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'conversations_list', return_value=load(
        open('resources/slack_helper_resources/conversations_list_successful_response.json')))
    @mock.patch.object(slack_web_client_, 'conversations_invite')
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    @mock.patch('psycopg2.connect')
    def test_invite_to_several_channel_by_several_tags(self, *_):
        with open(
                'resources/invite_to_channels_resources/message_from_user_to_invite_to_several_channels_by_several_tags_data.json') as f:
            msg_data_from_user_to_invite_to_channels_ = load(f)
        invite_to_channel(message=msg_data_from_user_to_invite_to_channels_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Invitation `casdjvsd, gasghts ! tag 1 name, tag 3 name` complete.")

    @mock.patch.object(slack_web_client_, 'users_info', return_value=load(
        open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'conversations_list', return_value=load(
        open('resources/slack_helper_resources/conversations_list_successful_response.json')))
    @mock.patch.object(slack_web_client_, 'conversations_invite')
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    @mock.patch('psycopg2.connect')
    def test_invite_to_channel_by_several_tags(self, *_):
        with open(
                'resources/invite_to_channels_resources/message_from_user_to_invite_to_channel_by_several_tags_data.json') as f:
            msg_data_from_user_to_invite_to_channels_ = load(f)
        invite_to_channel(message=msg_data_from_user_to_invite_to_channels_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Invitation `casdjvsd ! tag 1 name, tag 3 name` complete.")

    @mock.patch.object(slack_web_client_, 'users_info', return_value=load(
        open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'conversations_list', return_value=load(
        open('resources/slack_helper_resources/conversations_list_successful_response.json')))
    @mock.patch.object(slack_web_client_, 'conversations_invite')
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    @mock.patch('psycopg2.connect')
    def test_invite_to_several_channels_by_tag(self, *_):
        with open(
                'resources/invite_to_channels_resources/message_from_user_to_invite_to_several_channels_by_tag_data.json') as f:
            msg_data_from_user_to_invite_to_channels_ = load(f)
        invite_to_channel(message=msg_data_from_user_to_invite_to_channels_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Invitation `casdjvsd, gasghts ! tag 1 name` complete.")

    @mock.patch.object(slack_web_client_, 'users_info', return_value=load(
        open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'conversations_list', return_value=load(
        open('resources/slack_helper_resources/conversations_list_successful_response.json')))
    @mock.patch.object(slack_web_client_, 'conversations_invite')
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    @mock.patch('psycopg2.connect')
    def test_invite_to_channel_by_tag(self, *_):
        with open(
                'resources/invite_to_channels_resources/message_from_user_to_invite_to_channel_by_tag_data.json') as f:
            msg_data_from_user_to_invite_to_channels_ = load(f)
        invite_to_channel(message=msg_data_from_user_to_invite_to_channels_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Invitation `casdjvsd ! tag 1 name` complete.")

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(
                           open('resources/slack_helper_resources/users_info_successful_response_not_admin.json')))
    @mock.patch.object(slack_web_client_, 'conversations_list',
                       return_value=load(
                           open('resources/slack_helper_resources/conversations_list_successful_response.json')))
    @mock.patch.object(slack_web_client_, 'conversations_invite')
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    @mock.patch('psycopg2.connect')
    def test_invite_to_channel_by_tag_not_admin(self, *_):
        with open(
                'resources/invite_to_channels_resources/message_from_user_to_invite_to_channel_by_tag_data.json') as f:
            msg_data_from_user_to_invite_to_channels_ = load(f)
        invite_to_channel(message=msg_data_from_user_to_invite_to_channels_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'WARNING (.*)', last_line)[0],
                         "Message from user passed to channel_creation wasn't private / from admin.")

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(
                           open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    def test_display_onboarding(self, *_):
        with open(
                'resources/message_from_user_to_send_onboarding.json') as f:
            msg_data_from_user_to_send_onboarding_ = load(f)
        onboarding(message=msg_data_from_user_to_send_onboarding_, client=slack_web_client_)
        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Onboarding message display complete.")

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(
                           open('resources/slack_helper_resources/users_info_successful_response_not_admin.json')))
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    def test_display_onboarding_not_admin(self, *_):
        with open(
                'resources/message_from_user_to_send_onboarding.json') as f:
            msg_data_from_user_to_send_onboarding_ = load(f)
        onboarding(message=msg_data_from_user_to_send_onboarding_, client=slack_web_client_)
        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'WARNING (.*)', last_line)[0],
                         "Message from user passed to channel_creation wasn't private / from admin.")

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(
                           open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    def test_display_general_help(self, *_):
        with open(
                'resources/display_help_resources/message_from_user_to_send_help.json') as f:
            msg_data_from_user_to_send_help_ = load(f)
        display_help(message=msg_data_from_user_to_send_help_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Help message display complete.")

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(
                           open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    def test_display_help_on_channel_creation(self, *_):
        with open(
                'resources/display_help_resources/message_from_user_to_send_help_on_channel_creation.json') as f:
            msg_data_from_user_to_send_help_ = load(f)
        display_help(message=msg_data_from_user_to_send_help_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Help message display complete.")

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(
                           open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    def test_display_help_on_channel_invitation(self, *_):
        with open(
                'resources/display_help_resources/message_from_user_to_send_help_on_channel_invitation.json') as f:
            msg_data_from_user_to_send_help_ = load(f)
        display_help(message=msg_data_from_user_to_send_help_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Help message display complete.")

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(
                           open('resources/slack_helper_resources/users_info_successful_response_admin.json')))
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    def test_display_help_on_unknown_argument(self, *_):
        with open(
                'resources/display_help_resources/message_from_user_to_send_help_on_unknown_argument.json') as f:
            msg_data_from_user_to_send_help_ = load(f)
        display_help(message=msg_data_from_user_to_send_help_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        self.assertEqual(re.findall(r'INFO (.*)', last_line)[0],
                         "Status: SUCCESSFUL. Help message display complete.")

    @mock.patch.object(slack_web_client_, 'users_info',
                       return_value=load(
                           open('resources/slack_helper_resources/users_info_successful_response_not_admin.json')))
    @mock.patch.object(slack_web_client_, 'chat_postMessage')
    def test_display_help_not_admin(self, *_):
        with open(
                'resources/display_help_resources/message_from_user_to_send_help_on_unknown_argument.json') as f:
            msg_data_from_user_to_send_help_ = load(f)
        display_help(message=msg_data_from_user_to_send_help_, client=slack_web_client_)

        last_line = get_last_line_from_logs('test_logger.log')
        print(last_line)
        self.assertEqual(re.findall(r'WARNING (.*)', last_line)[0],
                         "Message from user passed to channel_creation wasn't private / from admin.")
