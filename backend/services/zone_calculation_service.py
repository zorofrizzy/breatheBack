"""Zone calculation service for geographic aggregation.

Handles conversion of coordinates to zone IDs and manages zone grid.
Requirements: 3.5, 3.6, 3.7
"""

import math
from typing import Dict, List
from datetime import datetime

from backend.models.zone import Zone, GeoBounds
from backend.constants import ZONE_GRID_SIZE


class ZoneCalculationService:
    """Service for calculating and managing geographic zones."""
    
    def __init__(self):
        """Initialize the zone calculation service."""
        self._zones: Dict[str, Zone] = {}
    
    def get_zone_id(self, latitude: float, longitude: float) -> str:
        """
        Convert coordinates to zone ID using grid calculation.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
        
        Returns:
            Zone ID string in format "zone_{latGrid}_{lngGrid}"
        
        Raises:
            ValueError: If coordinates are out of valid range
        
        Requirements: 3.5, 3.6
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
        
        # Calculate grid coordinates
        lat_grid = math.floor(latitude / ZONE_GRID_SIZE)
        lng_grid = math.floor(longitude / ZONE_GRID_SIZE)
        
        # Generate zone ID
        zone_id = f"zone_{lat_grid}_{lng_grid}"
        
        return zone_id
    
    def get_zone_bounds(self, zone_id: str) -> GeoBounds:
        """
        Get geographic boundaries for a zone ID.
        
        Args:
            zone_id: Zone ID in format "zone_{latGrid}_{lngGrid}"
        
        Returns:
            GeoBounds object with north, south, east, west boundaries
        
        Raises:
            ValueError: If zone_id format is invalid
        
        Requirements: 3.5, 3.6
        """
        # Parse zone ID
        parts = zone_id.split('_')
        if len(parts) != 3 or parts[0] != 'zone':
            raise ValueError(f"Invalid zone ID format: {zone_id}")
        
        try:
            lat_grid = int(parts[1])
            lng_grid = int(parts[2])
        except ValueError:
            raise ValueError(f"Invalid zone ID format: {zone_id}")
        
        # Calculate boundaries
        south = lat_grid * ZONE_GRID_SIZE
        north = (lat_grid + 1) * ZONE_GRID_SIZE
        west = lng_grid * ZONE_GRID_SIZE
        east = (lng_grid + 1) * ZONE_GRID_SIZE
        
        return GeoBounds(
            north=north,
            south=south,
            east=east,
            west=west
        )
    
    def create_zone(self, latitude: float, longitude: float) -> Zone:
        """
        Create a new zone for the given location.
        
        If a zone already exists for this location, returns the existing zone.
        Otherwise, creates a new zone with initial values.
        
        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
        
        Returns:
            Zone object (new or existing)
        
        Requirements: 3.5, 3.6, 3.7
        """
        # Get zone ID for this location
        zone_id = self.get_zone_id(latitude, longitude)
        
        # Return existing zone if it exists
        if zone_id in self._zones:
            return self._zones[zone_id]
        
        # Create new zone
        bounds = self.get_zone_bounds(zone_id)
        zone = Zone(
            id=zone_id,
            bounds=bounds,
            vape_debt=0.0,
            vape_restore=0.0,
            smoke_debt=0.0,
            smoke_restore=0.0,
            last_updated=datetime.utcnow()
        )
        
        # Store zone
        self._zones[zone_id] = zone
        
        return zone
    
    def get_all_zones(self) -> List[Zone]:
        """
        Retrieve all zones.
        
        Returns:
            List of all Zone objects
        
        Requirements: 3.7
        """
        return list(self._zones.values())
    
    def get_zone(self, zone_id: str) -> Zone:
        """
        Get a specific zone by ID.
        
        Args:
            zone_id: Zone ID to retrieve
        
        Returns:
            Zone object if found, None otherwise
        """
        return self._zones.get(zone_id)
    
    def clear_all_zones(self) -> None:
        """
        Clear all zones (for reset functionality).
        
        Requirements: 12.4
        """
        self._zones.clear()
