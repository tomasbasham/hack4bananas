from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    return "Hello"
    # pass

if __name__ == '__main__':
    app.run(debug=False, port=os.getenv('PORT', 8080))
