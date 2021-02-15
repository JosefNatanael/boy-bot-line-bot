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
