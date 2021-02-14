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
import pymongo
from pymongo import MongoClient
import datetime
import random

client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
db = client[os.getenv("MONGODB_DATABASE")]


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
# Channel Secret
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))


instant_resend = False
superuser_mode = True


class Replier:
    def __init__(self, event, mode="message") -> None:
        """
            mode: string. "message" | "unsend"
            event_source_type. "room" | "group"
        """
        self.event = event
        self.event_source_type = event.source.type
        self.mode = mode
        if self.mode == "message":
            self.message = event.message.text
        elif self.mode == "unsend":
            self.start_unsend_process()

    def start_message_process(self):
        global instant_resend, superuser_mode
        try:
            if self.message == "bbcon leave":
                self.leave()
            elif self.message == "bbcon instant":
                instant_resend = True
            elif self.message == "bbcon manual":
                instant_resend = False
            elif self.message.startswith("bbcon resend"):
                self.resend()
            elif self.messsage == "bbcon enable superuser":
                superuser_mode = True
            elif self.message == "bbcon disable superuser":
                superuser_mode = False
        except Exception as e:
            print(e)
            return False
        return True

    def start_user_message_process(self):
        try:
            if self.message.startswith("boybot resend"):
                self.resend()
            elif self.message == "boybot help":
                self.show_help()
            elif self.message == "boybot stefanize":
                # self.stefanize()
                pass
            elif self.message == "boybot quote":
                pass
            elif self.message == "boybot prank":
                self.prank_stefan()
        except Exception as e:
            print(e)
            return False
        return True

    def start_unsend_process(self):
        if not instant_resend:
            return True
        try:
            unsend_message_id = self.event.unsend.message_id
            collection = self.get_collection()
            results_cursor = collection.find({"message_id": unsend_message_id})
            num_found = collection.count_documents(
                {"message_id": unsend_message_id})
            if num_found == 1:
                unsend_message = results_cursor[0]["message_text"]
                unsend_source_user_id = results_cursor[0]["source_user_id"]
                unsend_message_timestamp = results_cursor[0]["message_timestamp"]
                # Add 8 hours in milliseconds (+ 28,800,000)
                dt = datetime.datetime.fromtimestamp(
                    (unsend_message_timestamp + 28800000) / 1000.0).isoformat(" ", "seconds")

                if unsend_message_id == os.getenv("SUPERUSER_ID") and superuser_mode:
                    return True
                if unsend_message_id == "U02f47026e6e0afb8edb4b262e6308a8f":    # user id stefan
                    self.prank_stefan()

                if self.event_source_type == "room":
                    profile = line_bot_api.get_room_member_profile(
                        self.get_room_or_group_id(), unsend_source_user_id)
                    display_name = profile.display_name
                elif self.event_source_type == "group":
                    profile = line_bot_api.get_group_member_profile(
                        self.get_room_or_group_id(), unsend_source_user_id)
                    display_name = profile.display_name
                else:
                    display_name = unsend_source_user_id

                message = f"{display_name} {dt}: {unsend_message}"
                line_bot_api.push_message(
                    self.get_room_or_group_id(), TextSendMessage(text=message))
            else:
                print(
                    "Ambiguous unsend, probably unsent message is a bbcon command or non text")
        except Exception as e:
            print(e)
            return False
        return True

    def show_help(self):
        help_message = "Commands:\nboybot help\nboybot resend\nboybot stefanize\nboybot quote\nboybot prank"
        try:
            line_bot_api.reply_message(
                self.event.reply_token, TextSendMessage(text=help_message))
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

    def resend(self) -> bool:
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            message_args = self.message.split()
            if len(message_args) == 3:
                user_arg = int(message_args[2])

            num_to_resend = min(
                collection.count_documents({}), user_arg)
            resend_message = ""
            room_or_group_id = self.get_room_or_group_id()

            for document in collection.find().sort("_id", pymongo.DESCENDING)[:num_to_resend]:
                # Add 8 hours in milliseconds (+ 28,800,000)
                dt = datetime.datetime.fromtimestamp(
                    (document['message_timestamp'] + 28800000) / 1000.0).isoformat(" ", "seconds")
                if document['source_user_id'] == os.getenv("SUPERUSER_ID") and superuser_mode:
                    continue

                if self.event_source_type == "room":
                    profile = line_bot_api.get_room_member_profile(
                        room_or_group_id, document['source_user_id'])
                    display_name = profile.display_name
                elif self.event_source_type == "group":
                    profile = line_bot_api.get_group_member_profile(
                        room_or_group_id, document['source_user_id'])
                    display_name = profile.display_name
                else:
                    display_name = document['source_user_id']

                resend_message += f"{display_name} {dt}: {document['message_text']}"
                resend_message += "\n----------\n"

            line_bot_api.reply_message(
                self.event.reply_token, TextSendMessage(text=resend_message))
        except Exception as exc:
            print(exc)
            return False
        return True

    def get_collection(self):
        try:
            # Find corresponding collection name from room id or group id or default
            collection_name = ""
            if self.event_source_type == "room":
                collection_name = self.event.source.room_id
            elif self.event_source_type == "group":
                collection_name = self.event.source.group_id
            else:
                collection_name = os.getenv("MONGODB_COLLECTION")

            # Return collection from collection name, create new capped collection if does not exist
            if collection_name not in db.list_collection_names():
                db.create_collection(
                    collection_name, capped=True, size=5000000, max=500)
            return db[collection_name]
        except Exception as exc:
            print(exc)
            return None

    def save_to_db(self):
        post = {
            "message_id": self.event.message.id,
            "message_text": self.event.message.text,
            "source_user_id": self.event.source.user_id,
            "message_timestamp": self.event.timestamp
        }
        try:
            collection = self.get_collection()
            if collection is None:
                return False
            collection.insert_one(post)
        except Exception as exc:
            print(exc)
            return False
        return True

    def get_room_or_group_id(self):
        if self.event_source_type == "room":
            return self.event.source.room_id
        elif self.event_source_type == "group":
            return self.event.source.group_id

    def prank_stefan(self):
        image_links = [
            "https://i.imgur.com/RuHNWgi.jpg",
            "https://i.imgur.com/Z6iFmBa.jpg",
            "https://i.imgur.com/6JabrpZ.jpg",
            "https://i.imgur.com/734wN2R.jpg"
        ]
        selected_index = random.randint(0, len(image_links) - 1)
        image_message = ImageSendMessage(
            original_content_url=image_links[selected_index],
            preview_image_url=image_links[selected_index]
        )
        line_bot_api.push_message(
            self.get_room_or_group_id(), image_message)


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
    rep = Replier(event)
    if "bbcon" in message.text[:5] and event.source.user_id == os.getenv("SUPERUSER_ID"):
        rep.start_message_process()
    elif "boybot" in message.text[:6]:
        rep.start_user_message_process()
    else:
        rep.save_to_db()


@handler.add(UnsendEvent)
def handle_unsend(event):
    print(event)
    if instant_resend:
        rep = Replier(event, mode="unsend")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
