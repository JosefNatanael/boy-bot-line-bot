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
import json

from src.utilclasses import logger


def init():
    global image_dict, text_dict, emergency_button_image_url, emergency_meeting_image_url

    # Image dict
    image_dict = load_image_dict()

    # Text dict
    text_dict = load_text_dict()

    emergency_button_image_url = "https://i.imgur.com/HUb6Xvf.jpg"
    emergency_meeting_image_url = "https://i.imgur.com/3suoOpj.png"


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
