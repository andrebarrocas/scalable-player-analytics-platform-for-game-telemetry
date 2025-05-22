import json
import uuid
from typing import Union, Dict, Any, Optional
from datetime import datetime
import os

import boto3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.models.base import (
    GameStartEvent,
    GameEndEvent,
    InGamePurchaseEvent,
    PlayerProgressEvent
)

app = FastAPI(
    title="Game Analytics API",
    description="API for ingesting game telemetry data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure AWS client for LocalStack
endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

kinesis = boto3.client(
    'kinesis',
    endpoint_url=endpoint_url,
    region_name=aws_region,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

class GameEvent(BaseModel):
    event_id: str
    timestamp: str
    game_id: str
    player_id: str
    session_id: str
    event_type: str
    version: str
    device_info: Optional[Dict[str, Any]] = None
    client_version: Optional[str] = None
    duration: Optional[int] = None
    score: Optional[int] = None
    level_reached: Optional[int] = None
    coins_earned: Optional[int] = None
    item_id: Optional[str] = None
    item_name: Optional[str] = None
    currency_type: Optional[str] = None
    amount: Optional[float] = None
    currency_code: Optional[str] = None
    level: Optional[int] = None
    xp_earned: Optional[int] = None
    achievements: Optional[list] = None
    current_state: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "game-analytics-api"}

@app.post("/events/{event_type}")
async def ingest_event(event_type: str, event: GameEvent):
    """
    Ingest a game event into the appropriate Kinesis stream.
    """
    try:
        # Validate event type
        if event_type not in ["game-start", "game-end", "purchase", "progress"]:
            raise HTTPException(status_code=400, detail="Invalid event type")

        # Add server timestamp
        event_data = event.model_dump()
        event_data["server_timestamp"] = datetime.utcnow().isoformat()

        # Send to appropriate Kinesis stream
        stream_name = "game-events-stream"
        
        response = kinesis.put_record(
            StreamName=stream_name,
            Data=json.dumps(event_data),
            PartitionKey=event.player_id
        )

        return {
            "status": "success",
            "sequence_number": response["SequenceNumber"],
            "shard_id": response["ShardId"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    try:
        # Check Kinesis connection
        kinesis.list_streams()
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/metrics/player/{player_id}")
async def get_player_metrics(player_id: str):
    """Get player metrics (placeholder for future implementation)."""
    # This would typically query our data warehouse or real-time analytics
    return {
        "player_id": player_id,
        "total_sessions": 0,
        "total_playtime": 0,
        "average_session_duration": 0,
        "total_spend": 0,
        "favorite_items": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 