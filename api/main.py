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
    
    if not KALSHI_API_KEY and not (KALSHI_EMAIL and KALSHI_PASSWORD):
        # No API credentials configured – return dummy data for testing
        log_to_file("❌ No API credentials found, returning dummy data")
        logger.warning("❌ No API credentials found, returning dummy data")
        print("🛑 Using dummy market data fallback in /feed (no valid Kalshi credentials detected)")
        return {"markets": dummy_markets, "source": "dummy"}
    
    try:
        # Determine which auth method to use
        if KALSHI_API_KEY:
            # Use API key authentication
            log_to_file("✅ Kalshi API key found. Fetching real market feed...")
            logger.info("✅ Kalshi API key found. Fetching real market feed...")
            
            # For v2 API (demo), we need to use a different endpoint structure
            if IS_DEMO:
                # Demo environment API (v2)
                url = f"{KALSHI_API_BASE}/markets"
                log_to_file(f"📌 Using demo API: {url}")
                logger.info(f"📌 Using demo API: {url}")
                headers = {
                    "X-API-Key": KALSHI_API_KEY,
                    "Content-Type": "application/json"
                }
            else:
                # Production environment API (v1)
                url = f"{KALSHI_API_BASE}/markets"
                log_to_file(f"📌 Using production API: {url}")
                logger.info(f"📌 Using production API: {url}")
                headers = {"Authorization": f"Bearer {KALSHI_API_KEY}"}
                
            log_to_file(f"Making request to Kalshi markets endpoint")
            logger.info(f"Making request to Kalshi markets endpoint")
            resp = requests.get(url, headers=headers, timeout=10)
        else:
            # Use email/password authentication
            logger.info("✅ Using email/password authentication to fetch real market feed...")
            
            # Auth URL depends on which environment we're using
            if IS_DEMO:
                # Demo environment API (v2)
                auth_url = f"{KALSHI_API_BASE}/login"
                logger.info(f"📌 Using demo API auth: {auth_url}")
            else:
                # Production environment API (v1)
                auth_url = f"{KALSHI_API_BASE}/login"
                logger.info(f"📌 Using production API auth: {auth_url}")
                
            auth_data = {
                "email": KALSHI_EMAIL,
                "password": KALSHI_PASSWORD
            }
            logger.info(f"Making auth request to Kalshi login endpoint")
            try:
                auth_resp = requests.post(auth_url, json=auth_data, timeout=10)
                auth_resp.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Authentication failed: {str(e)}")
                return {
                    "markets": dummy_markets, 
                    "source": "error", 
                    "error": f"Authentication failed: {str(e)}"
                }
            
            # The token structure might differ between API versions
            try:
                if IS_DEMO:
                    token = auth_resp.json().get("token")
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                else:
                    token = auth_resp.json().get("token")
                    headers = {"Authorization": f"Bearer {token}"}
            except (json.JSONDecodeError, AttributeError) as e:
                logger.error(f"❌ Failed to parse authentication response: {str(e)}")
                return {
                    "markets": dummy_markets, 
                    "source": "error", 
                    "error": f"Failed to parse authentication response: {str(e)}"
                }
            
            # Get markets based on environment
            if IS_DEMO:
                url = f"{KALSHI_API_BASE}/markets"
            else:
                url = f"{KALSHI_API_BASE}/markets"
                
            logger.info(f"Making request to Kalshi markets endpoint")
            resp = requests.get(url, headers=headers, timeout=10)
        
        log_to_file(f"API response status: {resp.status_code}")
        logger.info(f"API response status: {resp.status_code}")
        if resp.status_code != 200:
            log_to_file(f"❌ Error response from Kalshi API with status code: {resp.status_code}")
            logger.error(f"❌ Error response from Kalshi API with status code: {resp.status_code}")
            return {
                "markets": dummy_markets, 
                "source": "error", 
                "error": f"Kalshi API returned status code {resp.status_code}"
            }
            
        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            log_to_file(f"❌ Failed to parse Kalshi API response: {str(e)}")
            logger.error(f"❌ Failed to parse Kalshi API response: {str(e)}")
            return {
                "markets": dummy_markets, 
                "source": "error", 
                "error": f"Failed to parse Kalshi API response: {str(e)}"
            }
        
        # Extract and format market data
        # The structure may differ between API versions
        if IS_DEMO:
            markets = data.get("markets", []) if isinstance(data, dict) else []
        else:
            markets = data.get("markets", []) if isinstance(data, dict) else []
            
        log_to_file(f"✅ Successfully retrieved {len(markets)} markets from Kalshi API")
        logger.info(f"✅ Successfully retrieved {len(markets)} markets from Kalshi API")
        
        # If no markets were returned, use dummy data as fallback
        if not markets:
            log_to_file("❌ No markets returned from Kalshi API, using dummy data")
            logger.warning("❌ No markets returned from Kalshi API, using dummy data")
            return {
                "markets": dummy_markets, 
                "source": "empty_response", 
                "error": "No markets returned from Kalshi API"
            }
            
        # Simplify the response to include key information
        simplified = []
        for m in markets[:10]:  # Limit to 10 markets for readability
            market_data = {
                "id": m.get("id") or m.get("ticker") or m.get("name", ""),
                "title": m.get("title") or m.get("name") or m.get("ticker", "Unknown"),
                "category": m.get("category") or m.get("series") or m.get("event", "General"),
                "yes_bid": m.get("yes_bid") or m.get("last_price") or m.get("price", 0),
                "yes_ask": m.get("yes_ask") or m.get("last_price") or m.get("price", 0),
                "volume": m.get("volume", 0),
                "status": m.get("status", "")
            }
            
            # Add close_time if available in this API version
            if "close_time" in m:
                market_data["close_time"] = m["close_time"]
            
            simplified.append(market_data)
        
        log_to_file("Returning real Kalshi market data with source='kalshi'")
        
        return {"markets": simplified, "source": "kalshi"}
    
    except Exception as e:
        # Log the error and return dummy data as fallback
        logger.error(f"❌ Error fetching Kalshi markets: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "markets": dummy_markets, 
            "source": "error", 
            "error": str(e)
        }

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
    if can_use_openai:
        # Format market data for the prompt
        market_context = ""
        for idx, market in enumerate(market_data[:5]):  # Limit to top 5 markets to save tokens
            market_context += f"{idx+1}. Market: {market.get('market', 'Unknown')}, Price: {market.get('price', 0)}, "
            if 'volume' in market:
                market_context += f"Volume: {market.get('volume', 0)}, "
            if 'status' in market:
                market_context += f"Status: {market.get('status', '')}, "
            if 'close_time' in market:
                market_context += f"Close Time: {market.get('close_time', '')}"
            market_context += "\n"
        
        # Craft a prompt for the OpenAI model
        prompt = f"""You are a trading assistant for Kalshi, a regulated event contracts (prediction market) exchange.
User strategy: "{strategy}"

Current market data:
{market_context}

Based on the strategy and market conditions, create an immediate, actionable hourly trading strategy (Now – Next Hour).

For each recommendation, include:
1. Market: Clearly specify the Kalshi market and asset
2. Action: Explicitly indicate YES or NO
3. Probability: Numerical % probability clearly stated
4. Position: Clearly state the market price or range
5. Contracts: Suggest the number of contracts based on investing a maximum of 15% of available funds per trade
6. Cost: Estimate total cost
7. Target Exit: Recommended exit price to secure profits
8. Stop Loss: Recommended price to limit potential losses
9. Rationale: A brief reason for the recommendation (1-2 sentences)

Format each recommendation as:
- Market: [market name]
- Action: [Buy YES/Buy NO]
- Probability: [XX%]
- Position: [price range]
- Contracts: [number]
- Cost: [$XXX]
- Target Exit: [$XX.XX]
- Stop Loss: [$XX.XX]
- Reason: [brief explanation]

Also include a summary of fund allocation:
- Total funds allocated for these trades
- Remaining balance for next trading phase
- Reserved untouched base amount (40% of total)

Assume a starting balance of $10,000.
Keep your response concise and formatted clearly for easy reading.
"""

        try:
            # Call OpenAI API with the prompt using the newer client format
            print("Making OpenAI API request for recommendations")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" for more advanced reasoning
                messages=[
                    {"role": "system", "content": "You are a helpful trading assistant for Kalshi prediction markets."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Extract the response text
            ai_text = response.choices[0].message.content.strip()
            
            # Try to parse the AI output into structured format
            try:
                # Split by recommendations and parse
                structured_recs = []
                raw_recommendations = ai_text.split("\n\n")
                
                recommendation_pattern = re.compile(r"- (Market|Action|Probability|Position|Contracts|Cost|Target Exit|Stop Loss|Reason): (.*)")
                current_rec = {}
                
                for line in ai_text.split("\n"):
                    match = recommendation_pattern.match(line.strip())
                    if match:
                        key, value = match.groups()
                        # Convert keys to snake_case
                        key = key.lower().replace(" ", "_")
                        current_rec[key] = value
                    elif line.strip() == "" and current_rec:
                        # Empty line and we have a current rec, so add it
                        if 'market' in current_rec:  # Only add if it has at least a market
                            structured_recs.append(current_rec)
                            current_rec = {}
                
                # Add the last one if not empty
                if current_rec and 'market' in current_rec:
                    structured_recs.append(current_rec)
                
                # Extract allocation information if present
                allocation_info = {
                    "total_allocated": "N/A",
                    "remaining_balance": "N/A",
                    "reserved_base": "N/A"
                }
                
                # Look for allocation info in the text
                allocation_pattern = re.compile(r"(Total funds allocated|Remaining balance|Reserved untouched base amount): (\$[\d,]+\.?\d*)")
                for line in ai_text.split("\n"):
                    match = allocation_pattern.search(line)
                    if match:
                        key, value = match.groups()
                        if "Total funds" in key:
                            allocation_info["total_allocated"] = value
                        elif "Remaining balance" in key:
                            allocation_info["remaining_balance"] = value
                        elif "Reserved" in key:
                            allocation_info["reserved_base"] = value
                
                # If we found structured recommendations, return them
                if structured_recs:
                    return {
                        "strategy": strategy,
                        "recommendations": structured_recs,
                        "allocation": allocation_info,
                        "source": "openai"
                    }
            except Exception as e:
                print(f"Error parsing AI response into structured format: {e}")
                # Fall through to return raw text if parsing fails
            
            # For MVP, we'll return the raw text if parsing fails
            return {
                "strategy": strategy, 
                "recommendations": ai_text, 
                "source": "openai"
            }
        except Exception as e:
            # Log the error
            print(f"OpenAI API error: {e}")
            # Fallback to dummy recommendations on error
            response_data = add_allocation_to_recommendations(dummy_recommendations, strategy)
            response_data["source"] = "error"
            response_data["error"] = str(e)
            return response_data
    else:
        # Either we're not using the fallback or the API key isn't set
        reason = "dummy"
        if not OPENAI_API_KEY:
            print("No OpenAI API key found, returning dummy recommendations")
            reason = "no_api_key"
        elif not use_fallback:
            reason = "custom_agent"
        
        response_data = add_allocation_to_recommendations(dummy_recommendations, strategy)
        response_data["source"] = reason
        return response_data

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