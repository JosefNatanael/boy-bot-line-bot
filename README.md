# BoyBot

BoyBot is a LINE bot for cool kids. (I will spy your chat if you invite this bot).

# Installation
Installation guide

## MacOS and Linux
python3 -m venv env
pip install -r requirements.txt
source env/bin/activate

## Windows
py -m venv env
pip install -r requirements.txt
.\env\Scripts\activate

# Adding Image Reply

Go to chat folder, image_chat.json file
Enter key-value pairs
- key: image url (image needs to be less than 1MB)
- value: array of keyword triggers

# Adding Text Reply
Go to chat folder, text_chat.json file
Enter key-value pairs
 - key: reply text
 - value: array of keyword triggers

# Notes

- Still using development server
- Needs more refactor
