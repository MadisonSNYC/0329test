from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import json
from dotenv import load_dotenv
import traceback
from openai import OpenAI
import re
from datetime import datetime
import logging

# Simple debug trace file - accessible to all in the codebase
def log_to_file(message):
    with open("kalshi_debug.txt", "a") as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("kalshi_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("kalshi_assistant")

# Load environment variables
load_dotenv()

# Kalshi API configuration
KALSHI_API_KEY = os.getenv("KALSHI_API_KEY")
KALSHI_EMAIL = os.getenv("KALSHI_EMAIL")
KALSHI_PASSWORD = os.getenv("KALSHI_PASSWORD")
KALSHI_API_SECRET = os.getenv("KALSHI_API_SECRET")
IS_DEMO = os.getenv("IS_DEMO", "false").lower() in ["true", "1", "yes"]

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Only initialize the client if we have a valid API key
# For environment placeholders, we treat them as not having a key
if OPENAI_API_KEY and "your_" not in OPENAI_API_KEY and len(OPENAI_API_KEY) > 30:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print(f"OpenAI API key found and appears valid")
else:
    client = None
    if OPENAI_API_KEY:
        print(f"OpenAI API key found but appears to be a placeholder or invalid")
    else:
        print(f"No OpenAI API key found")

# Set the appropriate API base URL (demo or production)
if IS_DEMO:
    KALSHI_API_BASE = "https://demo-api.kalshi.co/trade-api/v2"
    print("Using DEMO Kalshi API environment")
    # Override IS_DEMO to a string for comparison in the get_trade_feed function
    IS_DEMO = "true"
else:
    KALSHI_API_BASE = "https://trading-api.kalshi.com/v1"
    print("Using PRODUCTION Kalshi API environment")

# Print environment variables for debugging (sensitive info will be masked)
print(f"KALSHI_API_KEY: {'Present' if KALSHI_API_KEY else 'Not set'}")
print(f"KALSHI_EMAIL: {'Present' if KALSHI_EMAIL else 'Not set'}")
print(f"KALSHI_PASSWORD: {'Present' if KALSHI_PASSWORD else 'Not set'}")
print(f"KALSHI_API_SECRET: {'Present' if KALSHI_API_SECRET else 'Not set'}")
print(f"OpenAI client initialized: {client is not None}")
print(f"API Environment: {'DEMO' if IS_DEMO else 'PRODUCTION'}")

# Add diagnostic info for Vercel deployment
print("🧪 DEBUG - KALSHI_API_KEY loaded?", bool(KALSHI_API_KEY))
print("🧪 DEBUG - KALSHI_EMAIL/PASSWORD loaded?", bool(KALSHI_EMAIL and KALSHI_PASSWORD))
print("🧪 DEBUG - OPENAI_API_KEY loaded?", bool(OPENAI_API_KEY))

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class RecommendationRequest(BaseModel):
    strategy: str

class TradeRequest(BaseModel):
    trade_id: str

# Dummy data structures
dummy_markets = [
    {
        "id": "ExampleEvent1", 
        "title": "Example Event 1", 
        "category": "Crypto", 
        "yes_bid": 0.55, 
        "yes_ask": 0.57, 
        "volume": 1000,
        "status": "active"
    },
    {
        "id": "ExampleEvent2", 
        "title": "Example Event 2", 
        "category": "Economics", 
        "yes_bid": 0.30, 
        "yes_ask": 0.32, 
        "volume": 750,
        "status": "active"
    },
]

dummy_recommendations = [
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
]

# Add allocation data to the dummy response
def add_allocation_to_recommendations(recommendations, strategy=None):
    """Add allocation data to recommendations response."""
    # Calculate total cost based on recommendations
    total_cost = sum(float(rec.get("cost", "0").replace("$", "").replace(",", "")) 
                     for rec in recommendations if isinstance(rec, dict))
    
    # Format as currency
    total_cost_formatted = f"${total_cost:,.2f}"
    
    # Assuming starting balance of $10,000
    starting_balance = 10000
    remaining = starting_balance - total_cost
    reserved = starting_balance * 0.4  # 40% reserved as base
    
    return {
        "strategy": strategy,
        "recommendations": recommendations,
        "allocation": {
            "total_allocated": total_cost_formatted,
            "remaining_balance": f"${remaining:,.2f}",
            "reserved_base": f"${reserved:,.2f}"
        },
        "source": "dummy"
    }

@app.get("/")
def read_root():
    """Root endpoint to verify the API is working"""
    return {"message": "Kalshi Trading Assistant API is running"}

@app.get("/hello")
def read_hello():
    """Test endpoint to verify frontend-to-backend integration"""
    return {"message": "Hello from FastAPI"}

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify the API is working"""
    return {"status": "ok", "message": "Kalshi Trading Assistant API is running"}

@app.get("/feed")
@app.get("/api/feed")
def get_trade_feed():
    print("🚦 Feed endpoint called.")
    print("🔍 IS_DEMO:", IS_DEMO)
    print("🔍 API Key:", "✅" if KALSHI_API_KEY else "❌")
    print("🔍 Email login:", "✅" if KALSHI_EMAIL and KALSHI_PASSWORD else "❌")

    try:
        if IS_DEMO == "true":
            print("🧪 Using Kalshi DEMO API")
            url = "https://demo-api.kalshi.co/trade-api/v2/markets"
            headers = {"X-API-Key": KALSHI_API_KEY}
        elif KALSHI_API_KEY:
            print("🧪 Using Kalshi PROD API with API Key")
            url = "https://trading-api.kalshi.com/v1/markets"
            headers = {"Authorization": f"Bearer {KALSHI_API_KEY}"}
        elif KALSHI_EMAIL and KALSHI_PASSWORD:
            print("🧪 Using Kalshi login flow")
            login_url = "https://trading-api.kalshi.com/v1/login"
            login_payload = {
                "email": KALSHI_EMAIL,
                "password": KALSHI_PASSWORD
            }
            login_resp = requests.post(login_url, json=login_payload)
            token = login_resp.json().get("token")
            headers = {"Authorization": f"Bearer {token}"}
            url = "https://trading-api.kalshi.com/v1/markets"
        else:
            print("❌ No Kalshi credentials found. Fallback to dummy.")
            return {"markets": dummy_markets, "source": "dummy"}

        print(f"📡 Requesting from {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        print("✅ Fetched market count:", len(data.get("markets", [])))

        formatted = []
        for m in data.get("markets", [])[:10]:
            formatted.append({
                "title": m.get("title") or m.get("ticker"),
                "category": m.get("category", "unknown"),
                "yes_price": m.get("yes_bid") or m.get("last_price") or 0,
                "volume": m.get("volume", 0)
            })

        return {
            "markets": formatted,
            "source": "kalshi"
        }

    except Exception as e:
        print("❌ Error fetching Kalshi feed:", str(e))
        return {
            "markets": dummy_markets,
            "source": "error",
            "error": str(e)
        }

@app.post("/recommendations")
@app.post("/api/recommendations")
def get_recommendations(req: RecommendationRequest, request: Request = None):
    """Generate trade recommendations using AI (OpenAI or custom)."""
    strategy_text = req.strategy
    print(f"🧠 STRATEGY PROMPT: {strategy_text}")
    
    # Check for mode parameter in query
    mode = "agent"  # default mode is agent
    if request:
        mode = request.query_params.get("mode", "agent")
    
    print(f"⚙️ MODE SELECTED: {mode}")

    if mode == "openai":
        if not OPENAI_API_KEY:
            print("❌ No OpenAI API Key - fallback to dummy")
            return {
                "strategy": strategy_text,
                "recommendations": dummy_recommendations,
                "allocation": {
                    "total_allocated": "$0.00",
                    "remaining_balance": "$10000.00",
                    "reserved_base": "$4000.00"
                },
                "source": "fallback_openai"
            }

        # Build prompt from user input
        prompt = f"""
You are a Kalshi trading assistant.

Given this strategy:
\"\"\"{strategy_text}\"\"\"

Scan live Kalshi markets and generate 2–3 trades with the following fields:
- Market
- Action (Buy YES / NO)
- Probability
- Position (price or range)
- Contracts
- Cost
- Target Exit
- Stop Loss
- Reason (1 sentence)

Then add a fund summary at the bottom:
- Total Allocated
- Remaining Balance
- Reserved Base

Respond in Markdown. DO NOT add any extra explanation.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Kalshi AI trade strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )

            ai_output = response.choices[0].message.content
            print("✅ OpenAI Response:", ai_output[:300])

            return {
                "strategy": strategy_text,
                "recommendations": ai_output,
                "allocation": {
                    "total_allocated": "see text",
                    "remaining_balance": "see text",
                    "reserved_base": "see text"
                },
                "source": "openai"
            }

        except Exception as e:
            print("❌ OpenAI failed:", str(e))
            return {
                "strategy": strategy_text,
                "recommendations": dummy_recommendations,
                "allocation": {
                    "total_allocated": "$0.00",
                    "remaining_balance": "$10000.00",
                    "reserved_base": "$4000.00"
                },
                "source": "error",
                "error": str(e)
            }

    # Default: agent mode (currently fallback)
    print("🛠️ Using AGENT fallback (dummy logic)")

    return {
        "strategy": strategy_text,
        "recommendations": dummy_recommendations,
        "allocation": {
            "total_allocated": "$1394.00",
            "remaining_balance": "$8606.00",
            "reserved_base": "$4000.00"
        },
        "source": "custom_agent"
    }

@app.post("/execute")
@app.post("/api/execute")
def execute_trade(req: TradeRequest):
    """Execute a trade (stub)."""
    # In a real implementation, place an order via Kalshi API
    now = datetime.now().isoformat()
    
    return {
        "status": "executed", 
        "trade_id": req.trade_id,
        "timestamp": now,
        "details": "Trade simulated in development environment"
    }

# This will be used by Vercel serverless functions
app_handler = app 