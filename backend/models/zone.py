"""Zone data model for geographic aggregation."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any


@dataclass
class GeoBounds:
    """Geographic boundaries for a zone."""
    north: float
    south: float
    east: float
    west: float
    
    def validate(self) -> None:
        """Validate geographic bounds."""
        if not (-90 <= self.south <= 90 and -90 <= self.north <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= self.west <= 180 and -180 <= self.east <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if self.south > self.north:
            raise ValueError("South latitude must be less than or equal to north latitude")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Zone:
    """
    Zone data model for aggregated geographic area.
    
    Maintains separate tracking for vape and smoke impacts.
    
    PRIVACY CONTROLS (Requirements 10.4, 10.5):
    - Context information is NOT stored in zones
    - Only aggregated debt and restoration scores are stored
    - No individual report data or identifying information
    
    Requirements: 10.1, 13.3, 13.4, 13.5
    """
    id: str
    bounds: GeoBounds
    vape_debt: float = 0.0
    vape_restore: float = 0.0
    smoke_debt: float = 0.0
    smoke_restore: float = 0.0
    last_updated: datetime = None
    
    def __post_init__(self):
        """Initialize and validate zone data."""
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()
        self.validate()
    
    def validate(self) -> None:
        """Validate zone data."""
        if not self.id:
            raise ValueError("Zone ID is required")
        
        if not isinstance(self.bounds, GeoBounds):
            raise ValueError("Bounds must be a GeoBounds instance")
        
        self.bounds.validate()
        
        if self.vape_debt < 0:
            raise ValueError("Vape debt cannot be negative")
        if self.vape_restore < 0:
            raise ValueError("Vape restore cannot be negative")
        if self.smoke_debt < 0:
            raise ValueError("Smoke debt cannot be negative")
        if self.smoke_restore < 0:
            raise ValueError("Smoke restore cannot be negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert zone to dictionary."""
        return {
            'id': self.id,
            'bounds': self.bounds.to_dict(),
            'vape_debt': self.vape_debt,
            'vape_restore': self.vape_restore,
            'smoke_debt': self.smoke_debt,
            'smoke_restore': self.smoke_restore,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Zone':
        """Create zone from dictionary."""
        bounds_data = data['bounds']
        bounds = GeoBounds(**bounds_data)
        
        return cls(
            id=data['id'],
            bounds=bounds,
            vape_debt=data.get('vape_debt', 0.0),
            vape_restore=data.get('vape_restore', 0.0),
            smoke_debt=data.get('smoke_debt', 0.0),
            smoke_restore=data.get('smoke_restore', 0.0),
            last_updated=datetime.fromisoformat(data['last_updated'])
        )
