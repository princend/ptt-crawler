import time
import requests
import pandas
from bs4 import BeautifulSoup
import sys
import os
from dotenv import load_dotenv
import datetime
import json
load_dotenv()
print(os.getenv("Test"))

from dotenv import dotenv_values
config = dotenv_values(".env")
print(config['Test'])

"""
    變數準備
"""
# 目標網址
target_url = "https://www.ptt.cc/bbs/"

# 目標看板
target_board = "Tech_Job"

#目標頁面
target_page = "/index"

#目標頁數
page_num = ""

#頁面附屬檔名
page_ext = ".html"

target = target_url + target_board + target_page + page_num  + page_ext

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}

# 常數
# 目標網址
TARGET_URL = "https://www.ptt.cc/bbs/"
# 目標頁面
TARGET_PAGE = "/index"
# 頁面附屬檔名
PAGE_EXT = ".html"
# Requests 請求標頭
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64;x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}


def parser_board_urls(requests_):
    # 傳入 request_ 並解析成 bs4 物件
    html_code = BeautifulSoup(requests_.content, features="html.parser")
    div_list = html_code.find_all('div', class_='title')
   
    urls = []
    for div_ in div_list:
        try:
            a_tag = div_.find('a').attrs['href']
        except:
            a_tag = None
        urls.append(a_tag)
    return urls


def parser_article_content(url_list):
    ptt_data = []
    for url_ in url_list:
        if url_ != None:
            article_url = 'https://www.ptt.cc' + url_
            page_data = download_html(article_url, headers)
            page_html_code = BeautifulSoup(page_data.content, features="html.parser")
            try:
                article_data = page_html_code.find_all('span', class_="article-meta-value")
                article_author = article_data[0].contents[0]
                article_title = article_data[2].contents[0]
                article_time = article_data[3].contents[0]
                article_body = page_html_code.find('div', id='main-content').contents[4]
                article_row = {
                    'url': article_url,
                    'title': article_title,
                    'author': article_author,
                    'time': article_time,
                    'content': article_body
                }
                ptt_data.append(article_row)
            except:
                print("parser error:", article_url)
   
    time.sleep(1)
    return ptt_data

def download_html(target,headers):
    return  requests.get(target, headers= headers)


def export_json(data):
    ptt_df = pandas.DataFrame(data)
    ptt_df.to_json("ptt.json")
    return True

## Test
# a = download_html(target, headers)
# b = parser_board_urls(a)
# c = parser_article_content(b)
# export_json(c)
# print(c)
def send_line_notify(msg = "傳輸訊息"):
    line_notify_url = "https://notify-api.line.me/api/notify"
    line_notify_token = os.getenv("Token")
   
    # Line Auth Header
    line_notify_header = {
        'Authorization': 'Bearer {}'.format(line_notify_token)
    }
   
    # Line Message
    line_notify_body = {
        'message':  msg
    }
   
    res = requests.post(line_notify_url, headers=line_notify_header, data = line_notify_body)
    res_msg =  json.loads(res.text)


    return res_msg['status']


def main():
    print("接收參數的長度:", len(sys.argv))
    if len(sys.argv) < 2:
        print("缺少參數: 爬蟲的目標看板")
        sys.exit()
    else:
        if len(sys.argv) == 2:
            page_num = ""
            print("未偵測到目標頁數，因此只進行最新文章頁面進行爬蟲")
        else:
            page_num = sys.argv[2]
       
        target_board = sys.argv[1]
       
        # 合併目標網址
        target = TARGET_URL + target_board + TARGET_PAGE + page_num  + PAGE_EXT
        print(target)
       
        '''爬蟲執行順序
            download_html() -> parser_board_urls() -> parser_article_content() -> export_json()
           
            download_html: arg1: 網址, arg2: 請求標頭, returns: requests class
            parser_board_urls: arg1: request class, returns: (list) urls
            parser_article_content: arg1: (list) urls, return: (list) ppt_data
            export_json: arg1: (list) ppt_data, return: (Boolean) True, Output: ppt.json
        '''
        # 爬蟲主程式
        res = download_html(target, HEADERS)
        url_list = parser_board_urls(res)
        ptt_data = parser_article_content(url_list)
        export_json(ptt_data)
       
        # 發動訊息
        time_str = "{date:%Y-%m-%d %H:%M:%S}".format(date=datetime.datetime.now())
        process_st = send_line_notify("{} - 看板{} 爬蟲已完成".format(time_str, target_board))
        if process_st == 200:
            print("Line Notify 通知完成。")
        else:
            print("Line Notify API Error")
       
       
    return None




if __name__=='__main__':
    main()


# send_line_notify()