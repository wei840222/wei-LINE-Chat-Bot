import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from msgProcess import *


app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('SECRET'))


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
    # log #
    print("Handle: userId: " + event.source.user_id + ", reply_token: " + event.reply_token + ", message: " + event.message.text)
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
        print(profile.display_name)
        print(profile.user_id)
        print(profile.picture_url)
        print(profile.status_message)
    except LineBotApiError as e:
        print('can\'t get user profile')
    # log #

    msg = event.message.text
    pm = profileMenu(profile, line_bot_api)
    if pm.isMenuOption(msg):
        pm.chooseMenuOption(msg)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='我不了解' + msg + '是什麼意思。'))


if __name__ == "__main__":
    app.run()
