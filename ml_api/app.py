import os
import re
import json
import shutil
import base64
from PIL import Image
from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin

from model_api import ModelApi
from train_model import train_model


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


general_api = None


@app.route('/add-class', methods=['POST'])
@cross_origin()
def add_class():
    p = "train" / Path(request.json['class'])
    p.mkdir(parents=True, exist_ok=True)
    for i, data in enumerate(request.json['data']):
        b64 = re.sub('^data:image/.+;base64,', '', data)
        Image.open(BytesIO(base64.b64decode(b64))).save(
            (p / str(i)).with_suffix('.jpg'))
    return "OK", 200


@app.route('/rm-class', methods=['GET'])
@cross_origin()
def rm_class():
    shutil.rmtree(Path("train") / request.args['name'])
    return 'OK'


@app.route('/get-classes', methods=['GET'])
@cross_origin()
def get_classes():
    p = Path("train")
    return jsonify([f.name for f in p.iterdir()])


@app.route('/load-model', methods=['GET'])
@cross_origin()
def load_model():
    global general_api
    general_api = ModelApi('models/' + request.args['name'])
    return "OK"


@app.route('/get-models', methods=['GET'])
@cross_origin()
def get_models():
    p = Path("models")
    return jsonify([m.name for m in p.iterdir()])


@app.route('/train', methods=['GET'])
@cross_origin()
def train():
    train_model(request.args['type'],
                request.args['name'], int(request.args['epochs']))
    return "OK"


@app.route('/predict', methods=['GET', 'POST'])
@cross_origin()
def predict():
    if request.method == "GET":
        return render_template('predict.html')

    img = request.json['image']
    if not img:
        return "No data"

    b64 = re.sub('^data:image/.+;base64,', '', img)
    image = Image.open(BytesIO(base64.b64decode(b64)))
    classname = general_api.get_class(image)

    return jsonify({"name": classname})


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

#    print(request.args)
#    print(request.files)
#    print(request.form)
#    print(request.values)
#    print(request.data)
#    print(request.json)
