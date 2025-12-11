from flask import Flask, request, jsonify
from services.trades import get_trades_from_db

app = Flask(__name__)


@app.route("/") 
def index():
    return jsonify({"message": "Polymarket Whale Watcher API"})

@app.route("/get_trades", methods=["GET"])
def get_trades():
    """Get insider trades from Supabase database."""
    # Optional query parameter to limit results
    limit = request.args.get("limit", type=int)
    trades = get_trades_from_db(limit=limit)
    return jsonify({"trades": trades, "count": len(trades)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

