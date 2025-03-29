from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/hello")
def read_root():
    """Test endpoint to verify frontend-to-backend integration"""
    return {"message": "Hello from FastAPI"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify the API is working"""
    return {"status": "ok", "message": "Kalshi Trading Assistant API is running"}

# This will be used by Vercel serverless functions
app_handler = app 