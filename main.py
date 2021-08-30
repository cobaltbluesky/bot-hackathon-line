from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, ImageMessage, TextMessage, TextSendMessage
)
import base64
import os
import random

app = Flask(__name__)

#環境変数取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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


@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):

    # イベントからメッセージidを取得
    message_id = event.message.id

    # 画像の中身を取得
    message_content = line_bot_api.get_message_content(message_id)

    #get_message_contentから取れるものが正体不明なので一旦.jpgにして開いてbase64に変換
    # 保存
    with open(Path(f"static/images/{message_id}.jpg").absolute(), "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="保存完了"))

    # 開く
    with open(f"static/images/{message_id}.jpg", "rb") as image_file:
        # base64に変換
        convertedImage = base64.b64encode(image_file.read())
        # バイナリ型を文字列に変換
        convertedImage_str = data.decode('utf-8')

    # 返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=convertedImage_str))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
