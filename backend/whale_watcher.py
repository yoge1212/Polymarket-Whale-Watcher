import time
import logging
from datetime import datetime, timezone
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, Deque, List, Tuple, Optional

import requests
from services.trades import insert_insider_trade

POLYMARKET_TRADES_URL = "https://data-api.polymarket.com/trades"

POLL_INTERVAL_SECONDS = 5
RECENT_TRADE_LIMIT = 200

MIN_NOTIONAL_USD = 3000.0
NEW_WALLET_MAX_TRADES = 3
MIN_PRICE_DEVIATION = 0.07



@dataclass
class Trade:
    proxy_wallet: str
    side: str
    condition_id: str
    size: float
    price: float
    timestamp: int
    title: str
    slug: str
    event_slug: str
    outcome: str


@dataclass
class WalletStats:
    first_seen_ts: int
    trade_count: int


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)



def fetch_recent_trades(limit: int = RECENT_TRADE_LIMIT) -> List[Trade]:
    params = {
        "limit": limit,
        "offset": 0,
        "takerOnly": True,
    }

    try:
        resp = requests.get(POLYMARKET_TRADES_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch trades from Polymarket API: {e}")
        raise

    trades: List[Trade] = []
    for t in data:
        try:
            trades.append(
                Trade(
                    proxy_wallet=t.get("proxyWallet"),
                    side=t.get("side"),
                    condition_id=t.get("conditionId"),
                    size=float(t.get("size", 0)),
                    price=float(t.get("price", 0)),
                    timestamp=int(t.get("timestamp", 0)),
                    title=t.get("title") or "",
                    slug=t.get("slug") or "",
                    event_slug=t.get("eventSlug") or "",
                    outcome=t.get("outcome") or "",
                )
            )
        except Exception as e:
            logging.warning(f"Failed to parse trade: {e}")
    return trades


def compute_notional_usd(trade: Trade) -> float:
    return trade.size * trade.price


def compute_insider_score(trade: Trade, wallet_stats: WalletStats, market_price_median: Optional[float]) -> float:
    notional = compute_notional_usd(trade)
    size_score = min(notional / MIN_NOTIONAL_USD, 3.0)
    size_score_norm = min(size_score / 3.0, 1.0)

    if wallet_stats.trade_count <= NEW_WALLET_MAX_TRADES:
        newness_score = 1.0
    elif wallet_stats.trade_count <= 10:
        newness_score = 0.5
    else:
        newness_score = 0.1

    if market_price_median and market_price_median > 0:
        deviation_pct = abs(trade.price - market_price_median) / market_price_median
        price_dev_score = min(deviation_pct / 0.20, 1.0)
    else:
        price_dev_score = 0.3

    score = (
        0.45 * size_score_norm +
        0.35 * newness_score +
        0.20 * price_dev_score
    )
    return round(score * 100, 1)


def is_suspicious_trade(trade: Trade, wallet_stats: WalletStats, median: Optional[float]) -> Tuple[bool, float, Optional[str]]:
    notional = compute_notional_usd(trade)

    if notional < MIN_NOTIONAL_USD:
        return False, 0.0, "low_notional"

    if wallet_stats.trade_count > 20:
        return False, 0.0, "too_many_trades"

    if median and median > 0:
        pct = abs(trade.price - median) / median
        if pct < MIN_PRICE_DEVIATION:
            return False, 0.0, "low_price_deviation"

    score = compute_insider_score(trade, wallet_stats, median)

    if score < 60:
        return False, score, "low_score"

    return True, score, None



class WhaleWatcher:

    def __init__(self, max_recent_trades: int = 1000):
        self.wallets: Dict[str, WalletStats] = {}
        self.recent_market_prices: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=200))
        self.recent_trades: Deque[Trade] = deque(maxlen=max_recent_trades)
        self.poll_count = 0

    def run_once(self):
        """Run ONE polling cycle."""
        self.poll_count += 1
        logging.debug("Polling Polymarket API for recent trades...")
        trades = fetch_recent_trades(limit=RECENT_TRADE_LIMIT)
        trades = list(reversed(trades))
        logging.info(f"Fetched {len(trades)} trades from Polymarket API")

        processed_count = 0
        filtered_count = 0
        alert_count = 0
        filter_reasons = {
            "low_notional": 0,
            "too_many_trades": 0,
            "low_price_deviation": 0,
            "low_score": 0
        }
        notional_values = []

        for trade in trades:
            processed_count += 1
            self.recent_trades.append(trade)
            
            # Track notional values for statistics
            notional = compute_notional_usd(trade)
            notional_values.append(notional)

            ws = self.wallets.get(trade.proxy_wallet)
            if ws is None:
                ws = WalletStats(first_seen_ts=trade.timestamp, trade_count=0)
                self.wallets[trade.proxy_wallet] = ws
            ws.trade_count += 1

            if trade.price > 0:
                self.recent_market_prices[trade.condition_id].append(trade.price)

            prices = self.recent_market_prices[trade.condition_id]
            median = None
            if len(prices) >= 5:
                s = sorted(prices)
                mid = len(s) // 2
                median = s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2

            should_alert, score, reason = is_suspicious_trade(trade, ws, median)
            if not should_alert:
                filtered_count += 1
                if reason:
                    filter_reasons[reason] = filter_reasons.get(reason, 0) + 1
                continue

            notional = compute_notional_usd(trade)
            price_impact = None
            if median:
                price_impact = ((trade.price - median) / median) * 100.0

            insert_insider_trade(
                wallet=trade.proxy_wallet,
                market_id=trade.condition_id,
                market_title=trade.title,
                market_slug=trade.slug,
                event_slug=trade.event_slug,
                outcome=trade.outcome,
                side=trade.side,
                size=trade.size,
                price=trade.price,
                notional_usd=notional,
                price_impact=price_impact,
                insider_score=score,
                trade_timestamp=datetime.fromtimestamp(trade.timestamp, tz=timezone.utc),
            )

            alert_count += 1
            logging.info(f"🚨 Insider Trade Detected | Score {score} | {trade.title}")
        
        if filtered_count > 0:
            reasons_str = ", ".join([f"{k}: {v}" for k, v in filter_reasons.items() if v > 0])
            logging.info(f"Poll cycle complete: {processed_count} processed, {filtered_count} filtered ({reasons_str}), {alert_count} alerts")
        else:
            logging.info(f"Poll cycle complete: {processed_count} processed, {filtered_count} filtered, {alert_count} alerts")
        
        # Log trade value statistics every cycle
        if notional_values:
            max_notional = max(notional_values)
            min_notional = min(notional_values)
            avg_notional = sum(notional_values) / len(notional_values)
            above_threshold = sum(1 for n in notional_values if n >= MIN_NOTIONAL_USD)
            logging.info(f"💰 Trade values: min=${min_notional:,.2f}, max=${max_notional:,.2f}, avg=${avg_notional:,.2f}, {above_threshold}/{len(notional_values)} above ${MIN_NOTIONAL_USD:,.2f} threshold")
        
        # Every 12 polls (1 minute), log summary statistics
        if self.poll_count % 12 == 0:
            total_wallets = len(self.wallets)
            if processed_count > 0:
                sample_trade = trades[0] if trades else None
                if sample_trade:
                    sample_notional = compute_notional_usd(sample_trade)
                    logging.info(f"📊 Summary (last minute): {total_wallets} unique wallets tracked, sample trade notional: ${sample_notional:,.2f}")

    def run_forever(self):
        """Run the watcher loop forever (NO THREADS)."""
        logging.info("WhaleWatcher started in blocking mode.")
        while True:
            try:
                self.run_once()
            except Exception as e:
                logging.exception(f"Monitor loop error: {e}")

            time.sleep(POLL_INTERVAL_SECONDS)



if __name__ == "__main__":
    # Check if Supabase is configured
    from services.trades import supabase
    if supabase is None:
        logging.warning("⚠️  Supabase not configured! Trades will not be saved to database.")
        logging.warning("   Set SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY environment variables.")
    else:
        logging.info("✅ Supabase configured successfully")
    
    watcher = WhaleWatcher()
    watcher.run_forever()
