"use client";

import { useState } from "react";

export function StrategyPanel() {
  const [strategy, setStrategy] = useState("");
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  async function submitStrategy() {
    setLoading(true);
    const res = await fetch("/api/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ strategy })
    });
    const data = await res.json();
    setRecommendations(data.recommendations || []);
    setLoading(false);
  }

  return (
    <div className="space-y-4 bg-card border rounded-xl p-6">
      <h2 className="text-lg font-semibold">🧠 AI Strategy Assistant</h2>
      <textarea
        value={strategy}
        onChange={(e) => setStrategy(e.target.value)}
        rows={3}
        className="w-full rounded-md border bg-background p-3 text-sm"
        placeholder="Describe your strategy… e.g. Trade hourly BTC/ETH based on volume spikes"
      />
      <button
        onClick={submitStrategy}
        disabled={loading}
        className="bg-primary text-white text-sm px-4 py-2 rounded-md"
      >
        {loading ? "Thinking..." : "Get AI Trades"}
      </button>

      {recommendations.length > 0 && (
        <div className="pt-4 space-y-2">
          {recommendations.map((rec, i) => (
            <div key={i} className="p-3 rounded-md border text-sm space-y-1 bg-muted/40">
              <p><strong>Market:</strong> {rec.market}</p>
              <p><strong>Action:</strong> {rec.action}</p>
              <p><strong>Confidence:</strong> {rec.probability}</p>
              <p><strong>Target Exit:</strong> {rec.target_exit}</p>
              <p><strong>Reason:</strong> {rec.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 