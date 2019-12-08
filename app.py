from flask import Flask, request, jsonify
from models.recipe import Recipe

import inverse_cooking_model.inversecooking_main as ic

app = Flask(__name__)

def initialize_model():
    ingr_size, instrs_size, _, _ = ic.load_vocabularies()
    return ic.load_model(ingr_size, instrs_size)

@app.route('/predict', methods=['GET'])
def predict():
    r = Recipe(name="Hello",
               ingredients=["one","two"],
               steps=["first do this", "then do that"])
    return jsonify(r)

model = initialize_model()
if __name__ == '__main__':
    app.run(debug=False, port=os.getenv('PORT', 8080))
