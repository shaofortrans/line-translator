from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai

# ====== 你的金鑰 ======
LINE_CHANNEL_ACCESS_TOKEN = "cptrgr1pmub3Yl765OhATEF12kPACiEGUG0C6E1UFSRCi5ca1m8Hq40Odc1ssmyi7Q5BOavK7uZ/hftXbJL+6nRCQGXRvYAprF4Vx4jwUtYfbcTzaY+9zTRjiVeE1QkpAI1xk3RMdnQ+UK6bPZuQcQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "bf4c37f1323066edae7b010679cb9994"
GEMINI_API_KEY = "AIzaSyCPzNVbAH309c1wEyWrufQJRZ7mnX3swN8"

# ====== 初始化 ======
app = Flask(__name__)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ====== Webhook ======
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

try:
        # 這邊是原本的 handler.handle 內容
        handler.handle(body, signature)
except Exception as e:
        # 這邊是處理錯誤的內容，必須跟 try 對齊
        print("Gemini錯誤:", e)
        if "quota" in str(e).lower():
            reply = "今天額度用完了 🥰"
        else:
            reply = "翻譯失敗"

return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    prompt = f"""
請把下面句子翻成另一種語言：
- 中文 → 印尼文
- 印尼文 → 中文
只輸出翻譯結果

{text}
"""

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
    except Exception as e:
        print("Gemini錯誤:", e)
        if "quota" in str(e).lower():
            reply = "今天額度用完了😅"
        else:
            reply = "翻譯失敗"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )
