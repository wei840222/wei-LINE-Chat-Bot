import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError, InvalidSignatureError
from linebot.models import *
import msgSrc
import app


main = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('SECRET'))
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')


@main.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    main.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.push_message(event.source.user_id,
                              TextSendMessage(text='您好！我是 wei-bot\n很高興認識您！'))
    line_bot_api.push_message(event.source.user_id,
                              StickerSendMessage(package_id=1, sticker_id=5))
    line_bot_api.push_message(event.source.user_id, TextSendMessage(
        text='點擊下方選單了解更多資訊...\n輸入 指令 查詢所有指令。'))
    line_bot_api.push_message(event.source.user_id, TextSendMessage(
        text='使用說明：\nhttps://github.com/wei840222/Line-Bot-Self-introduction/blob/master/README.md'))


@handler.add(JoinEvent)
def handle_join(event):
    print('added a grp')
    line_bot_api.push_message(event.source.group_id, TextSendMessage(
        text='目前還不支援群組聊天功能喔!\n請大家透過以下網址或是掃描QRCode加入好友...'))
    line_bot_api.push_message(event.source.group_id, TextSendMessage(
        text='https://line.me/R/ti/p/%40qrc2059q'))
    line_bot_api.push_message(event.source.group_id, ImageSendMessage(
        original_content_url='https://qr-official.line.me/M/0QjC1ice-_.png', preview_image_url='https://qr-official.line.me/M/0QjC1ice-_.png'))
    line_bot_api.push_message(event.source.group_id,
                              StickerSendMessage(package_id=1, sticker_id=4))
    line_bot_api.leave_group(event.source.group_id)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # log #
    print("Handle: userId: " + event.source.user_id + ", reply_token: " +
          event.reply_token + ", message: " + event.message.text)
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
        print(profile.display_name)
        print(profile.user_id)
        print(profile.picture_url)
        print(profile.status_message)
    except LineBotApiError:
        print('can\'t get user profile')
    # log #

    # search key word in msgDict and reply
    for key in msgSrc.msgDict.keys():
        if key in event.message.text:
            line_bot_api.reply_message(event.reply_token, msgSrc.msgDict[key])
            return None

    # all cmd
    if '指令' in event.message.text:
        msg = ''
        for key in msgSrc.msgDict.keys():
            msg += key + ', '
        msg += '時間, 天氣, 新聞, 指令'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=msg))
        return None

    # Time App
    if '時間' in event.message.text:
        timeApp = app.Time()
        line_bot_api.reply_message(event.reply_token, timeApp.getTime())
        return None

    # Weather App
    if '天氣' in event.message.text:
        weatherApp = app.Weather(WEATHER_API_KEY)
        weatherMsg = weatherApp.getWeather(event.message.text)
        for msg in weatherMsg:
            line_bot_api.push_message(event.source.user_id, msg)
        return None

    # Apple News
    if '新聞' in event.message.text:
        newsApp = app.News()
        newsMsg = newsApp.getNews()
        for msg in newsMsg:
            line_bot_api.push_message(event.source.user_id, msg)
        return None

    # can't find any msg to reply
    line_bot_api.push_message(profile.user_id, TextSendMessage(
        text='我不了解「' + event.message.text + '」是什麼意思。'))


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # echo sticker
    print(event.message.package_id, event.message.sticker_id)
    try:
        line_bot_api.reply_message(event.reply_token, StickerSendMessage(
            package_id=event.message.package_id, sticker_id=event.message.sticker_id))
    except LineBotApiError:
        line_bot_api.push_message(
            event.source.user_id, TextSendMessage(text='我沒有這個貼圖QQ'))
        line_bot_api.push_message(
            event.source.user_id, StickerSendMessage(package_id=2, sticker_id=154))


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data in msgSrc.msgListDict.keys():
        for msg in msgSrc.msgListDict[event.postback.data]:
            line_bot_api.push_message(event.source.user_id, msg)


if __name__ == "__main__":
    main.run()
