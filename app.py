from flask import Flask, request, abort

from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, ImageMessage, TextMessage, TextSendMessage
)

# メッセージをjsonに変換するやつ
from google.protobuf.json_format import MessageToJson

# Imports the Google Cloud client library
from google.cloud import vision

# 認証情報
from credentials import *

import os
import random
import json

app = Flask(__name__)

# Instantiates a client
client = vision.ImageAnnotatorClient()

# 画像の保存先
SRC_IMAGE_PATH = "static/images/{}.jpg"

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

    # src_image_pathを生成
    src_image_path = SRC_IMAGE_PATH.format(message_id)

    # 画像の中身を取得
    message_content = line_bot_api.get_message_content(message_id)

    #get_message_contentから取れるものが正体不明なので一旦.jpgにして開く
    # 保存
    with open(src_image_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    # 開く
    with open(src_image_path, "rb") as image_file:
        content = image_file.read()

    # 機械学習してるんやろ(適当)
    image = vision.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations

    # 返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=str(labels)))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
