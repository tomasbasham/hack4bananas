import os

from flask import Flask, jsonify, request

import inverse_cooking_model.inversecooking_main as ic
from models.recipe import Recipe

app = Flask(__name__)


def initialize_model():
    ingr_size, instrs_size, _, _ = ic.load_vocabularies()
    return ic.load_model(ingr_size, instrs_size)


@app.route('/predict', methods=['POST'])
def predict():

    img_url = 'https://scontent.xx.fbcdn.net/v/t1.15752-9/78984001_469543167020392_563915436299649024_n.jpg?_nc_cat=106&_nc_ohc=IYKX4MsAjKEAQnXxr42YfjWiRJ_sGxUKv9bMxIVfYLiNcXobm1XjOb56w&_nc_ad=z-m&_nc_cid=0&_nc_zor=9&_nc_ht=scontent.xx&oh=7d4e22539defe16afa7be21ec145989b&oe=5E8569D4'
    recipes = ic.predict(model, img_url)
    [ic.print_output(recipe) for recipe in recipes]
    r = Recipe(name="Hello", ingredients=["one", "two"], steps=[
               "first do this", "then do that"])

    payload = request.get_json()

    if not "url" in payload:
        return jsonify(error="No image specified"), 400

    r = Recipe(name="Hello",
               ingredients=["one", "two"],
               steps=["first do this", "then do that"])

    return jsonify(r)


model = initialize_model()
if __name__ == '__main__':
    app.run(debug=False, port=os.getenv('PORT', 8080))
