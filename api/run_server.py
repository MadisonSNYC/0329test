import uvicorn
from api.main import app

if __name__ == "__main__":
    # This directly runs the FastAPI app without needing to use the command line
    # Just execute this Python file directly
    print("Starting FastAPI server...")
    print("Server will be available at http://127.0.0.1:8001")
    print("You can test the OpenAI integration at http://localhost:3000/test-api")
    print("Press Ctrl+C to stop the server")
    
    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=8001) 