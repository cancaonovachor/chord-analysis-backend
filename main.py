import os
from flask import Flask, request, make_response, jsonify
from musicxml_chord_analysis import analyze

app = Flask(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR_PATH")

@app.route('/upload', methods=['POST'])
def upload_multipart():
    if 'uploadFile' not in request.files:
        make_response(jsonify({'result': 'uploadFile is required.'}))

    file = request.files['uploadFile']
    filename = file.filename
    if '' == filename:
        make_response(jsonify({'result': 'filename must not empty.'}))

    analyze(filename)
    return make_response(jsonify({'result': filename}))


@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
