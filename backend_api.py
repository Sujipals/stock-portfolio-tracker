from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import yfinance as yf
import logging

app = Flask(__name__, template_folder='templates')

# Enable CORS with specific configuration for Vercel
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/", methods=["GET"])
def home():
    """Serve the home page"""
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error serving home page: {str(e)}")
        return jsonify({"error": "Could not load home page"}), 500

@app.route("/portfolio", methods=["POST"])
def portfolio():
    """Calculate portfolio value"""
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

                logger.info(f"Fetching data for {symbol}...")
                
                # Fetch stock data
                stock = yf.Ticker(symbol)
                price = stock.info.get("regularMarketPrice")
                
                # Fallback: try getting previous close price if current price is None
                if price is None:
                    price = stock.info.get("previousClose", 0)
                
                if price is None:
                    price = 0
                    logger.warning(f"Could not fetch price for {symbol}")

                value = float(price) * float(qty)
                total += value

                result.append({
                    "symbol": symbol,
                    "price": float(price),
                    "quantity": int(qty),
                    "value": float(value)
                })
                
                logger.info(f"Successfully fetched {symbol}: ${price}")

            except Exception as e:
                error_msg = f"Error fetching {item.get('symbol', 'Unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

        if len(result) == 0:
            return jsonify({"error": "Could not fetch data for any stocks", "details": errors}), 400

        response = {
            "stocks": result,
            "total": float(total)
        }
        
        if errors:
            response["errors"] = errors

        logger.info(f"Portfolio calculation successful. Total: ${total}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Portfolio calculation error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/calculate", methods=["POST", "OPTIONS"])
def calculate():
    """Alias for /portfolio endpoint to match frontend calls"""
    if request.method == "OPTIONS":
        return "", 204
    return portfolio()

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Server is running"}), 200

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {str(error)}")
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"500 error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

# Handle CORS preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return "", 204

if __name__ == "__main__":
    app.run(port=5000, debug=True)
