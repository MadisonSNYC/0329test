"use client";

import { useEffect, useState } from "react";

type Tracker = {
  symbol: string;
  name: string;
  price: number | null;
  change: number | null;
  sentiment: number | null; // from Kalshi
};

export function MarketTrackers() {
  const [trackers, setTrackers] = useState<Tracker[]>([]);

  useEffect(() => {
    async function loadData() {
      const [
        cryptoRes,
        spxRes,
        ixicRes,
        kalshiRes
      ] = await Promise.all([
        fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,dogecoin&vs_currencies=usd&include_24hr_change=true").then(res => res.json()),
        fetch("https://api.allorigins.win/get?url=https://query1.finance.yahoo.com/v7/finance/quote?symbols=%5EGSPC").then(res => res.json()),
        fetch("https://api.allorigins.win/get?url=https://query1.finance.yahoo.com/v7/finance/quote?symbols=%5EIXIC").then(res => res.json()),
        fetch("/api/feed").then(res => res.json())
      ]);

      const parseYahoo = (raw: any) => {
        const parsed = JSON.parse(raw.contents);
        const q = parsed.quoteResponse.result[0];
        return {
          price: q.regularMarketPrice,
          change: q.regularMarketChangePercent
        };
      };

      const kalshiMarkets = kalshiRes.markets || [];

      const getSentiment = (keyword: string): number | null => {
        const match = kalshiMarkets.find((m: any) =>
          m.ticker.toLowerCase().includes(keyword.toLowerCase())
        );
        return match?.yes_bid ?? null;
      };

      const merged: Tracker[] = [
        {
          symbol: "BTC",
          name: "Bitcoin",
          price: cryptoRes.bitcoin.usd,
          change: cryptoRes.bitcoin.usd_24h_change,
          sentiment: getSentiment("btc")
        },
        {
          symbol: "ETH",
          name: "Ethereum",
          price: cryptoRes.ethereum.usd,
          change: cryptoRes.ethereum.usd_24h_change,
          sentiment: getSentiment("eth")
        },
        {
          symbol: "DOGE",
          name: "Dogecoin",
          price: cryptoRes.dogecoin.usd,
          change: cryptoRes.dogecoin.usd_24h_change,
          sentiment: getSentiment("doge")
        },
        {
          symbol: "SPX",
          name: "S&P 500",
          ...parseYahoo(spxRes),
          sentiment: getSentiment("spx")
        },
        {
          symbol: "NDX",
          name: "Nasdaq",
          ...parseYahoo(ixicRes),
          sentiment: getSentiment("ixic")
        }
      ];

      setTrackers(merged);
    }

    loadData();
  }, []);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {trackers.map((t) => (
        <div
          key={t.symbol}
          className="rounded-xl border p-4 bg-card shadow-sm flex flex-col gap-1"
        >
          <div className="text-sm text-muted-foreground">{t.name}</div>
          <div className="text-2xl font-semibold">${t.price?.toFixed(2)}</div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span className={t.change && t.change > 0 ? "text-green-600" : "text-red-500"}>
              {t.change?.toFixed(2)}%
            </span>
            {t.sentiment !== null && (
              <span>
                Kalshi Sentiment:{" "}
                <strong>{(t.sentiment * 100).toFixed(0)}%</strong>
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
} 