from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
# import openai
import os
import sys
from argparse import ArgumentParser
from skimage import color, io
from skimage import segmentation
from skimage.color import label2rgb


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, StickerMessage, TextSendMessage, ImageSendMessage, StickerSendMessage
)


app = Flask(__name__)

# 總共有四個地方要 改
channel_access_token = "HtrTk7+Fx848jDD4gNaKlyyoa0wcm6PFmZvsmimXBwp9XMiRsmygv59AhxVsZBNTSve0p1jUv/gMhM1398fZig2yg5Vo8AT0+FpOGXg60hmXGc35IDBNeBgXaqLFevyx+FaLORXET1kjHa57nz5BEgdB04t89/1O/w1cDnyilFU="
channel_secret = "e90698fdc335803f77785b291d7fd68c"

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))
   
# https://azweb*****.azurewebsites.net/callback
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
# https://github.com/line/line-bot-sdk-python#message
# MessageEvent
# type
# mode
# timestamp
# source: Source
# reply_token
# message: Message
###################################################這裡是朋友送給LINE 機器人


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    from datetime import datetime, timedelta
    now = (datetime.now() + timedelta(hours=8) ).strftime("%Y/%m/%d %H:%M:%S")
    try:
        ai =  event.message.text

    except Exception as e:
        ai = 'Something wrong in API, try again'
        with open('/home/logerr.txt', mode = 'a+') as f:
            f.write(str(e) + "\n")
            f.write(str(event.reply_token)+"\n")
            f.write("-" * 50 + "\n")
                
    replytext = "Lewis say {}: ".format(now) + ai + '...'
    
    with open('/home/log.txt', mode = 'a+') as f:
        f.write(replytext + "\n")
        f.write(str(event.reply_token)+"\n")
        f.write("-" * 50 + "\n")

    message = [
        TextSendMessage( text = replytext )
    ]

    line_bot_api.reply_message(
        event.reply_token,
        message
    )    


# 當LINE BOT收到圖片之後就說 回個 笑臉
@handler.add(MessageEvent, message=StickerMessage)
def message_image(event):
    from datetime import datetime, timedelta
    now = (datetime.now() + timedelta(hours=8) ).strftime("%Y/%m/%d %H:%M:%S")
    try:
        ai = "收到你圖樣訊息"
    except Exception as e:
        ai = 'Something wrong in OpenAI, try again'
        with open('/home/logstickererr.txt', mode = 'a+') as f:
            f.write(str(e) + "\n")
            f.write(str(event.reply_token)+"\n")
            f.write("-" * 50 + "\n")
                
    replytext = ai + '...'
    with open('/home/logsticker.txt', mode = 'a+') as f:
        f.write(replytext + "\n")
        f.write(str(event.reply_token)+"\n")
        f.write("-" * 50 + "\n")

    message = [
        TextSendMessage( text = replytext ), 
        StickerSendMessage( package_id = "1070", sticker_id ="17839" ), 
    ]

    line_bot_api.reply_message(
        event.reply_token,
        message
    )    
#https://developers.line.biz/en/docs/messaging-api/sticker-list/#sticker-definitions

# 當LINE BOT收到圖片之後開始處理
@handler.add(MessageEvent, message=ImageMessage)
def message_image(event):
    from datetime import datetime, timedelta
    now = (datetime.now() + timedelta(hours=8) ).strftime("%Y/%m/%d %H:%M:%S")
    try:
        ai = "收到你圖片訊息處理中..."
        SendImage = line_bot_api.get_message_content(event.message.id)

        path = './static/images/' + event.message.id + '.png'
        with open(path, 'wb') as fd:
            for chenk in SendImage.iter_content():
                fd.write(chenk)
        #灰階
        #io.imsave(path.replace('.png','.jpg'), (io.imread(path, as_gray=True)*255.0).astype('uint8'))
        
        #SuperPixel
        face = io.imread(path, as_gray=False)
        segments = segmentation.slic(face, start_label = 1, n_segments=500)
        segmented_face = label2rgb(label=segments, image=face, kind='avg', bg_label=None).astype('uint8')
        io.imsave(path.replace('.png','.jpg'), segmented_face)

    except Exception as e:
        ai = 'Something wrong in Image Processing, try again'
        with open('/home/logImageerr.txt', mode = 'a+') as f:
            f.write(str(e) + "\n")
            f.write(str(event.reply_token)+"\n")
            f.write("-" * 50 + "\n")
                
    replytext = ai + '轉成 SuperPixel 模式' #+ path
    with open('/home/logImage.txt', mode = 'a+') as f:
        f.write(replytext + "\n")
        f.write(str(event.reply_token)+"\n")
        f.write("-" * 50 + "\n")

    message = [
        TextSendMessage( text = replytext ),
        ImageSendMessage(original_content_url="https://azwebcunyuan.azurewebsites.net/static/images/" + event.message.id + '.jpg', preview_image_url="https://azwebcunyuan.azurewebsites.net/static/images/" + event.message.id + '.jpg')
    ]

    line_bot_api.reply_message(
        event.reply_token,
        message
    )        


if __name__ == '__main__':
    app.run()