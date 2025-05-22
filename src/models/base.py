from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base class for all game events."""
    event_id: UUID = Field(..., description="Unique identifier for the event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp in UTC")
    game_id: str = Field(..., description="Identifier for the game")
    player_id: str = Field(..., description="Unique identifier for the player")
    session_id: str = Field(..., description="Game session identifier")
    event_type: str = Field(..., description="Type of the event")
    version: str = Field(..., description="Event schema version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2023-11-01T12:00:00Z",
                "game_id": "game123",
                "player_id": "player456",
                "session_id": "session789",
                "event_type": "game_start",
                "version": "1.0"
            }
        }


class GameStartEvent(BaseEvent):
    """Event generated when a player starts a game."""
    device_info: Dict[str, str] = Field(..., description="Information about the player's device")
    client_version: str = Field(..., description="Version of the game client")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2023-11-01T12:00:00Z",
                "game_id": "game123",
                "player_id": "player456",
                "session_id": "session789",
                "event_type": "game_start",
                "version": "1.0",
                "device_info": {
                    "os": "iOS",
                    "model": "iPhone 12",
                    "os_version": "15.0"
                },
                "client_version": "2.1.0"
            }
        }


class GameEndEvent(BaseEvent):
    """Event generated when a player ends a game."""
    duration: int = Field(..., description="Duration of the game session in seconds")
    score: int = Field(..., description="Final score")
    level_reached: int = Field(..., description="Highest level reached")
    coins_earned: int = Field(..., description="Number of coins earned in the session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2023-11-01T12:00:00Z",
                "game_id": "game123",
                "player_id": "player456",
                "session_id": "session789",
                "event_type": "game_end",
                "version": "1.0",
                "duration": 300,
                "score": 1000,
                "level_reached": 5,
                "coins_earned": 150
            }
        }


class InGamePurchaseEvent(BaseEvent):
    """Event generated when a player makes an in-game purchase."""
    item_id: str = Field(..., description="Identifier of the purchased item")
    item_name: str = Field(..., description="Name of the purchased item")
    currency_type: str = Field(..., description="Type of currency used (real/virtual)")
    amount: float = Field(..., description="Amount spent")
    currency_code: str = Field(..., description="Currency code (USD, EUR, coins, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2023-11-01T12:00:00Z",
                "game_id": "game123",
                "player_id": "player456",
                "session_id": "session789",
                "event_type": "purchase",
                "version": "1.0",
                "item_id": "item123",
                "item_name": "Power Boost",
                "currency_type": "real",
                "amount": 0.99,
                "currency_code": "USD"
            }
        }


class PlayerProgressEvent(BaseEvent):
    """Event generated when a player makes progress in the game."""
    level: int = Field(..., description="Current level")
    xp_earned: int = Field(..., description="Experience points earned")
    achievements: List[str] = Field(default_factory=list, description="Achievements unlocked")
    current_state: Dict[str, Any] = Field(..., description="Current game state")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2023-11-01T12:00:00Z",
                "game_id": "game123",
                "player_id": "player456",
                "session_id": "session789",
                "event_type": "progress",
                "version": "1.0",
                "level": 5,
                "xp_earned": 100,
                "achievements": ["first_win", "speed_demon"],
                "current_state": {
                    "health": 100,
                    "coins": 1000,
                    "inventory": ["sword", "shield"]
                }
            }
        } 