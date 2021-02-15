# Copyright (C) 2021 Josef Natanael
# 
# This file is part of BoyBot LINE bot.
# 
# BoyBot LINE bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# BoyBot LINE bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with BoyBot LINE bot.  If not, see <http://www.gnu.org/licenses/>.
# 
# This copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.

"""Global stuff"""
import os

from pymongo import MongoClient
from linebot import (
    LineBotApi, WebhookHandler
)


def init():
    global client, db, line_bot_api, handler, instant_resend, superuser_mode

    # DB stuff
    client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
    db = client[os.getenv("MONGODB_DATABASE")]

    # Channel Access Token
    line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
    # Channel Secret
    handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))

    # Default bot settings
    instant_resend = True
    superuser_mode = True
