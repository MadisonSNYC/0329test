from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/api/feed")
def get_feed():
    import traceback
    try:
        url = "https://demo-api.kalshi.co/trade-api/v2/markets"
        headers = {
            "Accept": "application/json",
            "User-Agent": "kalshi-fastapi-client/1.0"
        }
        response = requests.get(url, headers=headers)
        return {
            "status_code": response.status_code,
            "text": response.text,
            "status": "kalshi-request-complete"
        }
    except Exception as e:
        trace = traceback.format_exc()
        return {
            "error": str(e),
            "trace": trace,
            "status": "kalshi-request-failed"
        }

app_handler = app 