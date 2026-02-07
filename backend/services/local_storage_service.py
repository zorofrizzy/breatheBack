"""Local storage service for persisting application data to JSON files."""

import json
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pathlib import Path

from backend.models.zone import Zone
from backend.models.user_points import UserPoints
from backend.models.community_event import CommunityEvent


class LocalStorageService:
    """
    Service for managing local file-based storage of application data.
    
    Handles persistence of zones, user points, and community events using JSON files.
    Requirements: 8.3, 12.2, 12.4
    """
    
    def __init__(self, storage_dir: str = "data"):
        """
        Initialize the local storage service.
        
        Args:
            storage_dir: Directory path for storing data files
        """
        self.storage_dir = Path(storage_dir)
        self.zones_file = self.storage_dir / "zones.json"
        self.points_file = self.storage_dir / "user_points.json"
        self.events_file = self.storage_dir / "events.json"
        
        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_zones(self, zones: List[Zone]) -> None:
        """
        Save zones to JSON file.
        
        Args:
            zones: List of Zone objects to save
            
        Raises:
            IOError: If file write fails
            ValueError: If zone data is invalid
        """
        try:
            # Validate all zones before saving
            for zone in zones:
                zone.validate()
            
            # Convert zones to dictionaries
            zones_data = [zone.to_dict() for zone in zones]
            
            # Write to file with pretty formatting
            with open(self.zones_file, 'w') as f:
                json.dump(zones_data, f, indent=2)
                
        except Exception as e:
            raise IOError(f"Failed to save zones: {str(e)}")
    
    def load_zones(self) -> List[Zone]:
        """
        Load zones from JSON file with error handling.
        
        Returns:
            List of Zone objects, empty list if file doesn't exist or is invalid
        """
        try:
            # Return empty list if file doesn't exist
            if not self.zones_file.exists():
                return []
            
            # Read and parse JSON file
            with open(self.zones_file, 'r') as f:
                zones_data = json.load(f)
            
            # Convert dictionaries to Zone objects
            zones = [Zone.from_dict(data) for data in zones_data]
            
            return zones
            
        except json.JSONDecodeError as e:
            # Log error and return empty list for corrupted files
            print(f"Warning: Corrupted zones file, returning empty list: {str(e)}")
            return []
        except Exception as e:
            # Log error and return empty list for other errors
            print(f"Warning: Failed to load zones, returning empty list: {str(e)}")
            return []
    
    def save_user_points(self, points: UserPoints) -> None:
        """
        Save user points to JSON file.
        
        Args:
            points: UserPoints object to save
            
        Raises:
            IOError: If file write fails
            ValueError: If points data is invalid
        """
        try:
            # Validate points before saving
            points.validate()
            
            # Convert to dictionary
            points_data = points.to_dict()
            
            # Write to file with pretty formatting
            with open(self.points_file, 'w') as f:
                json.dump(points_data, f, indent=2)
                
        except Exception as e:
            raise IOError(f"Failed to save user points: {str(e)}")
    
    def load_user_points(self) -> UserPoints:
        """
        Load user points from JSON file with daily reset check.
        
        Automatically resets points if the stored date doesn't match today's date.
        Requirement: 8.3 - Daily points reset at midnight
        
        Returns:
            UserPoints object for today, new object if file doesn't exist or date changed
        """
        try:
            # Get today's date in ISO format
            today = date.today().isoformat()
            
            # Return new UserPoints if file doesn't exist
            if not self.points_file.exists():
                return UserPoints(date=today)
            
            # Read and parse JSON file
            with open(self.points_file, 'r') as f:
                points_data = json.load(f)
            
            # Load points from data
            points = UserPoints.from_dict(points_data)
            
            # Check if date has changed (daily reset)
            if points.date != today:
                # Date changed, return new UserPoints for today
                return UserPoints(date=today)
            
            return points
            
        except json.JSONDecodeError as e:
            # Log error and return new UserPoints for corrupted files
            print(f"Warning: Corrupted points file, creating new: {str(e)}")
            return UserPoints(date=date.today().isoformat())
        except Exception as e:
            # Log error and return new UserPoints for other errors
            print(f"Warning: Failed to load user points, creating new: {str(e)}")
            return UserPoints(date=date.today().isoformat())
    
    def save_events(self, events: List[CommunityEvent]) -> None:
        """
        Save community events to JSON file.
        
        Args:
            events: List of CommunityEvent objects to save
            
        Raises:
            IOError: If file write fails
            ValueError: If event data is invalid
        """
        try:
            # Validate all events before saving
            for event in events:
                event.validate()
            
            # Convert events to dictionaries
            events_data = [event.to_dict() for event in events]
            
            # Write to file with pretty formatting
            with open(self.events_file, 'w') as f:
                json.dump(events_data, f, indent=2)
                
        except Exception as e:
            raise IOError(f"Failed to save events: {str(e)}")
    
    def load_events(self) -> List[CommunityEvent]:
        """
        Load community events from JSON file with error handling.
        
        Returns:
            List of CommunityEvent objects, empty list if file doesn't exist or is invalid
        """
        try:
            # Return empty list if file doesn't exist
            if not self.events_file.exists():
                return []
            
            # Read and parse JSON file
            with open(self.events_file, 'r') as f:
                events_data = json.load(f)
            
            # Convert dictionaries to CommunityEvent objects
            events = [CommunityEvent.from_dict(data) for data in events_data]
            
            return events
            
        except json.JSONDecodeError as e:
            # Log error and return empty list for corrupted files
            print(f"Warning: Corrupted events file, returning empty list: {str(e)}")
            return []
        except Exception as e:
            # Log error and return empty list for other errors
            print(f"Warning: Failed to load events, returning empty list: {str(e)}")
            return []
    
    def clear_all_data(self) -> None:
        """
        Clear all stored data by deleting all data files.
        
        Used for reset functionality.
        Requirement: 12.2, 12.4 - Reset function clears all data
        """
        try:
            # Delete zones file if it exists
            if self.zones_file.exists():
                self.zones_file.unlink()
            
            # Delete points file if it exists
            if self.points_file.exists():
                self.points_file.unlink()
            
            # Delete events file if it exists
            if self.events_file.exists():
                self.events_file.unlink()
                
        except Exception as e:
            raise IOError(f"Failed to clear data: {str(e)}")
