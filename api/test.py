from crawler import MemeGeneratorPredisAI, text_preprocessing

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
        meme_url = Generator.genrate_meme(text)
        Generator.close()
        print(meme_url)
    else:
        print("字數過少")

if __name__ == "__main__":
    main()