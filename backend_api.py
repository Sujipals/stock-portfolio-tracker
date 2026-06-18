from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import yfinance as yf
import logging
import os
import sqlite3
import json
from datetime import datetime

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
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
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

        valid, verrors = validate_stocks_payload(data)
        if not valid:
            return jsonify({"error": "Invalid payload", "details": verrors}), 400
        
        total = 0.0
        result = []
        errors = []

        def fetch_price(sym: str):
            """Robustly fetch a price for `sym` using multiple yfinance methods."""
            try:
                ticker = yf.Ticker(sym)
            except Exception:
                return None

            # 1) Try fast_info if available
            try:
                fi = getattr(ticker, "fast_info", None)
                if fi and isinstance(fi, dict):
                    p = fi.get("lastPrice") or fi.get("last_price")
                    if p is not None:
                        return float(p)
            except Exception:
                pass

            # 2) Try history close
            try:
                hist = ticker.history(period="5d", interval="1d")
                if hist is not None and not hist.empty:
                    return float(hist["Close"].iloc[-1])
            except Exception:
                pass

            # 3) Try info dict fallbacks
            try:
                info = getattr(ticker, "info", {}) or {}
                p = info.get("regularMarketPrice") or info.get("previousClose") or info.get("currentPrice")
                if p is not None:
                    return float(p)
            except Exception:
                pass

            return None

        for item in data:
            try:
                symbol = str(item.get("symbol", "")).strip().upper()
                raw_qty = item.get("quantity", 0)

                # Normalize quantity to float (accept strings)
                try:
                    qty = float(raw_qty)
                except Exception:
                    errors.append(f"Invalid quantity for {symbol}: {raw_qty}")
                    continue

                if not symbol or qty <= 0:
                    errors.append(f"Invalid symbol or quantity for item: {item}")
                    continue

                logger.info(f"Fetching data for {symbol}...")

                price = fetch_price(symbol)
                if price is None:
                    logger.warning(f"Could not fetch price for {symbol}")
                    errors.append(f"No price available for {symbol}")
                    continue

                value = float(price) * float(qty)
                total += value

                result.append({
                    "symbol": symbol,
                    "price": float(price),
                    "quantity": float(qty),
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


# --- Simple SQLite storage for portfolios (server-side) ---
DB_PATH = os.environ.get("DB_PATH", "data.db")

def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS portfolios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stocks TEXT NOT NULL,
        saved_at TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

init_db()


def list_portfolios():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, saved_at, json(length(stocks)) FROM portfolios")
    rows = cur.fetchall()
    # Fallback: select id, name, saved_at
    if not rows:
        cur.execute("SELECT id, name, saved_at FROM portfolios")
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_portfolio(name, stocks):
    conn = get_db_conn()
    cur = conn.cursor()
    saved_at = datetime.utcnow().isoformat() + "Z"
    cur.execute("INSERT INTO portfolios (name, stocks, saved_at) VALUES (?, ?, ?)",
                (name, json.dumps(stocks), saved_at))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def validate_stocks_payload(stocks):
    """Validate stocks payload: must be a list of {symbol, quantity} with valid values.
    Returns (ok: bool, errors: list)
    """
    errors = []
    if not isinstance(stocks, list):
        return False, ["stocks must be a list"]

    for i, item in enumerate(stocks):
        if not isinstance(item, dict):
            errors.append(f"item {i} must be an object")
            continue

        symbol = item.get("symbol")
        qty = item.get("quantity")

        if not symbol or not isinstance(symbol, str) or not symbol.strip():
            errors.append(f"item {i}: missing or invalid symbol")

        try:
            q = float(qty)
            if q <= 0:
                errors.append(f"item {i}: quantity must be > 0")
        except Exception:
            errors.append(f"item {i}: invalid quantity")

    return (len(errors) == 0), errors


def get_portfolio(pid):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, stocks, saved_at FROM portfolios WHERE id = ?", (pid,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    try:
        d["stocks"] = json.loads(d["stocks"])
    except Exception:
        d["stocks"] = []
    return d


def delete_portfolio_db(pid):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM portfolios WHERE id = ?", (pid,))
    conn.commit()
    changes = cur.rowcount
    conn.close()
    return changes > 0


@app.route("/portfolios", methods=["GET"])
def api_list_portfolios():
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, saved_at FROM portfolios ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        data = [{"id": r[0], "name": r[1], "savedAt": r[2]} for r in rows]
        return jsonify({"portfolios": data}), 200
    except Exception as e:
        logger.error(f"Error listing portfolios: {e}")
        return jsonify({"error": "Could not list portfolios"}), 500


@app.route("/portfolios", methods=["POST"])
def api_save_portfolio():
    try:
        payload = request.json
        name = (payload.get("name") or "Untitled").strip()
        stocks = payload.get("stocks") or []
        if not name:
            return jsonify({"error": "Name is required"}), 400
        valid, verrors = validate_stocks_payload(stocks)
        if not valid:
            return jsonify({"error": "Invalid stocks", "details": verrors}), 400
        pid = save_portfolio(name, stocks)
        return jsonify({"id": pid, "name": name}), 201
    except Exception as e:
        logger.error(f"Error saving portfolio: {e}", exc_info=True)
        return jsonify({"error": "Could not save portfolio"}), 500


@app.route("/portfolios/<int:pid>", methods=["GET"])
def api_get_portfolio(pid):
    try:
        p = get_portfolio(pid)
        if not p:
            return jsonify({"error": "Not found"}), 404
        return jsonify(p), 200
    except Exception as e:
        logger.error(f"Error fetching portfolio {pid}: {e}", exc_info=True)
        return jsonify({"error": "Could not fetch portfolio"}), 500


@app.route("/portfolios/<int:pid>", methods=["DELETE"])
def api_delete_portfolio(pid):
    try:
        ok = delete_portfolio_db(pid)
        if not ok:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"deleted": True}), 200
    except Exception as e:
        logger.error(f"Error deleting portfolio {pid}: {e}", exc_info=True)
        return jsonify({"error": "Could not delete portfolio"}), 500


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
    # Use PORT env var (Vercel) and bind to 0.0.0.0 for container environments
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)
