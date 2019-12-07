from dataclasses import dataclass
from typing import List
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods=['GET'])
def predict():
    r = Recipe(name="Hello", ingredients=["one","two"], steps=["first do this", "then do that"])
    return jsonify(r)

if __name__ == '__main__':
    app.run(debug=False, port=os.getenv('PORT', 8080))

@dataclass
class Recipe:
    name: str
    ingredients: List[str]
    steps: List[str]
