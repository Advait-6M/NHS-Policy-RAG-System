"""Script to run both FastAPI backend and Streamlit frontend."""

import multiprocessing
import os
import subprocess
import sys
import time
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent


def run_fastapi():
    """Run FastAPI backend server."""
    print("🚀 Starting FastAPI backend on http://localhost:8000")
    os.chdir(PROJECT_ROOT)
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"],
        check=True,
    )


def run_streamlit():
    """Run Streamlit frontend."""
    # Wait a bit for FastAPI to start
    time.sleep(2)
    print("🚀 Starting Streamlit frontend on http://localhost:8501")
    os.chdir(PROJECT_ROOT)
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "src/app.py", "--server.port", "8501"],
        check=True,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("🏥 NEPPA: NHS Expert Policy Assistant")
    print("=" * 60)
    print("\nStarting both FastAPI backend and Streamlit frontend...")
    print("Press Ctrl+C to stop both services.\n")
    
    # Create processes for both services
    fastapi_process = multiprocessing.Process(target=run_fastapi, name="FastAPI")
    streamlit_process = multiprocessing.Process(target=run_streamlit, name="Streamlit")
    
    try:
        # Start both processes
        fastapi_process.start()
        streamlit_process.start()
        
        # Wait for both processes
        fastapi_process.join()
        streamlit_process.join()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        fastapi_process.terminate()
        streamlit_process.terminate()
        fastapi_process.join()
        streamlit_process.join()
        print("✅ Services stopped.")

