from fastapi import FastAPI

app = FastAPI()

@app.get("/api/feed")
def read_feed():
    return {"status": "live"}
