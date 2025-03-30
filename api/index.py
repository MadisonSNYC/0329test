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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                          "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate, br"
        }

        response = requests.get(url, headers=headers)

        return {
            "status_code": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "text": response.text[:500]
        }

    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }

app_handler = app 