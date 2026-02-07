"""User points data model for tracking daily contributions."""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class CompletedAction:
    """Record of a completed restoration action."""
    action_id: str
    timestamp: datetime
    points: int
    type: str  # 'vape' or 'smoke'
    zone_id: str
    
    def validate(self) -> None:
        """Validate completed action data."""
        if not self.action_id:
            raise ValueError("Action ID is required")
        if self.points < 0:
            raise ValueError("Points cannot be negative")
        if self.type not in ['vape', 'smoke', 'both']:
            raise ValueError("Type must be 'vape', 'smoke', or 'both'")
        if not self.zone_id:
            raise ValueError("Zone ID is required")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'action_id': self.action_id,
            'timestamp': self.timestamp.isoformat(),
            'points': self.points,
            'type': self.type,
            'zone_id': self.zone_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompletedAction':
        """Create from dictionary."""
        return cls(
            action_id=data['action_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            points=data['points'],
            type=data['type'],
            zone_id=data['zone_id']
        )


@dataclass
class UserPoints:
    """
    User points data model for daily contribution tracking.
    
    Tracks total points, action count, and breakdown by type.
    """
    date: str  # ISO date string (YYYY-MM-DD)
    total_points: int = 0
    actions_completed: int = 0
    vape_points: int = 0
    smoke_points: int = 0
    actions: List[CompletedAction] = field(default_factory=list)
    
    def validate(self) -> None:
        """Validate user points data."""
        if not self.date:
            raise ValueError("Date is required")
        
        # Validate date format
        try:
            datetime.fromisoformat(self.date)
        except ValueError:
            raise ValueError("Date must be in ISO format (YYYY-MM-DD)")
        
        if self.total_points < 0:
            raise ValueError("Total points cannot be negative")
        if self.actions_completed < 0:
            raise ValueError("Actions completed cannot be negative")
        if self.vape_points < 0:
            raise ValueError("Vape points cannot be negative")
        if self.smoke_points < 0:
            raise ValueError("Smoke points cannot be negative")
        
        # Note: vape_points + smoke_points can be greater than total_points
        # when "both" actions are completed (they count towards both categories)
        # So we only validate that the sum is at least the total
        if self.vape_points + self.smoke_points < self.total_points:
            raise ValueError("Vape points + smoke points cannot be less than total points")
        
        # Validate actions count matches list length
        if len(self.actions) != self.actions_completed:
            raise ValueError("Actions completed must match actions list length")
        
        # Validate each action
        for action in self.actions:
            action.validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'date': self.date,
            'total_points': self.total_points,
            'actions_completed': self.actions_completed,
            'vape_points': self.vape_points,
            'smoke_points': self.smoke_points,
            'actions': [action.to_dict() for action in self.actions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPoints':
        """Create from dictionary."""
        actions = [CompletedAction.from_dict(a) for a in data.get('actions', [])]
        return cls(
            date=data['date'],
            total_points=data.get('total_points', 0),
            actions_completed=data.get('actions_completed', 0),
            vape_points=data.get('vape_points', 0),
            smoke_points=data.get('smoke_points', 0),
            actions=actions
        )
