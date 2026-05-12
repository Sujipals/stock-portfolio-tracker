from flask import Flask, jsonify, request
import yfinance as yf

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(port=5000, debug=True)