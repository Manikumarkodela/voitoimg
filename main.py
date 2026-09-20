import os
import sys
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir / "backend"))

load_dotenv(dotenv_path=root_dir / ".env")

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    print(f"🚀 Launching VoiToImg FastAPI Backend at http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=debug)
