#!/usr/bin/env python3
# start_system.py - Start both backend and frontend
import subprocess
import sys
import os
import time

def start_backend():
    """Start the FastAPI backend server"""
    print("Starting Hadi-Huda Backend API...")
    return subprocess.Popen([
        sys.executable, "api_server.py"
    ], cwd=os.path.dirname(os.path.abspath(__file__)))

def start_frontend():
    """Start the React frontend"""
    print("Starting React Frontend...")
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent-starter-react-main")
    
    # Install dependencies first
    print("Installing frontend dependencies...")
    subprocess.run(["pnpm", "install"], cwd=frontend_dir, check=True)
    
    # Start development server
    return subprocess.Popen([
        "pnpm", "dev"
    ], cwd=frontend_dir)

def main():
    print("Starting Hadi-Huda Integrated System...")
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(3)  # Give backend time to start
        
        # Start frontend
        frontend_process = start_frontend()
        
        print("\nSystem Started Successfully!")
        print("Backend API: http://localhost:8000")
        print("Frontend: http://localhost:3000")
        print("API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop both servers")
        
        # Wait for processes
        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\nShutting down...")
            backend_process.terminate()
            frontend_process.terminate()
            
    except Exception as e:
        print(f"Error starting system: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())