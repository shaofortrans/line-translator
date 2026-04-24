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
        # 我們直接偵測這段文字「最像」哪種語言
        # 這裡不需要 debug_tag 了，我們追求一次到位
        
        from deep_translator import GoogleTranslator
        
        # 建立一個偵測器（這不需要 Key）
        # 邏輯：如果你傳中文或英文，它會翻成印尼文 (id)
        #      如果你傳印尼文，它會翻成繁體中文 (zh-TW)
        
        # 我們先試著把它翻成繁體中文
        translated_to_zh = GoogleTranslator(source='auto', target='zh-TW').translate(text)
        
        # 如果翻譯出來的結果跟原本的一模一樣（代表原本就是中文）
        # 或者原本的文字裡有中文字，那我們就強制翻成印尼文
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
        
        if has_chinese:
            # 強制中翻印
            return GoogleTranslator(source='zh-CN', target='id').translate(text)
        else:
            # 可能是印尼文或英文 -> 翻成繁體中文
            return cc.convert(translated_to_zh)

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
