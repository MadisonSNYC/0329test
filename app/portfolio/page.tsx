"use client";

import { useEffect, useState } from "react";
import RequireAuth from "../../components/require-auth";

type Position = {
  ticker: string;
  contracts_held: number;
  average_open_price: number;
  current_price: number;
  pnl: number;
};

export default function PortfolioPage() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/positions")
      .then(res => res.json())
      .then(data => {
        setPositions(data.positions || []);
        setLoading(false);
      });
  }, []);

  return (
    <RequireAuth>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-semibold">📂 Portfolio</h1>

        {loading ? (
          <p className="text-sm text-muted-foreground">Loading positions...</p>
        ) : positions.length === 0 ? (
          <p className="text-muted-foreground text-sm">No open trades.</p>
        ) : (
          <div className="overflow-auto rounded-md border">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-muted text-left">
                  <th className="p-3">Market</th>
                  <th className="p-3">Contracts</th>
                  <th className="p-3">Open Price</th>
                  <th className="p-3">Current Price</th>
                  <th className="p-3">P&L</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos, i) => (
                  <tr key={i} className="border-t">
                    <td className="p-3 font-medium">{pos.ticker}</td>
                    <td className="p-3">{pos.contracts_held}</td>
                    <td className="p-3">${pos.average_open_price.toFixed(2)}</td>
                    <td className="p-3">${pos.current_price.toFixed(2)}</td>
                    <td className={`p-3 font-medium ${pos.pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                      ${pos.pnl.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </RequireAuth>
  );
} 