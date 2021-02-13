from linebot.models import *
from linebot.exceptions import (
    InvalidSignatureError,
    LineBotApiError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from flask import Flask, request, abort
import os

from linebot.models.events import UnsendEvent
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
db = client[os.getenv("boybotdb")]
collection = db[os.getenv("boybotcollection")]


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
# Channel Secret
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))


class Replier:
    def __init__(self, event) -> None:
        self.event = event
        self.event_source_type = event.source.type
        self.message = event.message.text

    def start_process(self):
        try:
            if self.message == "bbcon leave":
                self.leave()
        except Exception as e:
            print(e)
            return False
        return True

    def leave(self) -> bool:
        try:
            if self.event_source_type == "room":
                line_bot_api.leave_room(self.event.source.room_id)
            elif self.event_source_type == "group":
                line_bot_api.leave_group(self.event.source.group_id)
            else:
                print("Nothing to leave")
        except LineBotApiError as e:
            print("Error leaving")
            return False
        return True


def save_to_db(message_text: str, source_user_id: str, message_timestamp: int) -> bool:
    """
    post interface:
    - message_text: string
    - source_user_id: string
    - message_timestamp: int
    """
    post = {
        "message_text": message_text,
        "source_user_id": source_user_id,
        "message_timestamp": message_timestamp
    }
    try:
        collection.insert_one(post)
    except Exception as exc:
        print(exc)
        return False
    return True


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    print(event)
    if "bbcon" in message.text[:5]:
        rep = Replier(event)
        rep.start_process()
    else:
        save_to_db(event.message.text, event.source.user_id, event.timestamp)
        line_bot_api.reply_message(event.reply_token, message)


@handler.add(UnsendEvent)
def handle_unsend(event):
    print(event)
    unsend_message_id = event.unsend.message_id
    message_content = line_bot_api.get_message_content(unsend_message_id)
    print(message_content.content_type)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
