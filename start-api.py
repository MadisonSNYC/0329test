import os
import subprocess
import sys

def start_api_server():
    """
    Start the FastAPI server using uvicorn.
    This can be run directly from a terminal outside VS Code.
    """
    print("Starting FastAPI server...")
    
    # Determine the Python executable to use
    python_exec = sys.executable
    
    # Command to start uvicorn server
    cmd = [python_exec, "-m", "uvicorn", "api.index:app", "--host", "127.0.0.1", "--port", "8001", "--reload"]
    
    # Print the command being executed
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # Start the server
        process = subprocess.Popen(cmd)
        print(f"FastAPI server started with PID: {process.pid}")
        print("Press Ctrl+C to stop the server.")
        
        # Wait for the process to complete (or be interrupted)
        process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping FastAPI server...")
        process.terminate()
        process.wait()
        print("FastAPI server stopped.")
    except Exception as e:
        print(f"Error starting FastAPI server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(start_api_server()) 