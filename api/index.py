from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from api.chatgpt import ChatGPT

# from firebase_admin import storage

import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()


# def download_image(source_path: str, destination_path: str) -> None:
#     bucket = storage.bucket()

#     # 指定欲下載的檔案路徑
#     blob = bucket.blob(source_path)

#     # 下載檔案
#     blob.download_to_filename(destination_path)


# domain root
@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    
    if event.message.type != "text":
        return
    
    if event.message.text == "啟動":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我是時下流行的AI智能，目前可以為您服務囉，歡迎來跟我互動~"))
        return

    if event.message.text == "安靜":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="感謝您的使用，若需要我的服務，請跟我說 「啟動」 謝謝~"))
        return
    
    if event.message.text == "meme":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="開心果歡迎您~請寫一段話表達你現在的狀態，開心果將推薦您好笑的梗圖!"))
        return
    
    if event.message.text == "img":
        working_status = True

        # 下載完之後的位置
        # template_path = "./meme_template.png"
        # source_path = "meme_template/A train hitting a school bus.png"
        # download_image(source_path, template_path)

        img_url = "https://firebasestorage.googleapis.com/v0/b/fir-test-9907d.appspot.com/o/meme_template%2FAJ%20Styles%20%26%20Undertaker.png?alt=media&token=7910153b-fff3-4d2b-a1f2-ae40d508a23b&_gl=1*1qnypgh*_ga*MTQwMDk5MDE4LjE2ODQ2NDAxNjk.*_ga_CW55HF8NVT*MTY4NTU0OTE0MC40LjEuMTY4NTU0OTYzMS4wLjAuMA.."
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
        return
    
    if working_status:
        chatgpt.add_msg(f"Human:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))


if __name__ == "__main__":
    app.run()
