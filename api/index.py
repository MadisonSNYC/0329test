from fastapi import FastAPI
import traceback

app = FastAPI()

@app.get("/api/feed")
def test_feed():
    try:
        print("📡 /api/feed route HIT ✅")
        # Simulate a safe response
        raise Exception("Controlled test failure inside /api/feed")
    except Exception as e:
        trace = traceback.format_exc()
        print("❌ Exception caught in /api/feed:", trace)
        return {
            "error": str(e),
            "trace": trace,
            "status": "inside-feed-handler"
        }

app_handler = app 