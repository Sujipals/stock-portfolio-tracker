from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_URL = "http://127.0.0.1:5000"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
    response = requests.post(f"{API_URL}/portfolio", json=data)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(port=5001, debug=True)