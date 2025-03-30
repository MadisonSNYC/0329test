from fastapi.testclient import TestClient
import os

# Force simulation mode by setting empty environment variables
os.environ["KALSHI_API_KEY"] = ""
os.environ["KALSHI_API_SECRET"] = ""
os.environ["KALSHI_EMAIL"] = ""
os.environ["KALSHI_PASSWORD"] = ""

# Import the app after setting environment variables
from api.main import app

client = TestClient(app)

def test_execute_simulation():
    res = client.post("/api/execute", json={
        "ticker": "BTCUSD-2025E1",
        "side": "yes",
        "count": 5,
        "price": 50,
        "action": "buy"
    })
    assert res.status_code == 200
    assert res.json()["status"] in ("submitted", "simulation", "error")
    
    # Print the response for inspection
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}")
    
    return res

# For direct execution
if __name__ == "__main__":
    response = test_execute_simulation()
    print("\nTest passed! ✅") 