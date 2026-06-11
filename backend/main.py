import subprocess
import sys
import uvicorn

def main():
    print("🚀 Starting AgentDesk Backend Workflow...")

    print("📦 Ensuring PostgreSQL container is running...")
    try:
        # Spin up the database silently
        subprocess.run(["docker-compose", "up", "-d", "db"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start Docker Compose. Make sure Docker Desktop is running.")
        sys.exit(1)
    
    print("✅ Database is up. Starting FastAPI server...")
    
    # Run uvicorn programmatically
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
