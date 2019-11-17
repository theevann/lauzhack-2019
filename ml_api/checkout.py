import os
import re
import json
import base64
from PIL import Image
from io import BytesIO
from pathlib import Path

from flask import jsonify, request
from flask_cors import cross_origin

from app import app
from model_api import ModelApi


person_data = json.load(Path('jsons/person.json').open('r'))
food_data = json.load(Path('jsons/food.json').open('r'))

person_api = ModelApi('./models/model_person.pth')
food_api = ModelApi('./models/model_food.pth')


@app.route('/dish', methods=['POST'])
@cross_origin()
def dish():
    json_data = json.loads(request.data.decode('utf8'))
    person = json_data.get('person')
    food = json_data.get('food')

    if not food or not person:
        return "No data"

    person_b64 = re.sub('^data:image/.+;base64,', '', person)
    person_image = Image.open(BytesIO(base64.b64decode(person_b64)))

    food_b64 = re.sub('^data:image/.+;base64,', '', food)
    food_image = Image.open(BytesIO(base64.b64decode(food_b64)))

    person_id = person_api.get_class(person_image)
    person_info = person_data.get(person_id)

    food_id = food_api.get_class(food_image)
    food_info = food_data.get(food_id)

    return jsonify({"person": person_info['firstname'] + " " + person_info['lastname'],
                    "status": person_info['status'],
                    "food": food_info['name'],
                    "price": food_info['price']})


if __name__ == '__main__':
    app.run(debug=True)
