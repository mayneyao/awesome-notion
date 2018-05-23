import logging
import os
import requests
from configparser import ConfigParser

conf = ConfigParser()
conf.read('conf.ini')

ifttt_webhook_key = conf.get('AUTH', 'ifttt_webhook_key')

from urllib.parse import quote
from urllib.parse import urljoin

from flask import Flask, jsonify
from flask import request

from logging.handlers import RotatingFileHandler

log = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/youtube/liked', methods=['POST'])
def index():
    data = request.get_json()
    app.logger.info(data)

    title = data['title']
    url = data['url']

    # 1. 下载视频转化为音频存储
    if not os.path.exists('{}.mp4'.format(title)):
        r = os.popen('you-get {}'.format(url))

        for line in r.readlines():
            app.logger.info(line)

        r2 = os.popen('ffmpeg -i {}.mp4 ../../file/asmr/{}.mp3'.format(title, title))

        for line in r2.readlines():
            app.logger.info(line)

    # 2. 同步音频到云盘
    file_url = urljoin('https://file.gine.me/asmr/', quote('{}.mp3'.format(title)))
    event = 'asmr_upload'
    my_ifttt_webhook_key = ifttt_webhook_key
    post_url = 'https://maker.ifttt.com/trigger/{}/with/key/{}'.format(event, my_ifttt_webhook_key)

    requests.post(post_url, data={'value1': file_url, 'value2': title})

    return jsonify(request.get_json())


if __name__ == '__main__':
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0')
