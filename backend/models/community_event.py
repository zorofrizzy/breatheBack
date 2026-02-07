"""Community event data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class CommunityEvent:
    """
    Community event data model for scheduled restoration gatherings.
    
    Tracks event details including location, time, and focus type.
    
    PRIVACY CONTROLS (Requirement 11.5):
    - Location should be general area description (e.g., "Downtown", "North Park")
    - Location should NOT include specific venue names or addresses
    - No venue-specific details that could identify private spaces
    
    Requirements: 9.1, 9.2, 9.3, 11.5
    """
    id: str
    name: str
    location: str  # General area description, NOT specific venue
    date_time: datetime
    duration: int  # minutes
    type_focus: str  # 'vape', 'smoke', or 'both'
    description: str
    created_at: datetime
    context_hint: Optional[str] = None  # 'indoor' or 'outdoor'
    
    def __post_init__(self):
        """Initialize and validate event data."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        self.validate()
    
    def validate(self) -> None:
        """Validate community event data."""
        if not self.id:
            raise ValueError("Event ID is required")
        if not self.name:
            raise ValueError("Event name is required")
        if not self.location:
            raise ValueError("Event location is required")
        if not self.date_time:
            raise ValueError("Event date and time is required")
        if self.duration <= 0:
            raise ValueError("Duration must be positive")
        if self.type_focus not in ['vape', 'smoke', 'both']:
            raise ValueError("Type focus must be 'vape', 'smoke', or 'both'")
        if self.context_hint and self.context_hint not in ['indoor', 'outdoor']:
            raise ValueError("Context hint must be 'indoor' or 'outdoor'")
        if not self.description:
            raise ValueError("Event description is required")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'date_time': self.date_time.isoformat(),
            'duration': self.duration,
            'type_focus': self.type_focus,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'context_hint': self.context_hint
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommunityEvent':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            location=data['location'],
            date_time=datetime.fromisoformat(data['date_time']),
            duration=data['duration'],
            type_focus=data['type_focus'],
            description=data['description'],
            created_at=datetime.fromisoformat(data['created_at']),
            context_hint=data.get('context_hint')
        )
