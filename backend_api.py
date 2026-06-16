from flask import Flask, jsonify, request, render_template
import yfinance as yf

app = Flask(__name__, template_folder='templates')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/portfolio", methods=["POST"])
def portfolio():
    data = request.json
    total = 0
    result = []

    for item in data:
        symbol = item["symbol"]
        qty = item["quantity"]

        stock = yf.Ticker(symbol)
        price = stock.info.get("regularMarketPrice")
        if price is None:
            price = 0
        value = price * qty

        total += value
        result.append({
            "symbol": symbol,
            "price": price,
            "quantity": qty,
            "value": value
        })

    return jsonify({"stocks": result, "total": total})

@app.route("/calculate", methods=["POST"])
def calculate():
    """Alias for /portfolio endpoint to match frontend calls"""
    return portfolio()

if __name__ == "__main__":
    app.run(port=5000, debug=True)
