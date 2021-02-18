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

import os

from linebot.models import *
from linebot.models.events import UnsendEvent
from linebot.exceptions import InvalidSignatureError

from flask import Flask, request, abort

import global_settings
import constants

from src.replier import Replier
from src.utilclasses import logger


app = Flask(__name__)

global_settings.init()
constants.init()

# Channel Access Token
line_bot_api = global_settings.line_bot_api

instant_resend = global_settings.instant_resend
superuser_mode = global_settings.superuser_mode


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        global_settings.handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@global_settings.handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    logger.notice(event)
    rep = Replier(event, mode="message")
    if "bbcon" in message.text[:5] and event.source.user_id == os.getenv("SUPERUSER_ID"):
        rep.start_message_process()
    elif "boybot" in message.text[:6]:
        rep.start_nonadmin_message_process()
    else:
        rep.save_to_db()
        replied = rep.simple_chat_bot_image_reply()
        if not replied:
            rep.simple_chat_bot_text_reply()


@global_settings.handler.add(UnsendEvent)
def handle_unsend(event):
    print(event)
    if instant_resend:
        Replier(event, mode="unsend")


@global_settings.handler.add(PostbackEvent)
def handle_postback(event):
    print(event)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
