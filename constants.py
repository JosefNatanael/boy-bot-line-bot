"""Global stuff"""
import json

from src.utilclasses import logger


def init():
    global image_dict, text_dict

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
