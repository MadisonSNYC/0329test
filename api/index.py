import httpx
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

app = FastAPI()

class TradeRequest(BaseModel):
    ticker: str
    side: str
    count: int
    price: int
    action: str = "buy"
    order_type: str = Field("limit", alias="type")

@app.post("/api/execute")
def execute_trade(req: TradeRequest, request: Request = None):
    return {
        "status": "received",
        "ticker": req.ticker,
        "side": req.side,
        "count": req.count,
        "price": req.price,
        "order_type": req.order_type,
        "action": req.action
    }

@app.get("/api/execute")
def explain_execute():
    return {
        "message": "Use POST method to execute a trade. This endpoint does not accept GET requests."
    }

@app.post("/public/execute")
def public_execute_trade(req: TradeRequest, request: Request = None):
    return {
        "status": "received",
        "ticker": req.ticker,
        "side": req.side,
        "count": req.count,
        "price": req.price,
        "order_type": req.order_type,
        "action": req.action
    }

@app.get("/public/execute")
def explain_public_execute():
    return {
        "message": "Use POST method to execute a trade. This endpoint does not accept GET requests."
    }

@app.post("/noauth/trade")
def noauth_trade(req: TradeRequest, request: Request = None):
    return {
        "status": "received",
        "ticker": req.ticker,
        "side": req.side,
        "count": req.count,
        "price": req.price,
        "order_type": req.order_type,
        "action": req.action
    }

@app.get("/noauth/trade")
def explain_noauth_trade():
    return {
        "message": "Use POST method to execute a trade. This endpoint does not accept GET requests."
    }

@app.get("/api/feed")
def final_kalshi_feed():
    import traceback
    try:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        with httpx.Client(http2=True, headers=headers) as client:
            response = client.get("https://demo-api.kalshi.co/trade-api/v2/markets")

        # Parse only if content type starts with application/json or text/plain
        if response.headers.get("Content-Type", "").startswith(("application/json", "text/plain")):
            data = response.json()
        else:
            data = {"raw": response.text}

        return {
            "status_code": response.status_code,
            "markets": data.get("markets", []),
            "source": "kalshi"
        }

    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "trace": traceback.format_exc(),
            "source": "error"
        }

app_handler = app 