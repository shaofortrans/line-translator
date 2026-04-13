import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai

app = Flask(__name__)

# ====== 設定區 (請確保留原本的 Key) ======
line_bot_api = LineBotApi("cptrgr1pmub3Yl765OhATEF12kPACiEGUG0C6E1UFSRCi5ca1m8Hq40Odc1ssmyi7Q5BOavK7uZ/hftXbJL+6nRCQGXRvYAprF4Vx4jwUtYfbcTzaY+9zTRjiVeE1QkpAI1xk3RMdnQ+UK6bPZuQcQdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("bf4c37f1323066edae7b010679cb9994")
genai.configure(api_key="AIzaSyCPzNVbAH309c1wEyWrufQJRZ7mnX3swN8")

# 修改點：直接寫名字，不要加 models/ 也不要加 v1beta
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Webhook錯誤: {e}")
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    try:
        # 呼叫 Gemini
        response = model.generate_content(f"請將以下內容翻譯成中文：{user_text}")
        reply_text = response.text
    except Exception as e:
        # 回傳詳細錯誤，讓我們知道現在跑的是哪一版
        reply_text = f"連線成功但Gemini報錯：{str(e)}"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run()
