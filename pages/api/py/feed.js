// Next.js API route handler for feed endpoint
export default function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }
  
  // Dummy markets data that mimics the Kalshi API response
  const dummyMarkets = {
    markets: [
      {
        id: "BTCUSD-24MAR",
        title: "Bitcoin Price Range",
        subtitle: "Will BTC be above $52,500 by Mar 31?",
        category: "CRYPTO",
        close_time: new Date(2024, 2, 31).toISOString(),
        yes_bid: 0.65,
        yes_ask: 0.68,
        volume: 12500,
        open_interest: 8700
      },
      {
        id: "ETHUSD-24MAR",
        title: "Ethereum Price Range",
        subtitle: "Will ETH be above $3,000 by Mar 31?",
        category: "CRYPTO",
        close_time: new Date(2024, 2, 31).toISOString(),
        yes_bid: 0.72,
        yes_ask: 0.74,
        volume: 9800,
        open_interest: 6500
      },
      {
        id: "SPX-24MAR",
        title: "S&P 500 Index Range",
        subtitle: "Will SPX be above 5,100 by Mar 31?",
        category: "STOCKS",
        close_time: new Date(2024, 2, 31).toISOString(),
        yes_bid: 0.63,
        yes_ask: 0.65,
        volume: 15700,
        open_interest: 12400
      }
    ],
    cursor: null
  };

  // Return dummy data
  return res.status(200).json(dummyMarkets);
} 