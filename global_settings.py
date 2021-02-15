"""Global stuff"""
import os
import json

from pymongo import MongoClient
from linebot import (
    LineBotApi, WebhookHandler
)

from src.utilclasses import logger


def init():
    global client, db, line_bot_api, handler, instant_resend, superuser_mode, image_dict, text_dict

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

    # Image dict
    image_dict = load_image_dict()

    # Text dict
    text_dict = load_text_dict()


def load_image_dict():
    try:
        with open("./chat/image_chat.json") as f:
            return json.load(f)
    except Exception as exc:
        logger.exception(exc)
        return {}


def load_text_dict():
    try:
        with open("./chat/text_chat.json") as f:
            return json.load(f)
    except Exception as exc:
        logger.exception(exc)
        return {}
