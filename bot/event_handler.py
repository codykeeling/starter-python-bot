import json
import logging
import requests
import re
import urllib.request, urllib.parse, urllib.error
import pprint
import random
from imgurpython import ImgurClient
import random

eloTypes = {'control': 10, 'clash': 12, 'supremacy': 31, 'survival': 37, 'countdown': 38, 'trials': 39}
logger = logging.getLogger(__name__)


def substring_message_no_hawbot(cleanString):
    splits = cleanString.split()
    #print splits
    #print splits[0]
    if splits[0] in list(eloTypes.keys()):
        return splits[0]
    return 'control'


def substring_message_game_mode(cleanString):
    splits = cleanString.split()
    #print splits
    #print splits[0]
    if splits[0] in list(eloTypes.keys()):
        return splits[0]
    return 'control'


def substring_message_username(cleanString):
    splits = cleanString.split()
    #print splits
    #print splits[0]
    if splits[0] in list(eloTypes.keys()):
        first, _, rest = cleanString.partition(" ")
        return rest


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
            self.msg_writer.write_help_message(event['channel'])
        elif event_type == 'group_joined':
            # you joined a private group
            self.msg_writer.write_help_message(event['channel'])
        else:
            pass

    def strip_user_from_msg(self, message, username):
        msg = message[len(username) + 4:].strip()
        # print 'trimmed message: ' + msg
        return msg

    def _handle_message(self, event):
        if event.get('user') is not None and not self.clients.is_message_from_me(event['user']):

            msg_txt = event['text']
            if self.clients.is_bot_mention(msg_txt) and 'U1TUSDTPC' not in event.get('user') and 'U1T64QE8N' not in event.get('user'):
                message = self.strip_user_from_msg(msg_txt, event['user'])
                # e.g. user typed: "@pybot tell me a joke!"
                if 'help' in message:
                    self.msg_writer.write_help_message(event['channel'])
                elif message.startswith('username'):
                    user_to_check = self.clients.substring_message_without_trigger_word(message, 'username').strip();

                    if 'U1TUSDTPC' in event.get('user'):
                        self.msg_writer.send_message(event['channel'], "Drain can go eat a dick")
                    else:
                        status = self.ask_for_username(user_to_check)
                        self.eval_username(event, status, user_to_check)
                elif message.startswith('hours'):
                    user_to_check = self.clients.substring_message_without_trigger_word(message, 'hours').strip();
                    hours = self.hours_played(user_to_check)
                    self.msg_writer.send_message(event['channel'],
                                                 user_to_check + " has played " + str(hours) + " hours")
                elif message.lower().startswith('elo'):
                    user_to_check = self.clients.substring_message_without_trigger_word(message, 'elo').strip();

                    # mode = 'control'
                    # cleanString = substring_message_no_hawbot(user_to_check)
                    cleanString = user_to_check
                    #print 'cleanString:{}'.format(cleanString)
                    cleanStringModes = self.substring_message_game_mode(event,cleanString)
                    cleanStringUsername = substring_message_username(cleanString)

                    if not cleanStringUsername:
                        cleanStringUsername = cleanString

                    #print "cleanStringUsername: " + cleanStringUsername
                    #print "cleanStringModes: " + cleanStringModes
                    elo = self.elo(cleanStringUsername, cleanStringModes)

                    if elo and 'elo' in elo:
                        eloNumber = elo['elo']
                    else:
                        eloNumber = 69
                    self.msg_writer.send_message(event['channel'],
                                                 cleanStringUsername + " has a " + cleanStringModes + " elo of " + str(
                                                     "{0:.0f}".format(eloNumber)))
                elif message.startswith('gif'):
                    gif_to_check = self.clients.substring_message_without_trigger_word(message, 'gif').strip();
                    url = self.ask_for_gif(gif_to_check)
                    self.msg_writer.send_message(event['channel'], url)
                elif message.startswith('echo'):
                    self.msg_writer.send_message(event['channel'],
                                                 self.clients.substring_message_without_trigger_word(message, 'echo'))
                elif 'dadjoke' in msg_txt:
                    text = self.ask_for_dad_joke()
                    self.msg_writer.send_message(event['channel'], text['SETUP'])
                    self.clients.send_user_typing_pause(event['channel'])
                    self.msg_writer.send_message(event['channel'], text['PUNCHLINE'])
                elif 'joke' in msg_txt and 'dadjoke' not in msg_txt:
                    text = self.ask_for_joke()
                    self.msg_writer.send_message(event['channel'], text)
                elif re.search('hi|hey|hello|howdy', msg_txt, re.IGNORECASE):
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
                                         user_to_check + " is too long to be a Xbox One Premier Entertainment and Gaming System userlame.")
        elif status == 'first char':
            self.msg_writer.send_message(event['channel'], "username must start with an alpha character")
        elif status == 'illegal characters':
            self.msg_writer.send_message(event['channel'], "username has illegal characters")
        else:
            self.msg_writer.send_message(event['channel'], user_to_check + " is taken")

    # def ask_for_username(self, username):
    #     payload = {'tag': username}
    #
    #     if username[0].isdigit():
    #         return 'first char'
    #
    #     if not all(x.isalnum() or x.isspace() for x in username):
    #         return 'illegal characters'
    #
    #     if len(username) > 15:
    #         return 'length'
    #
    #     response = requests.post("http://www.gamertag.net/", data=payload)
    #
    #     if "is available to use!" in response.text:
    #         return 'available'
    #
    #     return response.text

    def ask_for_username(self, username):
        payload = {'tag':username,'t':0.667003289277363}
        headers = {'Content-type':'application/x-www-form-urlencoded'}


        if username[0].isdigit():
            return 'first char'

        if not all(x.isalnum() or x.isspace() for x in username):
            return 'illegal characters'

        if len(username) > 15:
            return 'length'

        # response = requests.post("http://www.gamertag.net/", data=payload)
        response = requests.post("https://checkgamertag.com/CheckGamertag.php", data=payload, headers=headers)
        # payload = {'tag':username}
        #
        # if username[0].isdigit():
        #     return 'first char'
        #
        # if not all(x.isalnum() or x.isspace() for x in username):
        #     return 'illegal characters'
        #
        # if len(username) > 15:
        #     return 'length'
        #
        # response = requests.post("http://www.gamertag.net/", data=payload)

        if "is available to use!" in response.text:
            return 'available'

        return response.text

    def hours_played(self, username):
        headers = {'User-Agent': 'Mozilla/5.0 Ubuntu/8.10 Firefox/3.0.4'}
        payload = {'console': '1', 'user': username}

        session = requests.Session()
        response = session.get("https://www.wastedondestiny.com/api/", params=payload)
        # print response.text
        map = json.loads(response.text)
        # print map
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(map)

        try:
            hours = map['Response']['totalTimePlayed']
            hours = hours / 60 / 60
            return hours
        except:
            return 0

    def substring_message_game_mode(self, event, cleanString):
        splits = cleanString.split()
        # print splits
        # print splits[0]
        if splits[0] in list(eloTypes.keys()):
            return splits[0]
        self.msg_writer.send_message(event['channel'],  "Available modes: " + str(list(eloTypes.keys())))
        return 'control'


    def elo(self, username, mode):
        headers = {'User-Agent': 'Mozilla/5.0 Ubuntu/8.10 Firefox/3.0.4', 'Host': 'api.guardian.gg',
                   'Accept': 'application/json, text/plain,*/*',
                   'Referer': 'https://guardian.gg/2/profile/1/{0}'.format(username), 'origin': 'https://guardian.gg'}

        session = requests.Session()
        response = session.get("https://api.guardian.gg/v2/players/1/{0}?lc=en".format(username), headers=headers)
        # print response.text
        if not response.text:
            map = {}
        else:
            map = json.loads(response.text)
            
        # print map
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(map)

        if mode in eloTypes:
            try:
                elos = map['player']['stats']
                controlElo = elos[next(index for (index, d) in enumerate(elos) if d["mode"] == eloTypes[mode])]
                return controlElo
            except:
                return 0
        return "{0} is not an acceptable game mode (control,clash,supremacy,survival,countdown,trials)".format(mode)

    # def elo(self,username,mode):
    #     mode = mode.lower()
    #     headers = {'User-Agent' :'Mozilla/5.0 Ubuntu/8.10 Firefox/3.0.4', 'Host':'api.guardian.gg', 'Accept':'application/json, text/plain,*/*',
    #                'Referer':'https://guardian.gg/2/profile/1/{0}'.format(username),'origin':'https://guardian.gg'}
    #     payload = {'console':'1','user':username}
    #
    #     session = requests.Session()
    #     response = session.get("https://api.guardian.gg/v2/players/1/{0}?lc=en".format(username), headers=headers)
    #     # print response.text
    #     map = json.loads(response.text)
    #     # print map
    #     # pp = pprint.PrettyPrinter(indent=4)
    #     # pp.pprint(map)
    #
    #     if mode in eloTypes:
    #         try:
    #             elos = map['player']['stats']
    #             print elos
    #             controlElo = elos[next(index for (index, d) in enumerate(elos) if d["mode"] == eloTypes[mode])]
    #             print controlElo
    #             return controlElo
    #         except:
    #             return 0
    #     return "{0} is not an acceptable game mode (control,clash,supremacy,survival,countdown,trials)".format(mode)



    def ask_for_gif(self, gif_request):
        key = "dc6zaTOxFJmzC"
        headers = {'User-Agent': 'Mozilla/5.0 Ubuntu/8.10 Firefox/3.0.4'}
        payload = {'q': gif_request, 'api_key': key, 'limit': 1, 'rating': 'pg'}

        session = requests.Session()
        response = session.get("http://api.giphy.com/v1/gifs/search", params=payload)

        map = {}
        map = response.text
        # print response.text
        map = json.loads(map)

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(map)

        if len(map['data']) == 0:
            client_id = "fccd85bd2df2d1d"
            client_secret = "5d048f197e04703b1491995dcb8af50fd0ea34b5"

            client = ImgurClient(client_id, client_secret)
            items = client.get_album_images('NLqMb')

            link = items[random.randint(0, len(items) - 1)].link
            if (link.endswith('gif')):
                link = link.replace('.gif', '.gifv')
                return link

            return link

        url_string = map['data'][0]['images']['downsized']['url']

        return url_string

    def ask_for_joke(self):
        key = "dc6zaTOxFJmzC"
        headers = {'User-Agent': 'Mozilla/5.0 Ubuntu/8.10 Firefox/3.0.4'}
        payload = {'1': random.randint(1, 999)}

        session = requests.Session()
        response = session.get("http://www.randomjokegenerator.com/getJoke.php", params=payload)

        # print response.text
        # print response.text.replace("&joke=","")
        return response.text.replace("&joke=", "")

    def ask_for_dad_joke(self):
        key = "dc6zaTOxFJmzC"
        headers = {'User-Agent': 'Mozilla/5.0 Ubuntu/8.10 Firefox/3.0.4'}
        payload = {'a': 'j', 'lt': 'r', 'vj': '0,10'}

        session = requests.Session()
        response = session.post("http://www.dadjokegenerator.com/api/api.php", headers=headers, params=payload)

        print(response.text)

        map = {}
        map = response.text
        # print response.text
        map = json.loads(map)

        # print map[0]["SETUP"]
        # print "and"
        # print map[0]["PUNCHLINE"]

        # print response.text.replace("&joke=","")
        return map[0]

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
