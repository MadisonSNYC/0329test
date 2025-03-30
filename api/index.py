from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/api/feed")
def safe_feed():
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
            "content_type": response.headers.get("Content-Type"),
            "text": response.text[:500]  # only first 500 characters
        }

    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }

app_handler = app 