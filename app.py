from flask import Flask, request, jsonify
from models.recipe import Recipe

import inverse_cooking_model.inversecooking_main as ic

app = Flask(__name__)

ingr_size, instrs_size, _, _ = ic.load_vocabularies()
ic.load_model(ingr_size, instrs_size)

@app.route('/predict', methods=['GET'])
def predict():
    r = Recipe(name="Hello", ingredients=["one","two"], steps=["first do this", "then do that"])
    return jsonify(r)

if __name__ == '__main__':
    app.run(debug=False, port=os.getenv('PORT', 8080))
