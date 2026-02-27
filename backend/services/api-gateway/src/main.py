from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="AUGUR API Gateway")

@app.get("/")
async def root():
    return {
        "service": "AUGUR Enterprise Platform",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
