#!/usr/bin/env python

import logging
import os

from beepboop import resourcer
from beepboop import bot_manager

from slack_bot import SlackBot
from slack_bot import spawn_bot
from imgurpython import ImgurClient
import random

logger = logging.getLogger(__name__)


if __name__ == "__main__":

    # imgur client id and secret
    client_id = "fccd85bd2df2d1d"
    client_secret = "5d048f197e04703b1491995dcb8af50fd0ea34b5"

    client = ImgurClient(client_id, client_secret)
    items = client.get_album_images('NLqMb')

    print items[random.randint(0,len(items)-1)].link
    # print album
