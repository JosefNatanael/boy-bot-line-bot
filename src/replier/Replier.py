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
import datetime

from linebot.models import *
from linebot.exceptions import LineBotApiError

import pymongo

from src.utilclasses import logger
import global_settings
import constants


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
        try:
            if self.message == "bbcon leave":
                self.leave()
            elif self.message == "bbcon instant":
                global_settings.instant_resend = True
            elif self.message == "bbcon manual":
                global_settings.instant_resend = False
            elif self.message.startswith("bbcon resend"):
                self.resend()
            elif self.message == "bbcon enable superuser":
                global_settings.superuser_mode = True
            elif self.message == "bbcon disable superuser":
                global_settings.superuser_mode = False
        except Exception as e:
            logger.exception(e)
            return False
        return True

    def start_nonadmin_message_process(self):
        try:
            if self.message.startswith("boybot resend"):
                self.resend()
            elif self.message == "boybot help":
                self.show_help()
        except Exception as e:
            logger.exception(e)
            return False
        return True

    def start_unsend_process(self):
        if not global_settings.instant_resend:
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

                if unsend_source_user_id == os.getenv("SUPERUSER_ID") and global_settings.superuser_mode:
                    return True

                if self.event_source_type == "room":
                    profile = global_settings.line_bot_api.get_room_member_profile(
                        self.get_room_or_group_id(), unsend_source_user_id)
                    display_name = profile.display_name
                elif self.event_source_type == "group":
                    profile = global_settings.line_bot_api.get_group_member_profile(
                        self.get_room_or_group_id(), unsend_source_user_id)
                    display_name = profile.display_name
                else:
                    display_name = unsend_source_user_id

                message = f"{display_name} {dt}: {unsend_message}"
                global_settings.line_bot_api.push_message(
                    self.get_room_or_group_id(), TextSendMessage(text=message))
            else:
                print(
                    "Ambiguous unsend, probably unsent message is a bbcon command or non text")
        except Exception as e:
            logger.exception(e)
            return False
        return True

    def show_help(self):
        help_message = "Commands:\nboybot help\nboybot resend"
        try:
            global_settings.line_bot_api.reply_message(
                self.event.reply_token, TextSendMessage(text=help_message))
        except Exception as e:
            logger.exception(e)
            return False
        return True

    def leave(self) -> bool:
        try:
            if self.event_source_type == "room":
                global_settings.line_bot_api.leave_room(
                    self.event.source.room_id)
            elif self.event_source_type == "group":
                global_settings.line_bot_api.leave_group(
                    self.event.source.group_id)
            else:
                print("Nothing to leave")
        except LineBotApiError as e:
            logger.exception(e)
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
                if document['source_user_id'] == os.getenv("SUPERUSER_ID") and global_settings.superuser_mode:
                    continue

                if self.event_source_type == "room":
                    profile = global_settings.line_bot_api.get_room_member_profile(
                        room_or_group_id, document['source_user_id'])
                    display_name = profile.display_name
                elif self.event_source_type == "group":
                    profile = global_settings.line_bot_api.get_group_member_profile(
                        room_or_group_id, document['source_user_id'])
                    display_name = profile.display_name
                else:
                    display_name = document['source_user_id']

                resend_message += f"{display_name} {dt}: {document['message_text']}"
                resend_message += "\n----------\n"

            global_settings.line_bot_api.reply_message(
                self.event.reply_token, TextSendMessage(text=resend_message))
        except Exception as exc:
            logger.exception(exc)
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
            if collection_name not in global_settings.db.list_collection_names():
                global_settings.db.create_collection(
                    collection_name, capped=True, size=5000000, max=500)
            return global_settings.db[collection_name]
        except Exception as exc:
            logger.exception(exc)
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
            logger.exception(exc)
            return False
        return True

    def get_room_or_group_id(self):
        if self.event_source_type == "room":
            return self.event.source.room_id
        elif self.event_source_type == "group":
            return self.event.source.group_id

    def simple_chat_bot_image_reply(self) -> bool:
        """
        Return True if we reply with an image
        Return False otherwise
        """
        try:
            url = ""
            lower_message = self.message.lower()
            for img_url, keywords in constants.image_dict.items():
                for keyword in keywords:
                    if keyword in lower_message:
                        url = img_url
                        break
                else:
                    continue
                break

            if url == "":
                return False
            else:
                image_message = ImageSendMessage(
                    original_content_url=url,
                    preview_image_url=url
                )
                global_settings.line_bot_api.reply_message(
                    self.event.reply_token, image_message)
        except Exception as exc:
            logger.exception(exc)
            return False
        return True

    def simple_chat_bot_text_reply(self) -> bool:
        """
        Reply if received text message is EXACTLY a keyword in our keywords

        Return True if we reply with a text message
        Return False otherwise
        """
        try:
            text_message = ""
            clean_message = self.message.lower().strip()
            for reply_text, keywords in constants.text_dict.items():
                for keyword in keywords:
                    if keyword.strip() == clean_message:
                        text_message = reply_text
                        break
                else:
                    continue
                break

            if text_message == "":
                return False
            else:
                global_settings.line_bot_api.reply_message(
                    self.event.reply_token, TextSendMessage(text=text_message))
        except Exception as exc:
            logger.exception(exc)
            return False
        return True
