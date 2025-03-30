from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
import requests
import os
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

app = FastAPI()

# Environment variables
KALSHI_API_KEY = os.getenv("KALSHI_API_KEY")
KALSHI_EMAIL = os.getenv("KALSHI_EMAIL")
KALSHI_PASSWORD = os.getenv("KALSHI_PASSWORD")
KALSHI_API_SECRET = os.getenv("KALSHI_API_SECRET")
IS_DEMO = os.getenv("IS_DEMO", "false").lower() in ["true", "1", "yes"]

base_domain = "https://demo-api.kalshi.co" if IS_DEMO else "https://trading-api.kalshi.com"
KALSHI_API_BASE = f"{base_domain}/trade-api/v2"

class TradeRequest(BaseModel):
    ticker: str
    side: str             # "yes" or "no"
    count: int            # number of contracts
    price: int            # price in cents (0–100)
    action: str = "buy"   # "buy" or "sell"
    order_type: str = Field("limit", alias="type")

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/feed")
def get_feed():
    headers = {}
    try:
        if KALSHI_API_KEY and KALSHI_API_SECRET:
            key_data = KALSHI_API_SECRET.replace("\\n", "\n")
            private_key = serialization.load_pem_private_key(
                key_data.encode(), password=None, backend=default_backend()
            )
            ts_ms = int(datetime.now().timestamp() * 1000)
            message = f"{ts_ms}GET/trade-api/v2/markets"
            signature = private_key.sign(
                message.encode('utf-8'),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            headers = {
                "KALSHI-ACCESS-KEY": KALSHI_API_KEY,
                "KALSHI-ACCESS-TIMESTAMP": str(ts_ms),
                "KALSHI-ACCESS-SIGNATURE": signature_b64
            }
        elif KALSHI_API_KEY:
            headers["Authorization"] = f"Bearer {KALSHI_API_KEY}"
        elif KALSHI_EMAIL and KALSHI_PASSWORD:
            login_url = f"{KALSHI_API_BASE}/log_in"
            resp = requests.post(login_url, json={"email": KALSHI_EMAIL, "password": KALSHI_PASSWORD})
            token = resp.json().get("token")
            headers["Authorization"] = f"Bearer {token}"
        else:
            return {"markets": [], "source": "dummy"}

        url = f"{KALSHI_API_BASE}/markets"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return {"markets": data.get("markets", []), "source": "kalshi"}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print("❌ Traceback:", error_details)
        return {
            "markets": [], 
            "source": "error", 
            "error": str(e),
            "trace": error_details  # <— helpful!
        }

@app.post("/api/execute")
def execute_trade(req: TradeRequest, request: Request = None):
    headers = {}
    try:
        if KALSHI_API_KEY and KALSHI_API_SECRET:
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
            signature_b64 = base64.b64encode(signature).decode("utf-8")
            headers = {
                "KALSHI-ACCESS-KEY": KALSHI_API_KEY,
                "KALSHI-ACCESS-TIMESTAMP": str(ts_ms),
                "KALSHI-ACCESS-SIGNATURE": signature_b64
            }
        elif KALSHI_API_KEY:
            headers["Authorization"] = f"Bearer {KALSHI_API_KEY}"
        elif KALSHI_EMAIL and KALSHI_PASSWORD:
            login_url = f"{KALSHI_API_BASE}/log_in"
            resp = requests.post(login_url, json={"email": KALSHI_EMAIL, "password": KALSHI_PASSWORD})
            token = resp.json().get("token")
            headers["Authorization"] = f"Bearer {token}"
        else:
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
            "yes_price": req.price,
            "client_order_id": client_order_id
        }

        url = f"{KALSHI_API_BASE}/portfolio/orders"
        response = requests.post(url, json=order_payload, headers=headers)
        response.raise_for_status()
        order_data = response.json() if response.text else {}

        return {
            "status": "submitted",
            "trade_id": client_order_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": "Trade sent to Kalshi",
            "kalshi_response": order_data.get("order_id", None)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "details": "Trade not executed"
        }

# Required for Vercel
app_handler = app
