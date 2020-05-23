
# coding: utf-8

# In[ ]:


# get_ipython().system('pip install flask')
# get_ipython().system('pip install line-bot-sdk')


# In[ ]:


'''

整體功能描述

應用伺服器主結構樣板
    用來定義使用者傳送消息時，應該傳到哪些方法上
        比如收到文字消息時，轉送到文字專屬處理方法

消息專屬方法定義
    當收到文字消息，從資料夾內提取消息，並進行回傳。
    
啟動應用伺服器    

'''


# In[ ]:


'''

Application 主架構

'''

# 引用Web Server套件
from flask import Flask, request, abort

# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)

# 載入json處理套件
import json

# 載入基礎設定檔
secretFileContentJson=json.load(open("./line_secret_key",'r',encoding='utf8'))

# 設定Server啟用細節
app = Flask(__name__,static_url_path = "/material" , static_folder = "./material/")

# 生成實體物件
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
handler = WebhookHandler(secretFileContentJson.get("secret_key"))

# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
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


# In[ ]:


'''

消息判斷器

讀取指定的json檔案後，把json解析成不同格式的SendMessage

讀取檔案，
把內容轉換成json
將json轉換成消息
放回array中，並把array傳出。

'''

# 引用會用到的套件
from linebot.models import (
    ImagemapSendMessage,TextSendMessage,ImageSendMessage,LocationSendMessage,FlexSendMessage,VideoSendMessage
)

from linebot.models.template import (
    ButtonsTemplate,CarouselTemplate,ConfirmTemplate,ImageCarouselTemplate
    
)

from linebot.models.template import *

def detect_json_array_to_new_message_array(fileName):
    
    #開啟檔案，轉成json
    with open(fileName,'r',encoding='utf8') as f:
        jsonArray = json.load(f)
    
    # 解析json
    returnArray = []
    for jsonObject in jsonArray:

        # 讀取其用來判斷的元件
        message_type = jsonObject.get('type')
        
        # 轉換
        if message_type == 'text':
            returnArray.append(TextSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'imagemap':
            returnArray.append(ImagemapSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'template':
            returnArray.append(TemplateSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'image':
            returnArray.append(ImageSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'sticker':
            returnArray.append(StickerSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'audio':
            returnArray.append(AudioSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'location':
            returnArray.append(LocationSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'flex':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'video':
            returnArray.append(VideoSendMessage.new_from_json_dict(jsonObject))    


    # 回傳
    return returnArray


# In[ ]:









'''

handler處理關注消息

用戶關注時，讀取 素材 -> 關注 -> reply.json

將其轉換成可寄發的消息，傳回給Line

'''

# 引用套件
from linebot.models import (
    FollowEvent
)

# 引用套件
from linebot.models import (
    FollowEvent
)
import boto3, os

# 關注事件處理
@handler.add(FollowEvent)
def process_follow_event(event):
    print(os.listdir("./"))
    print(os.listdir("../"))
#     print(os.path.dirname(file_path))

    
    if (os.path.exists("./datas/"+event.source.user_id+".txt")) == False:
            
        s3 = boto3.client(
            's3',
            aws_access_key_id="AKIAR4NDUH53GWDLQFNM",
            aws_secret_access_key="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"
        )

        s3.download_file('iii-tutorial-v2', "student12/123.txt", "./datas/"+event.source.user_id+".txt")
        print("success")
    else:
        with open('./datas/'+event.source.user_id+'.txt', 'w') as fd:
            fd.write(" ")
    # 讀取並轉換
    result_message_array =[]
    replyJsonPath = "material/follow/reply.json"
    result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

    # 消息發送
    line_bot_api.reply_message(
        event.reply_token,
        result_message_array
    )

    # 從follow資料夾內，取出圖文選單id，並告知line，綁定用戶
#     linkRichMenuId = open("material/follow/rich_menu_id", 'r').read()
#     line_bot_api.link_rich_menu_to_user(event.source.user_id, linkRichMenuId)
    


# In[ ]:


'''

handler處理文字消息

收到用戶回應的文字消息，
按文字消息內容，往素材資料夾中，找尋以該內容命名的資料夾，讀取裡面的reply.json

轉譯json後，將消息回傳給用戶

'''


import sys
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC

        
# 引用套件
from linebot.models import (
    MessageEvent, TextMessage
)

# 文字消息處理
@handler.add(MessageEvent,message=TextMessage)
def process_text_message(event):
    
    data_list=[]
    reply_list = event.message.text.split("-")
    score_list=[]
#     print(event.message.text)
    if event.message.text == "登登登登~~~":
        
        line_bot_api.reply_message(
            event.reply_token,
            template_message_dict.get(event.message.text)
            )
    elif event.message.text == "p1":
        
        
        
        # 讀取本地檔案，並轉譯成消息
        result_message_array =[]
        replyJsonPath = "material/007_末章_突如其來的結局/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        # 發送
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )       
    elif event.message.text == "p2":
                     
        # 讀取本地檔案，並轉譯成消息
        result_message_array =[]
        replyJsonPath = "material/009_stairs2/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        # 發送
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )       
    elif reply_list[0] == "紀錄":
        
        with open('./datas/'+event.source.user_id+'.txt', 'r') as fd:
                data = fd.read()
                # 字串分割
                data_list = data.split(" ")
                
                for d in data_list:
                    if d != "":
                        score_list.append(int(d))
                    
                score = sum(score_list)

        
        #pass
        #GDriveJSON就輸入下載下來Json檔名稱
        #GSpreadSheet是google試算表名稱
        GDriveJSON = 'mindful-backup-274916-0fc3ca9531ab.json'
        GSpreadSheet = 'Bot_test'
#         print("1")
        while True:
            try:
#                 print("2")
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                key = SAC.from_json_keyfile_name(GDriveJSON, scope)
                gc = gspread.authorize(key)
                worksheet = gc.open(GSpreadSheet).sheet1
#                 sheet = gss_client.open_by_key(spreadsheet_key).sheet2
#                 worksheet2 = gc.open(GSpreadSheet)
#                 worksheet = gc.add_worksheet(title="A worksheet", rows="100", cols="20")
#                 sheet = gc.open(GSpreadSheet).worksheet("test")
#                 worksheet = gc.open(GSpreadSheet)
#                 try:
#                     worksheet.add_worksheet(title=event.source.user_id, rows="1", cols="26")
#                 except Exception as ex:
#                     worksheet = gc.open(GSpreadSheet).worksheet(event.source.user_id)
# #                 return worksheet
            except Exception as ex:
                print('無法連線Google試算表', ex)
                sys.exit(1)
#             print("3")
            textt=""
            textt+=reply_list[1]
            print(textt)
            if textt!="":
#                 print("4")
                worksheet.append_row((datetime.datetime.now().isoformat(), event.source.user_id,textt , str(score)))
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="成功上傳至Google sheet"))
#                 print("5")
                print('新增一列資料到試算表' ,GSpreadSheet)
                return textt       
    else:
        # 讀取本地檔案，並轉譯成消息
        result_message_array =[]
        replyJsonPath = "material/"+event.message.text+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        # 發送
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    
# In[ ]:

# 猜拳函數

def play_pss(a, b, win, lose, tie):
    if a == b:
        print("tie")
        tie = 1

    elif a == 1:
        if b == 3:
            print("You win")
            win = 1

        else:
            print("You lose")
            lose = 1
 
    elif a == 2:
        if b == 1:
            print("You win")
            win = 1
        else:
            print("You lose")
            lose = 1
 
    elif a == 3:
        if b == 2:
            print("You win")
            win = 1

        else:
            print("You lose")
            lose = 1

    else:
        print("輸入錯誤")

    return win, lose ,tie


'''

handler處理Postback Event

載入功能選單與啟動特殊功能

解析postback的data，並按照data欄位判斷處理

現有三個欄位
menu, folder, tag

若folder欄位有值，則
    讀取其reply.json，轉譯成消息，並發送

若menu欄位有值，則
    讀取其rich_menu_id，並取得用戶id，將用戶與選單綁定
    讀取其reply.json，轉譯成消息，並發送

'''
from linebot.models import (
    PostbackEvent
)

from urllib.parse import parse_qs 

import random
# s = 0
win = 0 
lose = 0 
tie = 0
tr = 0
stair = 10




@handler.add(PostbackEvent)
def process_postback_event(event):
    
    query_string_dict = parse_qs(event.postback.data)
    
    
    
#     print(query_string_dict.get('folder')[0])
#     print(query_string_dict.get('folder')[1])
    print(query_string_dict)
    if 'folder' in query_string_dict:
        
      
        if query_string_dict.get('folder')[0] == "follow":
        
            with open('./datas/'+event.source.user_id+'.txt', 'a') as fd:
                fd.write("1"+" ")
        
        result_message_array =[]

        replyJsonPath = 'material/'+query_string_dict.get('folder')[0]+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
  
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    elif 'menu' in query_string_dict:
 
        linkRichMenuId = open("material/"+query_string_dict.get('menu')[0]+'/rich_menu_id', 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
        
        replyJsonPath = 'material/'+query_string_dict.get('menu')[0]+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
  
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    elif 'map' in query_string_dict:

        linkRichMenuId = open("material/map_all/"+query_string_dict.get('map')[0]+'/rich_menu_id', 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
        
        replyJsonPath = 'material/map_all/'+query_string_dict.get('map')[0]+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
  
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    elif 'stair' in query_string_dict:
        result_message_array =[]
        global a
#         s += 1
#         a = "已經爬了"+str(s)+"層囉!"
        a = query_string_dict.get('stair')[1]
        print(a)
#         r = random.randint(1, 5)

        
        if a == "10":
            replyJsonPath = 'material/010_終章_享用勝利的喜悅/reply.json'
            result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
        
            
            line_bot_api.reply_message(
                event.reply_token,
                result_message_array)
            

        else:
            replyJsonPath = 'material/stair_all/'+ a +"/reply.json"
            result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
#             print("???")
            
            line_bot_api.reply_message(
                event.reply_token,
                result_message_array)
        
    elif 'pss' in query_string_dict:
#         pass
    
        r1 = random.randint(1, 3)
        result_message_array =[]
        
        replyJsonPath = 'material/pss/'+ str(r1) +"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        line_bot_api.reply_message(
            event.reply_token,
            result_message_array)
            
    elif 'play' in query_string_dict:
        
        global win,lose,tie
#         pass
        me = query_string_dict.get('play')[0]
        r = random.randint(1,3)
        
        if me == "剪刀":
            me_int = 1
        elif me == "石頭":
            me_int = 2
        elif me == "布":
            me_int = 3
            
        print(me_int)
        print(r)
            
        win, lose ,tie = play_pss(me_int, r, win, lose, tie)
        
        print(win)
        print(lose)
        print(tie)
        
#         with open('./datas/'+event.source.user_id+'.txt', 'a') as fd:
#             fd.write(str(0) + " ")
        
        if win == 1:
            result_message_array =[]
        
            replyJsonPath = 'material/pss_win/reply.json'
            result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

            line_bot_api.reply_message(
                event.reply_token,
                result_message_array)
            
        elif lose == 1:
#             r1 = random.randint(1, 3)
            result_message_array =[]

            replyJsonPath = 'material/pss_lose/reply.json'
            result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

            line_bot_api.reply_message(
                event.reply_token,
                result_message_array)
        elif tie == 1:
#             r1 = random.randint(1, 3)
            result_message_array =[]

            replyJsonPath = 'material/pss_tie/reply.json'
            result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

            line_bot_api.reply_message(
                event.reply_token,
                result_message_array)
        win = 0 
        lose = 0 
        tie = 0

        
# StickerSendMessage
from linebot.models import (
    StickerMessage
)


@handler.add(MessageEvent, message=StickerMessage)
def handle_message(event):

        result_message_array =[]

        replyJsonPath = 'material/010_終章_享用勝利的喜悅/reply.json'
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        line_bot_api.reply_message(
            event.reply_token,
            result_message_array)


# In[ ]:

'''

Flex Message 

Bubble的原稿Json

開發者以後可將Bubble類型的Flex消息Json，對此處進行更換。

'''

flexBubbleContainerJsonString ="""
{
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "https://i.imgur.com/xUCoqJ2.jpg",
    "size": "full",
    "aspectRatio": "20:13",
    "aspectMode": "cover"
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "莫名其妙一直重生的異世界",
        "weight": "bold",
        "size": "md",
        "style": "normal",
        "decoration": "none"
      },
      {
        "type": "separator",
        "margin": "xxl"
      },
      {
        "type": "box",
        "layout": "vertical",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "icon",
                "size": "sm",
                "url": "https://resources.help.salesforce.com/images/a23ba039a82d443506afb146032325ce.png"
              },
              {
                "type": "text",
                "text": "遊戲大綱",
                "size": "sm",
                "flex": 1,
                "color": "#4169E1",
                "weight": "bold",
                "action": {
                  "type": "uri",
                  "label": "action",
                  "uri": "https://i.imgur.com/WRyZ7aJ.jpg"
                }
              },
              {
                "type": "icon",
                "size": "sm",
                "url": "https://resources.help.salesforce.com/images/887762a63e7c8e14b4b817db352e65ce.png"
              },
              {
                "type": "text",
                "text": "Google Sheet",
                "size": "sm",
                "flex": 1,
                "wrap": true,
                "position": "relative",
                "align": "start",
                "action": {
                  "type": "uri",
                  "label": "action",
                  "uri": "https://docs.google.com/spreadsheets/d/1yjsEqXjtkDJ0rBFND_E2RbdmaauV4bf2id9cnmy7H9I/edit"
                },
                "color": "#4169E1",
                "weight": "bold"
              }
            ]
          }
        ]
      },
      {
        "type": "box",
        "layout": "vertical",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "icon",
                "size": "sm",
                "url": "https://resources.help.salesforce.com/images/887762a63e7c8e14b4b817db352e65ce.png"
              },
              {
                "type": "text",
                "text": "作者勉勵",
                "size": "sm",
                "flex": 1,
                "action": {
                  "type": "uri",
                  "label": "action",
                  "uri": "https://i.imgur.com/7STMKec.png"
                },
                "color": "#4169E1",
                "weight": "bold"
              },
              {
                "type": "icon",
                "size": "sm",
                "url": "https://resources.help.salesforce.com/images/205349b6561a2e06402e850555ee4a8b.png"
              },
              {
                "type": "text",
                "text": "認識作者的貓",
                "size": "sm",
                "flex": 1,
                "wrap": true,
                "position": "relative",
                "align": "start",
                "action": {
                  "type": "uri",
                  "label": "action",
                  "uri": "https://line.me/R/nv/recommendOA/@368zeyal"
                },
                "color": "#4169E1",
                "weight": "bold"
              }
            ]
          }
        ]
      },
      {
        "type": "separator",
        "margin": "xxl"
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
      {
        "type": "button",
        "style": "primary",
        "height": "sm",
        "action": {
          "type": "message",
          "label": "給作者意見",
          "text": "請輸入格式'紀錄-XXXXX'"
        },
        "position": "relative",
        "color": "#4169E1"
      },
      {
        "type": "button",
        "style": "primary",
        "height": "sm",
        "action": {
          "type": "uri",
          "label": "贊助作者",
          "uri": "https://shopee.tw/shuyu02011?v=b88&smtt=0.0.4"
        },
        "position": "relative",
        "color": "#4169E1"
      },
      {
        "type": "spacer",
        "size": "xs"
      }
    ],
    "flex": 0
  }
}"""
 

'''

將bubble類型的json 進行轉換變成 Python可理解之類型物件

將該物件封裝進 Flex Message中

'''

from linebot.models import(
    FlexSendMessage,BubbleContainer
)

import json

bubbleContainer= BubbleContainer.new_from_json_dict(json.loads(flexBubbleContainerJsonString))
flexBubbleSendMessage =  FlexSendMessage(alt_text="hello", contents=bubbleContainer)

'''
設計一個字典

當用戶輸入 [::flex:]carousel ，回傳 旋轉類型的Flex消息

當用戶輸入 [::flex:]bubble ， 回傳 泡泡堆疊類型的Flex消息

'''
import json
template_message_dict = {
    "登登登登~~~" : flexBubbleSendMessage
}


'''

Application 運行（開發版）

'''
# if __name__ == "__main__":
#     app.run(host='0.0.0.0')


# In[ ]:


'''

Application 運行（heroku版）

'''

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])

