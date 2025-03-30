from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/api/feed")
def get_feed():
    import traceback
    try:
        print("📡 /api/feed called")

        url = "https://demo-api.kalshi.co/trade-api/v2/markets"
        headers = {
            "Accept": "application/json",
            "User-Agent": "kalshi-fastapi-client/1.0"
        }

        response = requests.get(url, headers=headers)
        print("📡 Kalshi response status:", response.status_code)

        # Return raw content in string if not JSON
        if response.headers.get("Content-Type", "").startswith("application/json"):
            data = response.json()
        else:
            data = {"raw_text": response.text}

        return {
            "status_code": response.status_code,
            "kalshi_response": data,
            "status": "kalshi-request-complete"
        }

    except Exception as e:
        trace = traceback.format_exc()
        print("❌ ERROR in /api/feed:\n", trace)
        return {
            "error": str(e),
            "trace": trace,
            "status": "kalshi-request-failed"
        }

app_handler = app 