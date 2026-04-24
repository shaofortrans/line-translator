import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from deep_translator import GoogleTranslator
from opencc import OpenCC

app = Flask(__name__)

# LINE 設定 (這些環境變數你原本就在 Render 設定好了，不用動)
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

# 初始化 OpenCC (s2twp: 簡轉繁 + 台灣用語修正)
cc = OpenCC('s2twp')

def get_translate(text):
    try:
        # 使用 Google 翻譯 (免 Key 穩定版)
        raw_translated = GoogleTranslator(source='auto', target='zh-TW').translate(text)
        # 轉換為台灣在地用語
        return cc.convert(raw_translated)
    except Exception as e:
        return f"翻譯出錯：{str(e)}"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    reply_text = get_translate(user_text)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run()
