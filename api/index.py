from fastapi import FastAPI
import traceback
import requests

app = FastAPI()

@app.get("/api/feed")
def test_kalshi_request():
    try:
        print("📡 /api/feed called — Kalshi ping starting...")

        url = "https://demo-api.kalshi.co/trade-api/v2/markets"
        headers = {
            "Accept": "application/json",
            "User-Agent": "kalshi-fastapi-client/1.0"
        }

        response = requests.get(url, headers=headers)

        print("📡 Kalshi responded with", response.status_code)

        return {
            "status_code": response.status_code,
            "json": response.json() if response.status_code == 200 else None,
            "text": response.text,
            "status": "kalshi-request-complete"
        }
    except Exception as e:
        trace = traceback.format_exc()
        print("❌ Error during Kalshi test request:\n", trace)
        return {
            "error": str(e),
            "trace": trace,
            "status": "kalshi-request-failed"
        }

app_handler = app 