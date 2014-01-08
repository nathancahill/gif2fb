import os
import string
import random

import redis
import facebook
import requests
from flask import Flask, request

from config import UPLOAD_FOLDER, APP_ID, APP_SECRET

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

redis = redis.StrictRedis()

def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

@app.route("/upload", methods=['POST'])
def upload():
    id = id_generator(32)

    with open(os.path.join(app.config['UPLOAD_FOLDER'], id + '.gif'), 'wb') as file:
        file.write(request.get_data())

    redis.set(id, 'generating')
    redis.rpush('video', id)

    return id + '.gif'

@app.route("/done", methods=['POST'])
def done():
    id = request.form.get('id', None)

    if id:
        return redis.get(id.split('.gif')[0])
    else:
        return 'error'

@app.route("/post", methods=['POST'])
def post():
    user = facebook.get_user_from_cookie(request.cookies, APP_ID, APP_SECRET)

    id = request.form.get('id', None)

    if id:
        id = id.split('.gif')[0]
    else:
        return 'error'

    if user:
        files = {'file': open('uploads/' + id + '.mp4', 'rb')}
        res = requests.post('https://graph-video.facebook.com/me/videos?access_token=' + user['access_token'], files=files)

        os.remove('uploads/' + id + '.mp4')
        os.remove('uploads/' + id + '.gif')

        return res.text
    else:
        return 'error'
