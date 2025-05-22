import json
import uuid
from typing import Union

import boto3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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

# Initialize AWS clients
kinesis_client = boto3.client('kinesis')
STREAM_NAME = "game-events-stream"

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "game-analytics-api"}

@app.post("/events/game-start")
async def ingest_game_start(event: GameStartEvent):
    """Ingest game start events."""
    try:
        response = kinesis_client.put_record(
            StreamName=STREAM_NAME,
            Data=event.json(),
            PartitionKey=str(event.player_id)
        )
        return {
            "status": "success",
            "sequence_number": response["SequenceNumber"],
            "shard_id": response["ShardId"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/game-end")
async def ingest_game_end(event: GameEndEvent):
    """Ingest game end events."""
    try:
        response = kinesis_client.put_record(
            StreamName=STREAM_NAME,
            Data=event.json(),
            PartitionKey=str(event.player_id)
        )
        return {
            "status": "success",
            "sequence_number": response["SequenceNumber"],
            "shard_id": response["ShardId"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/purchase")
async def ingest_purchase(event: InGamePurchaseEvent):
    """Ingest in-game purchase events."""
    try:
        response = kinesis_client.put_record(
            StreamName=STREAM_NAME,
            Data=event.json(),
            PartitionKey=str(event.player_id)
        )
        return {
            "status": "success",
            "sequence_number": response["SequenceNumber"],
            "shard_id": response["ShardId"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/progress")
async def ingest_progress(event: PlayerProgressEvent):
    """Ingest player progress events."""
    try:
        response = kinesis_client.put_record(
            StreamName=STREAM_NAME,
            Data=event.json(),
            PartitionKey=str(event.player_id)
        )
        return {
            "status": "success",
            "sequence_number": response["SequenceNumber"],
            "shard_id": response["ShardId"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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