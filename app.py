import os

from linebot.models import *
from linebot.models.events import UnsendEvent
from linebot.exceptions import InvalidSignatureError

from flask import Flask, request, abort

import global_settings

from src.replier import Replier
from src.utils import logger


app = Flask(__name__)

global_settings.init()

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
    logger(event)
    rep = Replier(event)
    if "bbcon" in message.text[:5] and event.source.user_id == os.getenv("SUPERUSER_ID"):
        rep.start_message_process()
    elif "boybot" in message.text[:6]:
        rep.start_nonadmin_message_process()
    else:
        rep.simple_chat_bot_image_push()
        rep.save_to_db()


@global_settings.handler.add(UnsendEvent)
def handle_unsend(event):
    print(event)
    if instant_resend:
        Replier(event, mode="unsend")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
