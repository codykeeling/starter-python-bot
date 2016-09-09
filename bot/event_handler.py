import json
import logging
import requests
import re

logger = logging.getLogger(__name__)


class RtmEventHandler(object):
    def __init__(self, slack_clients, msg_writer):
        self.clients = slack_clients
        self.msg_writer = msg_writer

    def handle(self, event):

        if 'type' in event:
            self._handle_by_type(event['type'], event)

    def _handle_by_type(self, event_type, event):
        # See https://api.slack.com/rtm for a full list of events
        if event_type == 'error':
            # error
            self.msg_writer.write_error(event['channel'], json.dumps(event))
        elif event_type == 'message':
            # message was sent to channel
            self._handle_message(event)
        elif event_type == 'channel_joined':
            # you joined a channel
            self.msg_writer.write_help_message(event['channel'])
        elif event_type == 'group_joined':
            # you joined a private group
            self.msg_writer.write_help_message(event['channel'])
        else:
            pass

    def strip_user_from_msg(self, message, username):
        msg = message[len(username)+4:].strip()
        print 'trimmed message: ' + msg
        return msg


    def _handle_message(self, event):
        # Filter out messages from the bot itself
        if not self.clients.is_message_from_me(event['user']):

            msg_txt = event['text']
            if self.clients.is_bot_mention(msg_txt):
                message = self.strip_user_from_msg(msg_txt, event['user'])
                # e.g. user typed: "@pybot tell me a joke!"
                if 'help' in message:
                    self.msg_writer.write_help_message(event['channel'])
                elif message.startswith('username'):
                    user_to_check = self.clients.substring_message_without_trigger_word(message,'username').strip();
                    status = self.ask_for_username(user_to_check)
                    self.eval_username(event, status, user_to_check)
                elif message.startswith('echo'):
                    self.msg_writer.send_message(event['channel'], self.clients.substring_message_without_trigger_word(message,'echo'))
                elif 'joke' in msg_txt:
                    self.msg_writer.write_joke(event['channel'])
                elif re.search('hi|hey|hello|howdy', msg_txt):
                    self.msg_writer.write_greeting(event['channel'], event['user'])
                # elif 'attachment' in msg_txt:
                #     self.msg_writer.demo_attachment(event['channel'])
                else:
                    self.msg_writer.write_prompt(event['channel'])

    def eval_username(self, event, status, user_to_check):
        if status == 'taken':
            self.msg_writer.send_message(event['channel'], user_to_check + " is taken")
        elif status == 'available':
            self.msg_writer.send_message(event['channel'], user_to_check + " is available")
        elif status == 'length':
            self.msg_writer.send_message(event['channel'],
                                         user_to_check + " is too long to be a Xbox One Premier Entertainment and Gaming System userame.")
        elif status == 'first char':
            self.msg_writer.send_message(event['channel'], "username must start with an alpha character")
        elif status == 'illegal characters':
            self.msg_writer.send_message(event['channel'], "username has illegal characters")
        else:
            self.msg_writer.send_message(event['channel'], user_to_check + " is taken")

    def ask_for_username(self, username):
        headers = {'User-Agent' :'Mozilla/5.0 Ubuntu/8.10 Firefox/3.0.4'}
        payload = { 'tag':username}

        session = requests.Session()
        response = session.post("http://checkgamertag.com/CheckGamertag.php", headers=headers, data=payload)

        return response.text

# else if(message.startsWith("username")){
# String response = checkUsername(event)
#
# if(response == "available"){
# session.sendMessage(event.channel, event.messageContent.substring(8 + 9).trim() + " is available", null)
# }
# else if(response == "length"){
# session.sendMessage(event.channel, event.messageContent.substring(8 + 9).trim()  + " is too long", null)
# }
# else if(response == "first char"){
# session.sendMessage(event.channel, "first character must be alpha", null)
# }
# else if(response == "illegal characters"){
# session.sendMessage(event.channel, "bad characters", null)
# }
# else{
# session.sendMessage(event.channel, event.messageContent.substring(8 + 9).trim() + " is taken", null)
# }

#
#     def getGiphy(def event){
#     def key = "dc6zaTOxFJmzC"
#     def message = event.messageContent.substring(8).trim()
#     //find gif
#     def urlEncodedMessage = URLEncoder.encode(message, "UTF-8")
#     def url = "http://api.giphy.com"
#     def path = "/v1/gifs/search"
#     def query = ['q':urlEncodedMessage,'api_key':key,'limit':1,'rating':'pg']
#     println path
#
#     println url + path
#
#     HTTPBuilder restClient = new HTTPBuilder(url)
#     def response = restClient.request(Method.GET, ContentType.JSON){
#         uri.path=path
#     uri.query = query
#     }
#     return  response.data.get(0).images.downsized.url
# }
