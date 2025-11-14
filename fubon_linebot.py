# line_bot_main.py
import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from linebot.exceptions import InvalidSignatureError

# 讀取 .env
def load_env(path=".env"):
    env = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

env = load_env()
CHANNEL_ACCESS_TOKEN = env.get("LINE_CHANNEL_ACCESS_TOKEN", "")
CHANNEL_SECRET = env.get("LINE_CHANNEL_SECRET", "")
PORT = int(env.get("PORT", "5000"))

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise SystemExit("請在 .env 設定 LINE_CHANNEL_ACCESS_TOKEN 與 LINE_CHANNEL_SECRET")

# 初始化 LINE SDK
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Flask
app = Flask(__name__)

# Webhook 入口
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# 關鍵字路由
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()

    if "富邦" in user_text or "展覽" in user_text:
        # 1) 執行你的爬蟲主程式，產出 Downloads/fubon_exhibitions.json
        from fubon_art_museum import main as fubon_crawler_main
        fubon_crawler_main()

        # 2) 讀取 JSON 結果
        downloads_path = os.path.join(os.getcwd(), "Downloads", "fubon_exhibitions.json")
        if not os.path.exists(downloads_path):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到展覽資料檔案。"))
            return

        with open(downloads_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 3) 組裝回覆（簡易文字 / Flex）
        on_now = data.get("on_now", [])
        if not on_now:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前沒有現正展出的資料。"))
            return

        # 簡易：只回第一筆
        first = on_now[0]
        text_reply = (
            f"{first['title']}\n"
            f"英文：{first['eng_title']}\n"
            f"日期：{first['date']}\n"
            f"地點：{first['location']}\n"
            f"連結：{first['link']}"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text_reply))
        return

    else:
        # 提示
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="輸入「富邦展覽」可以查看最新展覽資訊。"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)