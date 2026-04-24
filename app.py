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
        # 1. 先偵測語言 (或是簡單判斷：如果裡面有中文，目標就是印尼文)
        # 我們用一個簡單的邏輯：如果有中文字，就翻印尼語
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
        
        if has_chinese:
            # 中文 -> 印尼文
            translated = GoogleTranslator(source='auto', target='id').translate(text)
            return translated
        else:
            # 其他語言 -> 繁體中文
            raw_translated = GoogleTranslator(source='auto', target='zh-TW').translate(text)
            # 依然加上 OpenCC 確保台灣用語習慣
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
