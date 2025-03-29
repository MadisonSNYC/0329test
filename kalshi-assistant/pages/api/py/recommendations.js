// Next.js API route handler for recommendations
export default function handler(req, res) {
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