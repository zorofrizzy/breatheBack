"""Air impact report data model (transient)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Coordinates:
    """Geographic coordinates."""
    latitude: float
    longitude: float
    
    def validate(self) -> None:
        """Validate coordinates."""
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude
        }


@dataclass
class AirImpactReport:
    """
    Air impact report data model (transient).
    
    Reports are immediately processed and not stored to ensure privacy.
    
    PRIVACY CONTROLS (Requirements 10.4, 10.5):
    - Context is used ONLY for action suggestions
    - Context is NOT stored in zone data
    - Context is NOT displayed in public views
    - Reports are transient and discarded after processing
    
    Requirements: 3.1, 3.2, 3.3, 10.4, 10.5, 11.1, 11.3
    """
    type: str  # 'smoke' or 'vape'
    location: Coordinates
    timestamp: datetime
    context: Optional[str] = None  # 'indoor' or 'outdoor' - used ONLY for action suggestions
    
    def __post_init__(self):
        """Initialize and validate report data."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        self.validate()
    
    def validate(self) -> None:
        """Validate air impact report data."""
        if self.type not in ['smoke', 'vape']:
            raise ValueError("Type must be 'smoke' or 'vape'")
        
        if not isinstance(self.location, Coordinates):
            raise ValueError("Location must be a Coordinates instance")
        
        self.location.validate()
        
        if self.context and self.context not in ['indoor', 'outdoor']:
            raise ValueError("Context must be 'indoor' or 'outdoor'")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'type': self.type,
            'location': self.location.to_dict(),
            'timestamp': self.timestamp.isoformat(),
            'context': self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AirImpactReport':
        """Create from dictionary."""
        location = Coordinates(**data['location'])
        return cls(
            type=data['type'],
            location=location,
            timestamp=datetime.fromisoformat(data['timestamp']),
            context=data.get('context')
        )
