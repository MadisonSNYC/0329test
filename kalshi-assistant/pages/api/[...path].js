// Catch-all route handler for all API requests
export default function handler(req, res) {
  const { path } = req.query;
  const fullPath = path.join('/');
  
  console.log(`API request received for path: ${fullPath}`);
  console.log(`Method: ${req.method}`);
  console.log(`Query params:`, req.query);
  
  // Check if this is a recommendations request
  if (fullPath === 'py/recommendations') {
    // Handle recommendations request
    if (req.method !== 'POST') {
      return res.status(405).json({ message: 'Method not allowed' });
    }

    const { strategy } = req.body;
    const mode = req.query.mode || 'agent';
    
    // Dummy data (copied from your Python backend)
    const dummyRecommendations = [
      {
        "market": "BTCUSD-24MAR", 
        "action": "Buy YES", 
        "reason": "Positive momentum trending upward with increased volume and favorable technical indicators.",
        "probability": "68%",
        "position": "$52,400-$52,600",
        "contracts": "12",
        "cost": "$624",
        "target_exit": "$54,800",
        "stop_loss": "$51,200"
      },
      {
        "market": "ETHUSD-24MAR", 
        "action": "Buy NO", 
        "reason": "Bearish divergence on hourly chart with decreasing volume suggests short-term downward pressure.",
        "probability": "72%",
        "position": "$3,050-$3,080",
        "contracts": "15",
        "cost": "$420",
        "target_exit": "$2,950",
        "stop_loss": "$3,150"
      },
      {
        "market": "SPX-24MAR", 
        "action": "Buy YES", 
        "reason": "Market showing resilience after pullback with positive breadth and momentum indicators.",
        "probability": "65%",
        "position": "$5,120-$5,135",
        "contracts": "10",
        "cost": "$350",
        "target_exit": "$5,180",
        "stop_loss": "$5,090"
      }
    ];

    // Calculate allocation
    const costs = dummyRecommendations.map(rec => 
      parseFloat(rec.cost.replace('$', '').replace(',', ''))
    );
    const totalCost = costs.reduce((a, b) => a + b, 0);
    const startingBalance = 10000;
    const remaining = startingBalance - totalCost;
    const reserved = startingBalance * 0.4;

    // Return dummy data
    return res.status(200).json({
      strategy: strategy,
      recommendations: dummyRecommendations,
      allocation: {
        total_allocated: `$${totalCost.toFixed(2)}`,
        remaining_balance: `$${remaining.toFixed(2)}`,
        reserved_base: `$${reserved.toFixed(2)}`
      },
      source: mode === 'agent' ? 'custom_agent' : 'dummy'
    });
  }
  
  // Check if this is a feed request
  if (fullPath === 'py/feed') {
    // Handle feed request
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

  // Default response for any unknown paths
  return res.status(200).json({ 
    message: `Catch-all endpoint responding to ${fullPath}`,
    query: req.query,
    method: req.method
  });
} 