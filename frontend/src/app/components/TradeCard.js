import { Card, CardContent } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";

export function TradeCard({
  marketTitle,
  wallet,
  notional,
  side,
  priceImpact,
  insiderScore,
  timestamp,
  onClick,
}) {
  const safeNotional = Number(notional) || 0;           
  const safePriceImpact = Number(priceImpact) || 0;     
  const safeTimestamp = timestamp
    ? new Date(timestamp).toLocaleString()
    : "Unknown time";                                   

  const isPositive = safePriceImpact >= 0;

  return (
    <Card
      className="border border-neutral-800 bg-[#1b1912] hover:bg-[#22201a] 
                 transition cursor-pointer rounded-xl w-full"
      onClick={onClick}
    >
      <CardContent className="flex items-center justify-between gap-6 p-6">
        
        <div className="flex flex-col min-w-0 flex-1">
          <h3 className="text-lg font-semibold text-white truncate">
            {marketTitle || "Unknown Market"}
          </h3>
          <p className="text-neutral-400 text-sm">{safeTimestamp}</p>
        </div>

        <div className="flex flex-col text-sm min-w-0">
          <span className="text-neutral-400">Wallet</span>
          <span className="text-neutral-200 truncate">{wallet || "N/A"}</span>
        </div>

        <div className="flex flex-col text-sm">
          <span className="text-neutral-400">Bet Size</span>
          <span className="text-neutral-200 font-medium">
            ${safeNotional.toLocaleString()}
          </span>
        </div>

        <div className="flex flex-col text-sm items-start">
          <span className="text-neutral-400">Side</span>
          <span className="flex items-center gap-1 text-neutral-200 font-medium">
            {(side || "").toUpperCase()}
            {isPositive ? (
              <ArrowUpRight className="w-4 h-4 text-green-400" />
            ) : (
              <ArrowDownRight className="w-4 h-4 text-red-400" />
            )}
          </span>
        </div>

        <div className="flex flex-col text-sm">
          <span className="text-neutral-400">Insider Score</span>
          <span
            className={`font-semibold ${
              insiderScore >= 80
                ? "text-green-400"
                : insiderScore >= 60
                ? "text-yellow-400"
                : "text-red-400"
            }`}
          >
            {insiderScore ?? "N/A"}
          </span>
        </div>

        <div className="flex flex-col text-sm">
          <span className="text-neutral-400">Price Impact</span>
          <span
            className={`font-medium ${
              isPositive ? "text-green-400" : "text-red-400"
            }`}
          >
            {safePriceImpact > 0 ? "+" : ""}
            {safePriceImpact}%
          </span>
        </div>

      </CardContent>
    </Card>
  );
}
