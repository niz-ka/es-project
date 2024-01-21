import os
import base64
import uuid
import datetime

from flask import Flask, redirect, send_from_directory
from flask import render_template
from flask import request
from flask import url_for
from elasticsearch import Elasticsearch, NotFoundError

UPLOAD_FOLDER = './files'
INDEX = 'my-index-000001'
PIPELINE = 'attachment'
ANALYZER = "lang_pl"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
es = Elasticsearch("http://localhost:9200")


@app.route("/", methods=["GET"])
def index():
    search_arg = request.args.get('search')

    if search_arg:
        response = es.search(
            index=INDEX,
            query={
                "match": {
                    "attachment.content": {
                        "query": search_arg,
                        "analyzer": ANALYZER
                    }
                }
            },
        )

    else:
        search_arg = ""
        response = es.search(index=INDEX, query={
            "match_all": {},
        })

    files = []
    for i, doc in enumerate(response['hits']['hits']):
        real_filename = doc['_source']['real_filename']
        secure_filename = doc['_source']['secure_filename']
        uploaded = doc['_source']['uploaded']
        files.append((i + 1, real_filename, secure_filename, uploaded))

    return render_template('index.html', files=files, search_arg=search_arg)


@app.route("/", methods=["POST"])
def upload():
    files = request.files.getlist("file")
    for file in files:
        if not file.filename:
            continue
        real_filename = file.filename
        id = uuid.uuid4()
        new_filename = f'{id}.{real_filename.split(".", 1)[-1]}'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

        with open(os.path.join(app.config['UPLOAD_FOLDER'], new_filename),
                  'rb') as b_file:
            content = b_file.read()

        es.index(index=INDEX,
                 pipeline=PIPELINE,
                 id=id,
                 refresh=True,
                 document={
                     "data": base64.b64encode(content).decode(),
                     "real_filename": real_filename,
                     "secure_filename": new_filename,
                     "id": id,
                     "uploaded": str(datetime.datetime.now()),
                 })

    return redirect(url_for('index'))


@app.route('/download/<name>', methods=["GET"])
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route('/delete/<name>', methods=["POST"])
def delete_file(name: str):
    try:
        es.delete(index=INDEX, id=name.split('.')[0], refresh=True)
    except NotFoundError:
        pass

    file = os.path.join(app.config['UPLOAD_FOLDER'], name)
    if os.path.isfile(file):
        os.remove(file)

    return redirect(url_for('index'))


@app.route('/delete_all', methods=["POST"])
def delete_all():

    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        os.remove(path)

    es.delete_by_query(
        index=INDEX,
        body={"query": {
            "match_all": {}
        }},
        refresh=True,
    )

    return redirect(url_for('index'))
