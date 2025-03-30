from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
import requests
import httpx
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


def auth_headers(method="GET", path="/markets"):
    ts_ms = int(datetime.now().timestamp() * 1000)
    message = f"{ts_ms}{method}{path}"
    key_data = KALSHI_API_SECRET.replace("\\n", "\n")
    private_key = serialization.load_pem_private_key(
        key_data.encode(), password=None, backend=default_backend()
    )
    signature = private_key.sign(
        message.encode("utf-8"),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature).decode("utf-8")
    return {
        "KALSHI-ACCESS-KEY": KALSHI_API_KEY,
        "KALSHI-ACCESS-TIMESTAMP": str(ts_ms),
        "KALSHI-ACCESS-SIGNATURE": signature_b64,
        "Accept": "application/json",
        "User-Agent": "kalshi-fastapi-client/1.0"
    }

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/feed")
def get_feed():
    try:
        headers = auth_headers()
        url = f"{KALSHI_API_BASE}/markets"
        with httpx.Client(http2=True, headers=headers) as client:
            response = client.get(url)
        if response.status_code == 200:
            return {"status_code": response.status_code, "markets": response.json().get("markets", []), "source": "kalshi"}
        else:
            return {"status_code": response.status_code, "text": response.text, "source": "kalshi"}
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc(), "source": "error"}

@app.post("/api/execute")
def execute_trade(req: TradeRequest, request: Request = None):
    try:
        headers = auth_headers(method="POST", path="/portfolio/orders")
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
        response = httpx.post(url, json=order_payload, headers=headers)
        response.raise_for_status()
        return {
            "status": "submitted",
            "trade_id": client_order_id,
            "kalshi_response": response.json()
        }
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "trace": traceback.format_exc()}

@app.get("/api/positions")
def get_positions():
    try:
        headers = auth_headers(path="/portfolio/positions")
        url = f"{KALSHI_API_BASE}/portfolio/positions"
        response = httpx.get(url, headers=headers)
        return response.json()
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/api/orders")
def get_orders():
    try:
        headers = auth_headers(path="/portfolio/orders")
        url = f"{KALSHI_API_BASE}/portfolio/orders"
        response = httpx.get(url, headers=headers)
        return response.json()
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/api/markets/{ticker}/orderbook")
def get_orderbook(ticker: str):
    try:
        headers = auth_headers(path=f"/markets/{ticker}/orderbook")
        url = f"{KALSHI_API_BASE}/markets/{ticker}/orderbook"
        response = httpx.get(url, headers=headers)
        return response.json()
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}

@app.delete("/api/orders/{order_id}")
def cancel_order(order_id: str):
    try:
        headers = auth_headers(method="DELETE", path=f"/portfolio/orders/{order_id}")
        url = f"{KALSHI_API_BASE}/portfolio/orders/{order_id}"
        response = httpx.delete(url, headers=headers)
        return {"status_code": response.status_code, "result": response.json() if response.text else "No content"}
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}

app_handler = app 