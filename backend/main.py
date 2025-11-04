"""
Apollo AI Service - Main Entry Point

Imports and runs the Apollo API server with all agents.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Apollo app
from api.main import app

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8002"))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
