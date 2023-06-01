from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction
from api.chatgpt import ChatGPT

# 函式註解
from typing import *

# 網路爬蟲
import requests
from time import sleep
from requests.exceptions import InvalidSchema ##here
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait

# from transformers import (
#    BertTokenizerFast,
#    AutoModelForMaskedLM,
#    AutoModelForCausalLM,
#    AutoModelForTokenClassification,
# )
# from ckip_transformers.nlp import CkipWordSegmenter

import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

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

# class MemeGeneratorPredisAI:
#     def __init__(self, url: str) -> None:
#         self.url = url

#         self.chrome_options = Options()
#         self.chrome_options.add_argument("--disable-gpu")

#         # 無頭模式
#         self.chrome_options.add_argument("--headless")
    
#     # 開啟瀏覽器
#     def open_webdriver(self) -> None:
#         # 初始化瀏覽器、設置智能等待
#         # 注意!!! implicitly_wait 不要設定得太短
#         self.driver = webdriver.Chrome('chromedriver', options = self.chrome_options)
#         self.driver.implicitly_wait(20)

#         # 開啟瀏覽器，並固定視窗大小
#         self.driver.get(self.url)
#         self.driver.set_window_size(1200, 800)
#         sleep(0.5)

#     def genrate_meme(self, text: str) -> None:
#         # 輸入情境文本
#         textarea = self.driver.find_element(By.CLASS_NAME, "MuiFilledInput-input")
#         textarea.send_keys(text)
#         sleep(0.5)
        
#         # 點擊 "GENERATE" 按鈕
#         btn_genrate = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[3]/div/div/div/div/div[2]/div[2]/button[2]")
#         btn_genrate.click()
#         sleep(15)

#         # 獲取圖片 url
#         img_url = self.driver.find_element(By.CLASS_NAME, "MuiAvatar-img").get_attribute("src")
#         print(img_url)

#     # 關閉瀏覽器
#     def close(self) -> None:
#         self.driver.quit()


# Function to send the message with the auto-appearing button
def handle_message(event):
    global working_status

    if event.message.type != "text":
        return
    

    if event.message.text == "啟動":
        working_status = True
        text_message = TextSendMessage(text="我是時下流行的AI智能，目前可以為您服務囉，歡迎來跟我互動~")
        line_bot_api.reply_message(
            event.reply_token,
            [text_message,send_auto_button_message()])
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
