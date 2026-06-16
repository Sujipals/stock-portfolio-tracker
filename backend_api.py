from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import yfinance as yf
import logging

app = Flask(__name__, template_folder='templates')
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/portfolio", methods=["POST"])
def portfolio():
    try:
        data = request.json
        
        if not data or len(data) == 0:
            return jsonify({"error": "No stocks provided"}), 400
        
        total = 0
        result = []
        errors = []

        for item in data:
            try:
                symbol = item.get("symbol", "").strip().upper()
                qty = item.get("quantity", 0)

                if not symbol or qty <= 0:
                    errors.append(f"Invalid symbol or quantity")
                    continue

                # Fetch stock data
                stock = yf.Ticker(symbol)
                price = stock.info.get("regularMarketPrice")
                
                # Fallback: try getting previous close price if current price is None
                if price is None:
                    price = stock.info.get("previousClose", 0)
                
                if price is None:
                    price = 0
                    logger.warning(f"Could not fetch price for {symbol}")

                value = price * qty
                total += value

                result.append({
                    "symbol": symbol,
                    "price": price,
                    "quantity": qty,
                    "value": value
                })

            except Exception as e:
                error_msg = f"Error fetching {item.get('symbol', 'Unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

        if len(result) == 0:
            return jsonify({"error": "Could not fetch data for any stocks"}), 400

        return jsonify({
            "stocks": result,
            "total": total,
            "errors": errors
        })

    except Exception as e:
        logger.error(f"Portfolio calculation error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/calculate", methods=["POST"])
def calculate():
    """Alias for /portfolio endpoint to match frontend calls"""
    return portfolio()

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
