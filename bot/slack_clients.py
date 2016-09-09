
import logging
import re
import time

from slacker import Slacker
from slackclient import SlackClient

logger = logging.getLogger(__name__)


class SlackClients(object):
    def __init__(self, token):
        self.token = token

        # Slacker is a Slack Web API Client
        self.web = Slacker(token)

        # SlackClient is a Slack Websocket RTM API Client
        self.rtm = SlackClient(token)

    def bot_user_id(self):
        return self.rtm.server.login_data['self']['id']

    def is_message_from_me(self, user):
        return user == self.rtm.server.login_data['self']['id']

    def is_bot_mention(self, message):
        bot_user_name = self.rtm.server.login_data['self']['id']
        if re.search("@{}".format(bot_user_name), message):
            return True
        else:
            return False

    def substring_message_without_bot_name(self, message):
        bot_user_name = self.rtm.server.login_data['self']['id']
        print bot_user_name
        return message[len(bot_user_name)+4:]

    def substring_message_without_bot_name_or_username(self, message):
        bot_user_name = self.rtm.server.login_data['self']['id']
        print bot_user_name
        return message[len(bot_user_name + "username ")+4:]

    def substring_message_without_trigger_word(self, message, trigger):
        without_trigger = message[len(trigger):].strip()
        return without_trigger

    def substring_message_without_bot_name_or_echo(self, message):
        bot_user_name = self.rtm.server.login_data['self']['id']
        print bot_user_name
        return message[len(bot_user_name + "echo ")+4:]

    def send_user_typing_pause(self, channel_id, sleep_time=3.0):
        user_typing_json = {"type": "typing", "channel": channel_id}
        self.rtm.server.send_to_websocket(user_typing_json)
        time.sleep(sleep_time)
