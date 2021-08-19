import os
from flask import Flask, request, make_response, jsonify, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from google.cloud import storage

from musicxml_chord_analysis import getChordMinimumUnit, writeChord
from music21 import environment

from io import StringIO

environment.set('autoDownload', 'allow')

app = Flask(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR_PATH")

CLOUD_STORAGE_BUCKET = os.getenv("CLOUD_STORAGE_BUCKET")

CLOUD_STORAGE_ENDPOINT = 'http://' + \
    CLOUD_STORAGE_BUCKET + '.storage.googleapis.com'

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
        if 'file' not in request.files:
            make_response(jsonify({'result': 'uploadFile is required.'}))

        file = request.files.get('file')
        filename = file.filename
        if '' == filename:
            make_response(jsonify({'result': 'filename must not empty.'}))

        gcs = storage.Client()

        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

        blob = bucket.blob(filename)
        blob.upload_from_string(
            file.read(),
            content_type=file.content_type
        )

        if file and allowed_file(file.filename):
            # file: werzurg.FileStorage
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for())
            response = make_response()

            # upload file to cloud storage
            file_url = upload_blob(file, filename)

            # file_url = cloud_storage_endpoint + '/nippon.musicxml'

            chord_list = getChordMinimumUnit(
                file_url, head=1, tail=-1, sameChordPass=1)

            # 受け取ったmusicxmlに、オンメモリでコードを書き込む
            output = StringIO()
            output.write(writeChord(file, chord_list, head=1, tail=-1))

            response.data = output.getvalue()

            output.close()

            downloadFileName = 'down' + filename
            response.headers['Content-Disposition'] = 'attachment; filename=' + \
                downloadFileName

            response.mimetype = 'text/xml'

            return response

    return '''
    <!doctype html>
    <title>chord analysis</title>
    <h1>コード解析</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
