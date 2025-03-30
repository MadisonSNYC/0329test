print("✅ FastAPI main.py is being loaded")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import requests
import json
from dotenv import load_dotenv
import traceback
from openai import OpenAI
import re
from datetime import datetime
import logging
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor

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
    KALSHI_API_BASE = "https://trading-api.kalshi.com/trade-api/v2"
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
    ticker: str           # Market ticker (e.g. "BTCUSD-2025E1")
    side: str             # "yes" or "no"
    count: int            # Number of contracts
    price: int            # Price in cents (0–100)
    action: str = "buy"   # "buy" or "sell"
    order_type: str = Field("limit", alias="type")  # "limit" (default)

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
    print("🔍 API Key present:", "✅" if KALSHI_API_KEY else "❌", "| Secret present:", "✅" if KALSHI_API_SECRET else "❌")
    print("🔍 Email/Password present:", "✅" if KALSHI_EMAIL and KALSHI_PASSWORD else "❌")

    base_domain = "https://demo-api.kalshi.co" if IS_DEMO else "https://trading-api.kalshi.com"
    api_base = f"{base_domain}/trade-api/v2"

    headers = {}
    
    try:
        if KALSHI_API_KEY and KALSHI_API_SECRET:
            print("🔐 Using Kalshi API Key + Secret")
            key_data = KALSHI_API_SECRET.replace("\\n", "\n")

            private_key = serialization.load_pem_private_key(
                key_data.encode(), password=None, backend=default_backend()
            )

            ts_ms = int(datetime.now().timestamp() * 1000)
            message = f"{ts_ms}GET/trade-api/v2/markets"

            signature = private_key.sign(
                message.encode("utf-8"),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            signature_b64 = __import__("base64").b64encode(signature).decode("utf-8")

            headers.update({
                "KALSHI-ACCESS-KEY": KALSHI_API_KEY,
                "KALSHI-ACCESS-TIMESTAMP": str(ts_ms),
                "KALSHI-ACCESS-SIGNATURE": signature_b64
            })
        elif KALSHI_API_KEY and not KALSHI_API_SECRET:
            print("⚠️ Using Bearer token (API key only)")
            headers["Authorization"] = f"Bearer {KALSHI_API_KEY}"

        elif KALSHI_EMAIL and KALSHI_PASSWORD:
            print("🔑 Using email/password login")
            login_url = f"{api_base}/log_in"  # ✅ Must be /log_in, NOT /login
            resp = requests.post(login_url, json={"email": KALSHI_EMAIL, "password": KALSHI_PASSWORD})
            if resp.status_code != 200:
                raise Exception(f"Login failed: {resp.text}")
            token = resp.json().get("token")
            headers["Authorization"] = f"Bearer {token}"
        else:
            print("❌ No Kalshi credentials — returning dummy data")
            return {"markets": dummy_markets, "source": "dummy"}

        url = f"{api_base}/markets"
        print(f"📡 Requesting {url}")
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        markets = data.get("markets", data)

        print(f"✅ Fetched {len(markets)} markets")
        formatted = []
        for m in markets[:10]:
            yes_price = m.get("yes_bid") or m.get("last_price") or 0
            formatted.append({
                "title": m.get("title") or m.get("ticker", "Unknown Market"),
                "category": m.get("category", "unknown"),
                "yes_price": yes_price,
                "volume": m.get("volume", 0)
            })

        return {"markets": formatted, "source": "kalshi"}

    except Exception as e:
        print("❌ Error fetching markets:", e)
        return {
            "markets": dummy_markets,
            "source": "error",
            "error": str(e)
        }

@app.post("/recommendations")
@app.post("/api/recommendations")
def get_recommendations(req: RecommendationRequest, request: Request = None):
    """Generate trade recommendations using OpenAI and local agent in parallel."""
    strategy_text = req.strategy
    mode = request.query_params.get("mode", "agent") if request else "agent"
    logger.info(f"🧠 STRATEGY: \"{strategy_text}\" (mode={mode})")
    
    # Validate strategy text
    if not strategy_text or len(strategy_text.strip()) < 5:
        return {
            "status": "error",
            "error": "Strategy prompt is too short or missing.",
            "details": "Please provide a more detailed trading strategy."
        }
    
    # Clean strategy text (optional)
    strategy_text = strategy_text.strip()
    
    # Unique ID to correlate OpenAI and agent outputs
    request_id = str(uuid4())

    # Prepare placeholders for results
    openai_output = None
    agent_output = None
    openai_error = None
    openai_prompt = None

    # Define a function to call OpenAI API
    def run_openai():
        logger.info("💡 [OpenAI] Running OpenAI recommendation generation...")
        # Build the prompt for OpenAI
        prompt = (
            "You are a Kalshi trading assistant.\n\n"
            f"Given this strategy:\n\"\"\"{strategy_text}\"\"\"\n\n"
            "Scan live Kalshi markets and generate 2–3 trades with the following fields:\n"
            "- Market\n- Action (Buy YES / NO)\n- Probability\n- Position (price or range)\n- Contracts\n- Cost\n- Target Exit\n- Stop Loss\n- Reason (1 sentence)\n\n"
            "Then add a fund summary at the bottom:\n- Total Allocated\n- Remaining Balance\n- Reserved Base\n\n"
            "Respond in Markdown. DO NOT add any extra explanation."
        )
        try:
            if not client:  # OpenAI client was initialized at startup if API key was valid
                raise Exception("OpenAI API key not configured")
            
            # Store the full prompt for later use
            nonlocal openai_prompt
            openai_prompt = prompt
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Kalshi AI trade strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            content = response.choices[0].message.content
            logger.info("✅ [OpenAI] Recommendation received.")
            return content  # Markdown string
        except Exception as e:
            logger.error("❌ [OpenAI] Failed to generate recommendations: %s", str(e))
            raise e  # will be caught outside

    # Define a function for local agent (dummy for now)
    def run_agent():
        logger.info("🤖 [Agent] Generating recommendations using local AI agent...")
        # Here we use dummy_recommendations as the agent's output.
        recos = dummy_recommendations  
        # Calculate allocation based on dummy recos cost
        total_cost = 0
        for reco in recos:
            # Remove '$' and commas to sum costs
            cost_str = reco.get("cost", "$0").replace("$", "").replace(",", "")
            try:
                total_cost += float(cost_str)
            except ValueError:
                pass
        remaining = 10000.00 - total_cost
        allocation = {
            "total_allocated": f"${total_cost:,.2f}",
            "remaining_balance": f"${remaining:,.2f}",
            "reserved_base": "$4000.00"
        }
        logger.info("✅ [Agent] Recommendations ready.")
        return {"recommendations": recos, "allocation": allocation}

    # Run both tasks in parallel (if OpenAI is available)
    with ThreadPoolExecutor() as executor:
        future_agent = executor.submit(run_agent)
        future_openai = None
        if OPENAI_API_KEY and client:
            future_openai = executor.submit(run_openai)
        else:
            logger.info("⚠️ [OpenAI] No OpenAI API configured – will use agent output as fallback.")

        # Collect agent result
        try:
            agent_result = future_agent.result()
            agent_output = agent_result["recommendations"]
            agent_allocation = agent_result["allocation"]
        except Exception as e:
            agent_output = dummy_recommendations
            agent_allocation = {
                "total_allocated": "$0.00",
                "remaining_balance": "$10000.00",
                "reserved_base": "$4000.00"
            }
            logger.error("❌ [Agent] Error in agent logic: %s", str(e))

        # Collect OpenAI result (if attempted)
        if future_openai:
            try:
                openai_content = future_openai.result()
                openai_output = openai_content
            except Exception as e:
                openai_error = str(e)
                # Use agent recommendations as fallback for OpenAI failure
                openai_output = agent_output
                logger.warning("⚠️ [OpenAI] Using agent recommendations as fallback for OpenAI.")

    # At this point, we have openai_output and agent_output (or fallbacks) ready.
    # Write results to Supabase (if configured)
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY"):
        supabase_url = os.getenv("SUPABASE_URL").rstrip("/")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        headers = {
            "Content-Type": "application/json",
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}"
        }
        # Prepare data for openai and agent tables
        try:
            if openai_output is not None:
                openai_data = {
                    "request_id": request_id,
                    "strategy": strategy_text,
                    "prompt": openai_prompt,  # Store the full prompt
                    "result": openai_output,
                    "source": "openai" if not openai_error else "fallback_openai",
                    "error": openai_error or None,
                    "created_at": datetime.utcnow().isoformat()
                }
                res = requests.post(f"{supabase_url}/rest/v1/openai_recommendations", json=openai_data, headers=headers)
                if res.status_code < 300:
                    logger.info("📝 Saved OpenAI recommendation to database.")
                else:
                    logger.error(f"❌ Failed to save OpenAI data: {res.status_code}, {res.text}")
            # Save agent output
            if agent_output is not None:
                agent_data = {
                    "request_id": request_id,
                    "strategy": strategy_text,
                    "result": agent_output,
                    "source": "agent",
                    "created_at": datetime.utcnow().isoformat()
                }
                res = requests.post(f"{supabase_url}/rest/v1/agent_recommendations", json=agent_data, headers=headers)
                if res.status_code < 300:
                    logger.info("📝 Saved Agent recommendation to database.")
                else:
                    logger.error(f"❌ Failed to save agent data: {res.status_code}, {res.text}")
        except Exception as db_err:
            logger.error("❌ Database logging error: %s", str(db_err))

    # Prepare a unified response format regardless of source
    def create_unified_response(source, content, allocation, error=None):
        content_format = "markdown" if source == "openai" and not error else "json"
        response = {
            "strategy": strategy_text,
            "recommendations": {
                "format": content_format,
                "content": content
            },
            "allocation": allocation,
            "source": source
        }
        if error:
            response["error"] = error
        return response

    # Decide what to return to the user based on requested mode
    if mode == "openai":
        if openai_output is None:
            # No OpenAI output (e.g., not configured) -> fallback response
            return create_unified_response(
                "fallback_openai", 
                agent_output, 
                {
                    "total_allocated": "$0.00",
                    "remaining_balance": "$10000.00",
                    "reserved_base": "$4000.00"
                }
            )
        elif openai_error:
            # OpenAI attempted but failed
            return create_unified_response(
                "error", 
                agent_output, 
                {
                    "total_allocated": "$0.00",
                    "remaining_balance": "$10000.00",
                    "reserved_base": "$4000.00"
                },
                openai_error
            )
        else:
            # Successful OpenAI response
            return create_unified_response(
                "openai", 
                openai_output, 
                {
                    "total_allocated": "see text",
                    "remaining_balance": "see text",
                    "reserved_base": "see text"
                }
            )
    else:
        # Default or "agent" mode: return agent's recommendations
        return create_unified_response(
            "custom_agent", 
            agent_output, 
            agent_allocation if agent_output is not None else {
                "total_allocated": "$0.00",
                "remaining_balance": "$10000.00",
                "reserved_base": "$4000.00"
            }
        )

@app.post("/execute")
@app.post("/api/execute")
def execute_trade(req: TradeRequest, request: Request = None):
    print("🚀 Execute endpoint called.")
    print("🎯 TradeRequest:", req.dict())

    base_domain = "https://demo-api.kalshi.co" if IS_DEMO else "https://trading-api.kalshi.com"
    api_base = f"{base_domain}/trade-api/v2"

    headers = {}
    token = None
    
    try:
        # Authentication similar to feed
        if KALSHI_API_KEY and KALSHI_API_SECRET:
            print("🔐 Using Kalshi API Key + Secret")
            key_data = KALSHI_API_SECRET.replace("\\n", "\n")

            private_key = serialization.load_pem_private_key(
                key_data.encode(), password=None, backend=default_backend()
            )

            ts_ms = int(datetime.now().timestamp() * 1000)
            message = f"{ts_ms}POST/trade-api/v2/portfolio/orders"

            signature = private_key.sign(
                message.encode("utf-8"),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            signature_b64 = __import__("base64").b64encode(signature).decode("utf-8")

            headers.update({
                "KALSHI-ACCESS-KEY": KALSHI_API_KEY,
                "KALSHI-ACCESS-TIMESTAMP": str(ts_ms),
                "KALSHI-ACCESS-SIGNATURE": signature_b64
            })
        elif KALSHI_API_KEY and not KALSHI_API_SECRET:
            print("⚠️ Using Bearer token (API key only)")
            headers["Authorization"] = f"Bearer {KALSHI_API_KEY}"

        elif KALSHI_EMAIL and KALSHI_PASSWORD:
            print("🔑 Using email/password login")
            login_url = f"{api_base}/log_in"  # ✅ Must be /log_in, NOT /login
            resp = requests.post(login_url, json={"email": KALSHI_EMAIL, "password": KALSHI_PASSWORD})
            if resp.status_code != 200:
                raise Exception(f"Login failed: {resp.text}")
            token = resp.json().get("token")
            headers["Authorization"] = f"Bearer {token}"
        else:
            print("❌ No Kalshi credentials — simulating trade")
            return {
                "status": "simulation",
                "trade_id": req.ticker,
                "timestamp": datetime.utcnow().isoformat(),
                "details": "Trade simulated (no Kalshi credentials)"
            }

        client_order_id = str(uuid4())
        order_payload = {
            "ticker": req.ticker,
            "side": req.side,
            "count": req.count,
            "type": req.order_type,
            "action": req.action,
            "yes_price": req.price,  # assumes YES side; use "no_price" if needed
            "client_order_id": client_order_id
        }
        print("📦 Order payload:", order_payload)

        url = f"{api_base}/portfolio/orders"
        response = requests.post(url, json=order_payload, headers=headers)
        if response.status_code == 401:
            raise Exception("Unauthorized – check credentials")

        response.raise_for_status()
        order_data = response.json() if response.text else {}
        print("✅ Order placed successfully.")

        return {
            "status": "submitted",
            "trade_id": client_order_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": "Trade sent to Kalshi",
            "kalshi_response": order_data.get("order_id", None)
        }
    except Exception as e:
        print("❌ Error executing trade:", e)
        return {
            "status": "error",
            "error": str(e),
            "details": "Trade not executed"
        }

# This will be used by Vercel serverless functions
app_handler = app
