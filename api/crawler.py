# 函式註解
from typing import *

# 網路爬蟲
import requests
from time import sleep
from requests.exceptions import InvalidSchema
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from transformers import (
   BertTokenizerFast,
   AutoModelForMaskedLM,
   AutoModelForCausalLM,
   AutoModelForTokenClassification,
)
from ckip_transformers.nlp import CkipWordSegmenter

class MemeGeneratorPredisAI:
    def __init__(self, url: str) -> None:
        self.url = url

        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-gpu")

        # 無頭模式
        self.chrome_options.add_argument("--headless")
    
    # 開啟瀏覽器
    def open_webdriver(self) -> None:
        # 初始化瀏覽器、設置智能等待
        # 注意!!! implicitly_wait 不要設定得太短
        self.driver = webdriver.Chrome('chromedriver', options = self.chrome_options)
        self.driver.implicitly_wait(20)

        # 開啟瀏覽器，並固定視窗大小
        self.driver.get(self.url)
        self.driver.set_window_size(1200, 800)
        sleep(0.5)

    def genrate_meme(self, text: str) -> None:
        # 輸入情境文本
        textarea = self.driver.find_element(By.CLASS_NAME, "MuiFilledInput-input")
        textarea.send_keys(text)
        sleep(0.5)
        
        # 點擊 "GENERATE" 按鈕
        btn_genrate = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[3]/div/div/div/div/div[2]/div[2]/button[2]")
        btn_genrate.click()
        sleep(15)

        # 獲取圖片 url
        img_url = self.driver.find_element(By.CLASS_NAME, "MuiAvatar-img").get_attribute("src")
        print(img_url)

    # 關閉瀏覽器
    def close(self) -> None:
        self.driver.quit()

def text_preprocessing(text: List[str]) -> List[str]:
    # 以下三種模型擇一
    # masked language model (ALBERT, BERT)
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')
    model = AutoModelForMaskedLM.from_pretrained('ckiplab/albert-tiny-chinese') # or other models above

    # casual language model (GPT2)
    # tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')
    # model = AutoModelForCausalLM.from_pretrained('ckiplab/gpt2-base-chinese') # or other models above

    # nlp task model
    # tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')
    # model = AutoModelForTokenClassification.from_pretrained('ckiplab/albert-tiny-chinese-ws') # or other models above


    # Initialize drivers
    # tokenizer
    ws_driver = CkipWordSegmenter(model = "bert-base")

    # 斷詞
    ws_result = ws_driver(text)

    # 回傳斷詞結果，list[str]
    return ws_result[0]

def main():
    text = "你們抓捕周樹人跟我魯迅有甚麼關係"
    url = "https://predis.ai/free-ai-tools/ai-meme-generator/#"
    
    # 對輸入文本進行預處理，回傳 List[str]
    text = text_preprocessing([text])

    # 至少 4 個詞彙才會執行
    if len(text) >= 4:
        # 詞彙之間以空格做間隔
        text = " ".join(text)

        # 開始網路爬蟲
        Generator = MemeGeneratorPredisAI(url)
        Generator.open_webdriver()
        Generator.genrate_meme(text)
        Generator.close()
    else:
        print("字數過少")

if __name__ == "__main__":
    main()