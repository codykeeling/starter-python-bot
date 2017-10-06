import json
import logging
import requests
import re
import urllib
import pprint
import random
from imgurpython import ImgurClient
import random

eloTypes = {'control':10,'clash':12,'supremacy':31,'survival':37,'countdown':38,'trials':39}

def hours_played(username):
    username = 'MoistTurtleneck'
    headers = {'User-Agent' :'Mozilla/5.0 Ubuntu/8.10 Firefox/3.0.4', 'Host':'api.guardian.gg', 'Accept':'application/json, text/plain,*/*',
               'Referer':'https://guardian.gg/2/profile/1/{0}'.format(username),'origin':'https://guardian.gg'}
    # headers = {'User-Agent' :'Mozilla/5.0 Ubuntu/8.10 Firefox/3.0.4', 'Host':'api.guardian.gg', 'Accept':'application/json, text/plain,*/*',
    #            'Referer':'https://guardian.gg/2/profile/1/GoGoGadgetChris','origin':'https://guardian.gg'}
    payload = {'console':'1','user':username}

    session = requests.Session()
    response = session.get("https://api.guardian.gg/v2/players/1/{0}?lc=en".format(username), headers=headers)
    # print response.text
    map = json.loads(response.text)
    # print map
    pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(map)
    mode = "control"
    if mode in eloTypes:
        try:
            elos = map['player']['stats']
            print elos
            controlElo = elos[next(index for (index, d) in enumerate(elos) if d["mode"] == eloTypes['control'])]
            print controlElo
            return controlElo
        except:
            return 0
    return "{0} is not an acceptable game mode (control,clash,supremacy,survival,countdown,trials)".format(mode)

elo = hours_played("moistturtleneck")
print elo