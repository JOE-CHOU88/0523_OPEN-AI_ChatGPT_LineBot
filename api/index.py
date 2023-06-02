from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction
from api.chatgpt import ChatGPT


# 函式註解
from typing import *

# 網路爬蟲
# import requests
from threading import Thread
# from time import sleep
# from requests.exceptions import InvalidSchema
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.remote.webelement import WebElement
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait

from crawler import MemeGeneratorPredisAI, text_preprocessing

import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--headless")

def generate_meme(reply_token, message_text):
    # 對輸入文本進行預處理，回傳 List[str]
    text = text_preprocessing([message_text])
    URL = "https://predis.ai/free-ai-tools/ai-meme-generator/#"

    # 至少 4 個詞彙才會執行
    if len(text) >= 4:
        # 詞彙之間以空格做間隔
        text = " ".join(text)

        # 開始網路爬蟲
        Generator = MemeGeneratorPredisAI(URL)
        Generator.open_webdriver()
        meme_url = Generator.genrate_meme(text)
        Generator.close()

        image_message = ImageSendMessage(original_content_url=meme_url, preview_image_url=meme_url)
        line_bot_api.reply_message(
            reply_token,
            image_message
        )
    else:
        line_bot_api.reply_message(
            reply_token, 
            TextSendMessage(text="字數過少，請輸入至少 4 個詞彙")
        )

    # driver = webdriver.Chrome('chromedriver', options=chrome_options)
    # driver.get()  # Replace with the URL you want to open
    # # Perform actions with the WebDriver (e.g., fill forms, click buttons)
    # # You can interact with the page using driver.find_element, driver.click, etc.
    # # After the necessary actions, capture the screenshot or extract information from the page
    # screenshot_path = "screenshot.png"  # Replace with your desired screenshot path
    # driver.save_screenshot(screenshot_path)
    # driver.quit()

    # line_bot_api.reply_message(
    #     reply_token,
    #     TextSendMessage(text="Meme generated!")
    # )

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

# Function to send the message with the auto-appearing button
def handle_message(event):
    global working_status
    global gen_meme

    if event.message.type != "text":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="不好意思，我無法處理文字以外的請求，請確認您輸入的是文字，謝謝~"))
        return
    

    if event.message.text == "啟動":
        working_status = True
        gen_meme = False

        text_message = TextSendMessage(text="我是時下流行的AI智能，目前可以為您服務囉，歡迎來跟我互動~")
        line_bot_api.reply_message(
            event.reply_token,
            [text_message,send_auto_button_message()])
        return

    if event.message.text == "安靜":
        working_status = False
        gen_meme = False

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="感謝您的使用，若需要我的服務，請跟我說 「啟動」 謝謝~"))
        return
    
    if event.message.text == "meme":
        working_status = False
        gen_meme = True
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="開心果歡迎您~請寫一段話表達你現在的狀態，開心果將推薦您好笑的梗圖!"))
        
        # Start the meme generation in a background thread
        # meme_thread = Thread(target=generate_meme, args=(event.reply_token, event.message.text))
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(text="Meme generation in progress...")
        # )
        # meme_thread.start()
        return
    
    if event.message.text == "img":
        working_status = True

        img_url = "https://firebasestorage.googleapis.com/v0/b/fir-test-9907d.appspot.com/o/meme_template%2FAJ%20Styles%20%26%20Undertaker.png?alt=media&token=7910153b-fff3-4d2b-a1f2-ae40d508a23b&_gl=1*1qnypgh*_ga*MTQwMDk5MDE4LjE2ODQ2NDAxNjk.*_ga_CW55HF8NVT*MTY4NTU0OTE0MC40LjEuMTY4NTU0OTYzMS4wLjAuMA.."

        image_message = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
        text_message = TextSendMessage(text='This is a message with an image.')
        
        line_bot_api.reply_message(
            event.reply_token,
            [image_message,text_message,send_auto_button_message()])
        
        return
    
    if working_status:
        chatgpt.add_msg(f"Human:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        if event.message.text == "conversation":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="好的請說，我在聽~"))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                [TextSendMessage(text=reply_msg),send_auto_button_message()])
            
    if gen_meme:
        generate_meme(event.reply_token, event.message.text)

# 自動產生對話詢問是否要切換到meme模式
def send_auto_button_message():
    # Create alternative message actions
    action1 = MessageAction(label='迷因產生器', text='meme')
    action2 = MessageAction(label='正常對話', text='conversation')

    # Create quick reply buttons
    quick_reply_buttons = [
        QuickReplyButton(action=action1),
        QuickReplyButton(action=action2),
    ]

    # Create quick reply instance
    quick_reply = QuickReply(items=quick_reply_buttons)

    # Create the text message with alternatives
    message = TextSendMessage(
        text='還有什麼能為您服務的嗎?',
        quick_reply=quick_reply
    )

    return message

    # # Send the message with alternatives
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     message
    # )

if __name__ == "__main__":
    app.run()
