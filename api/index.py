import httpx
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/feed")
def use_httpx_feed():
    try:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
        }

        with httpx.Client(http2=True, headers=headers) as client:
            response = client.get("https://demo-api.kalshi.co/trade-api/v2/markets")

        return {
            "status_code": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "text": response.text[:500]
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }

app_handler = app 