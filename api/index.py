import httpx
from fastapi import FastAPI

app = FastAPI()

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