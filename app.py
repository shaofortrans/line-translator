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
        # 定義：如果裡面包含中文字符，就視為中文
        import re
        # 這是最暴力的正規表達式，專門抓中文字
        is_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
        
        if is_chinese:
            # 確定是中文 -> 翻成印尼文
            return GoogleTranslator(source='zh-TW', target='id').translate(text)
        else:
            # 不是中文 -> 翻成繁體中文
            raw = GoogleTranslator(source='auto', target='zh-TW').translate(text)
            return cc.convert(raw)
            
    except Exception as e:
        return f"報錯了：{str(e)}"
        
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
