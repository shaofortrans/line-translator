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

import time
import re

def get_translate(text):
    # 嘗試 3 次
    for i in range(3):
        try:
            # 判斷中文字的正則表達式
            is_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
            
            if is_chinese:
                # 中翻印
                res = GoogleTranslator(source='zh-TW', target='id').translate(text)
            else:
                # 印/英翻中
                raw = GoogleTranslator(source='auto', target='zh-TW').translate(text)
                res = cc.convert(raw)
            
            # 只要有拿到東西就回傳
            if res and len(res.strip()) > 0:
                return res
                
        except Exception as e:
            # 失敗了就等 0.5 秒再試，這時候伺服器可能正在變快
            print(f"嘗試第 {i+1} 次失敗...")
            time.sleep(0.5)
            continue
            
    # 如果 3 次都失敗，回傳一個特定的「喚醒中」訊息
    return "（機器人暖機中，請再試一次這句！）"
        
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
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    
    # 取得翻譯結果
    reply_text = get_translate(user_text)
    
    # 如果真的不幸連重試都失敗，回傳一個溫馨提示
    if not reply_text:
        reply_text = "抱歉，我剛睡醒腦袋還沒轉過來... 請再對我說一次！"
        
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
if __name__ == "__main__":
    app.run()
