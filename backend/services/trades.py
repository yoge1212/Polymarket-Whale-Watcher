from typing import Optional, List, Dict
import logging
import os
from datetime import datetime, timezone
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")   

supabase: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None




def insert_insider_trade(
    wallet: str,
    market_id: str,
    market_title: str,
    market_slug: str,
    event_slug: str,
    outcome: str,
    side: str,
    size: float,
    price: float,
    notional_usd: float,
    price_impact: Optional[float],
    insider_score: float,
    trade_timestamp: datetime,
) -> bool:
    """
    Insert an insider trade into the database.
    
    Args:
        wallet: Wallet address
        market_id: Market condition ID
        market_title: Market title
        market_slug: Market slug
        event_slug: Event slug
        outcome: Outcome name
        side: Trade side (buy/sell)
        size: Trade size
        price: Trade price
        notional_usd: Notional value in USD
        price_impact: Price impact percentage (optional)
        insider_score: Insider score (0-100)
        trade_timestamp: Trade timestamp as datetime
        
    Returns:
        True if inserted successfully, False otherwise
    """
    if not supabase:
        logging.warning("Supabase not initialized, cannot insert trade")
        return False
    
    try:
        trade_data = {
            "wallet": wallet,
            "market_id": market_id,
            "market_title": market_title,
            "market_slug": market_slug,
            "event_slug": event_slug,
            "outcome": outcome,
            "side": side,
            "size": float(size),
            "price": float(price),
            "notional_usd": float(notional_usd),
            "price_impact": float(price_impact) if price_impact is not None else None,
            "insider_score": float(insider_score),
            "trade_timestamp": trade_timestamp.isoformat(),
        }
        
        supabase.table("insider_trades").insert(trade_data).execute()
        identifier = f"{wallet}-{market_id}"
        logging.info(f"✅ Inserted insider trade to Supabase: {identifier}")
        return True
    except Exception as e:
        logging.error(f"Failed to insert trade to Supabase: {e}")
        return False


def get_trades_from_db(limit: Optional[int] = None) -> List[Dict]:
    """
    Get insider trades from Supabase database.
    Returns list of trades as dictionaries, most recent first.
    
    Args:
        limit: Optional limit on number of trades to return (default: all)
    
    Returns:
        List of trade dictionaries
    """
    if not supabase:
        logging.warning("Supabase not initialized, returning empty list")
        return []
    
    try:
        query = supabase.table("insider_trades").select("*").order("trade_timestamp", desc=True)
        
        if limit is not None and limit > 0:
            query = query.limit(limit)
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        logging.error(f"Failed to fetch trades from Supabase: {e}")
        return []
    