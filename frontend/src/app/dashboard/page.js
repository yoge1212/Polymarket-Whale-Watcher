"use client";
import { TradeCard } from "../components/TradeCard";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Dashboard() {
    const [trades, setTrades] = useState([]);
    const router = useRouter();

    useEffect(() => {
        fetch("/api/trades")
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                setTrades(data.trades || []);
                if (data.error) {
                    console.error("API error:", data.error);
                }
            })
            .catch(error => {
                console.error("Error fetching trades:", error);
                setTrades([]); 
            });
    }, []);

    return (
      <div className="min-h-screen bg-[#13120a] text-white">
        <main className="flex min-h-[calc(100vh-80px)] flex-col items-start justify-start px-16 pt-32">
          <div className="flex flex-col gap-6 w-full">
            <h1>Insider Feed (Live)</h1>
            <div className="flex gap-3 flex-col w-full">
                
            {trades.map((trade) => (
                <TradeCard
                    key={trade.id}
                    marketTitle={trade.market_title}
                    wallet={trade.wallet}
                    notional={trade.notional_usd}
                    side={trade.side}
                    priceImpact={trade.price_impact}
                    insiderScore={trade.insider_score}
                    timestamp={trade.trade_timestamp}
                />
            ))}

            </div>
          </div>
        </main>
      </div>
    );
  }
  