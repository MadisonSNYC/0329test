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
    """Return latest market feed from Kalshi API."""
    log_to_file("Feed endpoint called")
    logger.info("Feed endpoint called")
    
    if not any([KALSHI_API_KEY, KALSHI_EMAIL, KALSHI_PASSWORD]):
        print("❌ No Kalshi credentials detected.")
    else:
        print("✅ Kalshi credentials detected. Proceeding with live fetch.")

    try:
        if IS_DEMO == "true":
            print("🔁 Using Kalshi DEMO API")
            url = "https://demo-api.kalshi.co/trade-api/v2/markets"
            headers = {"X-API-Key": KALSHI_API_KEY}
        else:
            print("🔁 Using Kalshi PROD API")
            url = "https://trading-api.kalshi.com/v1/markets"
            headers = {"Authorization": f"Bearer {KALSHI_API_KEY}"}

        response = requests.get(url, headers=headers)
        data = response.json()

        print("✅ Raw Kalshi Market Feed (first 1):", data.get("markets", [])[0])

        return {
            "markets": [
                {
                    "title": m.get("title") or m.get("ticker"),
                    "category": m.get("category", "unknown"),
                    "yes_bid": m.get("yes_bid") or m.get("last_price") or m.get("price"),
                    "volume": m.get("volume", 0)
                }
                for m in data.get("markets", [])[:10]
            ],
            "source": "kalshi"
        }

    except Exception as e:
        print("❌ Kalshi Fetch Failed:", str(e))
        return {"markets": dummy_markets, "source": "error", "error": str(e)}

@app.post("/recommendations")
@app.post("/api/recommendations")
def get_recommendations(req: RecommendationRequest, request: Request = None):
    """Generate trade recommendations using AI (OpenAI or custom)."""
    logger.info(f"Recommendations requested for strategy: {req.strategy}")
    log_to_file(f"Recommendations requested for strategy: {req.strategy}")
    
    # Start with fallback in case the real API call fails
    if not req.strategy or req.strategy.strip() == "":
        logger.warning("No strategy provided, using default recommendations")
        print("🛑 Using dummy recommendations fallback in /recommendations - no strategy provided")
        return add_allocation_to_recommendations(dummy_recommendations, "balanced")
    
    # If OpenAI is not configured, return dummy recommendations
    if not client:
        logger.warning("OpenAI client not initialized, using dummy recommendations")
        print("🛑 Using dummy recommendations fallback in /recommendations - no valid OpenAI key")
        return add_allocation_to_recommendations(dummy_recommendations, req.strategy)
        
    strategy = req.strategy or ""
    
    # Check for mode parameter in query
    mode = "agent"  # default mode is agent
    if request:
        mode = request.query_params.get("mode", "agent")
    
    # Add the requested debug prints
    print("🎯 Mode selected:", mode)
    if not OPENAI_API_KEY:
        print("🛑 No OpenAI API key detected — using dummy fallback")
    
    # Set use_fallback based on mode
    # If mode is "openai", use the OpenAI fallback
    # If mode is "agent", prepare to use our custom agent (default to dummy for now)
    use_fallback = (mode == "openai")
    
    # Check if we can use OpenAI (needs API key and fallback enabled)
    can_use_openai = use_fallback and OPENAI_API_KEY and client
    
    # 1. Get current market data (to provide context to AI)
    market_data = []
    try:
        market_response = get_trade_feed()
        market_data = market_response.get("markets", [])  # reuse our feed function
    except Exception as e:
        print(f"Could not fetch market data: {e}")
        # Continue with empty market data rather than failing completely
    
    # 2. Prepare prompt for OpenAI
    if not can_use_openai:
        print("🧠 Using Fallback: dummy_agent")
        return {
            "strategy": strategy,
            "recommendations": dummy_recommendations,
            "allocation": {
                "total_allocated": "$1394.00",
                "remaining_balance": "$8606.00",
                "reserved_base": "$4000.00"
            },
            "source": "custom_agent"
        }

    print("🧠 Calling OpenAI with strategy prompt...")

    prompt = f"""
    You are a Kalshi trading assistant.

    Strategy:
    {strategy}

    Generate up to 3 hourly trade recommendations using Kalshi prediction markets.
    Each recommendation should include:
    - Market
    - Action (Buy YES or Buy NO)
    - Probability
    - Position range
    - Contracts
    - Cost
    - Target Exit
    - Stop Loss
    - 1-2 sentence rationale

    Also summarize fund allocation: total allocated, remaining, and base reserve.

    Respond ONLY with structured output in markdown format.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Kalshi AI trade strategist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        raw_output = response.choices[0].message.content
        print("✅ OpenAI Raw Response:", raw_output[:500])

        return {
            "strategy": strategy,
            "recommendations": raw_output,
            "source": "openai"
        }

    except Exception as e:
        print("❌ OpenAI failed:", str(e))
        return {
            "strategy": strategy,
            "recommendations": dummy_recommendations,
            "allocation": {"total_allocated": "0", "remaining_balance": "0", "reserved_base": "0"},
            "source": "error",
            "error": str(e)
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