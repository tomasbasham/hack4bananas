import os

from flask import Flask, jsonify, request

import inverse_cooking_model.inversecooking_main as ic
from models.recipe import Recipe, recipe_builder

# Silence all the thigns.
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)

def initialize_model():
    ingr_size, instrs_size, ingrs_vocab, vocab = ic.load_vocabularies()
    return ic.load_model(ingr_size, instrs_size), ingrs_vocab, vocab

@app.route('/predict', methods=['POST'])
def predict():
    payload = request.get_json()
    if not "url" in payload:
        return jsonify(error="No image specified"), 400

    raw_recipes = ic.predict(model, ingrs_vocab, vocab, payload["url"])
    recipes = [recipe_builder(recipe) for recipe in raw_recipes]

    if len(recipes) == 0:
        return jsonify(error="No recipes found"), 422

    print(recipes[0])
    return jsonify(recipes[0])

model, ingrs_vocab, vocab = initialize_model()

if __name__ == '__main__':
    app.run(debug=False, port=os.getenv('PORT', 8080))
