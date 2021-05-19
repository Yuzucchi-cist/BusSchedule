import os.path
import sys
import csv
import requests
import urllib.request, urllib.error
from bs4 import BeautifulSoup
import logging

class LINENotifyBot:
    API_URL = "https://notify-api.line.me/api/notify"
    def __init__(self, access_token):
        self.headers = {'Authorization': 'Bearer ' + access_token}
    
    def send(self, message, image=None, sticker_package_id=None, sticker_id=None):
        message = '\n' + message
        payload = {
                'message': message,
                'stickerPackageId' : sticker_package_id,
                'stickerId' : sticker_id
        }

        files = {}

        if image != None:
            files = {'imageFile' : open(image, 'rb')}
        
        r = requests.post(self.API_URL, headers=self.headers, data=payload, files=files)

#ログの記録するフォーマットを決める
log_format = '%(levelname)s : %(asctime)s : %(message)s'
logging.basicConfig(filename='log.log', level=logging.INFO, format=log_format)
logging.info('START')
url = 'https://www.chitose.ac.jp/info/access'
bot = LINENotifyBot(access_token = '80AFrkbQdIc76sTvfg8rCc2GCxlKnq6vYyh9gKtoELV')
try:
    #HTMLを取得
    html = urllib.request.urlopen(url)
    #HTMLのステータスコード(正常に取得できたかどうか)を記録
    logging.info('HTTP STATUS CODE : ' + str(html.getcode()))
except:
    #取得に失敗した場合のLINEに通知
    bot.send('URLの取得に失敗しました')
    #念のため強制終了
    sys.exit(1)
soup = BeautifulSoup(html, "html.parser")
#HTMLの中からaタグのみを抽出
tags = soup.find_all("a")
links = list()
#前回取得したリンク
oldlinks = set()
#今回取得したリンク
newlinks = set()

#aタグからリンクのURLのみを取り出す
for tag in tags:
    links.append(tag.get('href'))

#前回取得したリンクをファイルから読み込む
try:
    if os.path.isfile('links.csv'):
        with open('links.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                oldlinks = set(row)
            logging.info('Opend csv file')
        links_flg = True
    else:
        #csvファイルが存在しない場合の通知、ログ
        bot.send('新しくURLの状態を保存します')
        logging.info('Create new links.csv')
        links_flg = False
except:
    #失敗した場合のLINEに通知、ログ
    bot.send('ファイルの取得に失敗しました')
    logging.error('Failed to get csv file')

try:
    #今回取得したリンクを記録する（上書き）
    with open('links.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(links)
    logging.info('Writed csv file')
except:
    #失敗した場合の通知、ログ
    bot.send('ファイルの書き込みに失敗しました')
    logging.error('Failed to write csv file')
    sys.exit(1)

try:
    newlinks = set(links)
    #setで引き算をすると差分がわかる
    if links_flg :
        #今回新しく発見したリンク
        added = newlinks - oldlinks
        #前回あったが今回亡くなったリンク
        removed = oldlinks - newlinks

        for link in added:
            #追加されたら通知
            bot.send('リンクが追加されました')
        
        for link in removed:
            #消去されたら通知
            bot.send('リンクが消去されました')
        
        logging.info('Compared links')

except:
    #失敗した場合の通知、ログ
    bot.send('比較に失敗しました')
    logging.error('Failed to compare')
    sys.exit(1)

logging.info('DONE')