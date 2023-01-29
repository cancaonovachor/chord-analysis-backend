#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from os.path import join, dirname
from flask import Flask, request, make_response, jsonify, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from urllib.parse import quote
from google.cloud import storage
from flask_cors import CORS

from google.oauth2 import service_account

from dotenv import load_dotenv

from musicxml_chord_analysis import getChordMinimumUnit, writeChord
from music21 import environment

from io import StringIO

load_dotenv(override=True)
environment.set('autoDownload', 'allow')

app = Flask(__name__)
CORS(app)


UPLOAD_DIR = os.getenv("UPLOAD_DIR_PATH")

CLOUD_STORAGE_BUCKET = str(os.getenv("CLOUD_STORAGE_BUCKET"))

CLOUD_STORAGE_ENDPOINT = (
    'http://' + CLOUD_STORAGE_BUCKET + '.storage.googleapis.com')

ALLOWED_EXTENSIONS = {'musicxml'}

PROJECT_ID = os.getenv("PROJECT_ID")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ファイルをアップロードして、ファイルへのURLを返す


def upload_blob(source_file_object, destination_blob_name):
    storage_client = storage.Client(PROJECT_ID)
    bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(source_file_object, rewind=True)

    print(
        "File uploaded to {}".format(
            destination_blob_name
        )
    )

    # upload_from_fileがストリームの位置を変更するので、最初に戻す
    source_file_object.seek(0)

    return CLOUD_STORAGE_ENDPOINT + '/' + destination_blob_name

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        print(request.files)
        if 'file' not in request.files:
            make_response(jsonify({'result': 'uploadFile is required.'}))

        file = request.files.get('file')
        filename = file.filename
        if '' == filename:
            make_response(jsonify({'result': 'filename must not empty.'}))

        gcs = storage.Client()

        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

        if file and allowed_file(file.filename):
            # file: werzurg.FileStorage
            filename = file.filename
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for())
            response = make_response()

            # upload file to cloud storage
            file_url = upload_blob(file, filename)

            # file_url = cloud_storage_endpoint + '/nippon.musicxml'
            sameChordPass = 0 if request.form.get(
                'sameChordPass') == 'false' else 1

            # 開始小節: 最終小節よりも大きい値を入れると解析せずそのままの楽譜が返る
            # start = request.form.get('start')
            # head = int(start) if start != '' else 1

            # 終了小節: -1の場合最後まで
            # 最終小節よりも大きい値を入れるとエラー
            # 開始 > 終了 では解析せずそのままの楽譜が返る
            # end = request.form.get('end')
            # tail = int(end) if end != '' else -1

            chord_list = getChordMinimumUnit(
                file_url, head=1, tail=-1, sameChordPass=sameChordPass)

            # 受け取ったmusicxmlに、オンメモリでコードを書き込む
            output = StringIO()
            output.write(writeChord(file, chord_list, head=1, tail=-1))

            response.data = output.getvalue()

            output.close()

            downloadFileName = 'down' + filename
            response.headers["Content-Disposition"] = \
                "attachment;" \
                "filename*=UTF-8''{utf_filename}".format(
                utf_filename=quote(downloadFileName.encode('utf-8'))
            )

            response.mimetype = 'text/xml'

            return response

    return '''
    <!doctype html>
    <head>
        <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
        <meta content="utf-8" http-equiv="encoding">
    </head>
    <title>chord analysis</title>
    <h1>コード解析</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file> <br>
      前と同じコードを飛ばす <input type=checkbox name=sameChordPass><br>
      開始小節 <input type="number" name="start"> <br>
      終了小節 <input type="number" name="end">
      <br>
      <input type=submit value=Upload>
    </form>
    '''


@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "VS")
    return "Hello {}!".format(name)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == "__main__":
    app.run(debug=bool(os.getenv('DEBUG')), host="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)))
