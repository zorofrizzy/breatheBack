"""Unit tests for ZoneCalculationService.

Tests the zone calculation service functionality.
"""

import pytest
from backend.services.zone_calculation_service import ZoneCalculationService
from backend.models.zone import GeoBounds


def test_get_zone_id_basic():
    """Test basic zone ID generation."""
    service = ZoneCalculationService()
    
    # Test positive coordinates
    zone_id = service.get_zone_id(37.7749, -122.4194)  # San Francisco
    assert zone_id.startswith("zone_")
    assert "_" in zone_id
    
    # Test that same coordinates produce same zone ID
    zone_id2 = service.get_zone_id(37.7749, -122.4194)
    assert zone_id == zone_id2


def test_get_zone_id_grid_calculation():
    """Test zone ID grid calculation logic."""
    service = ZoneCalculationService()
    
    # Test coordinates in same grid cell produce same zone ID
    # Grid size is 0.01, for negative coordinates floor rounds down
    # -122.41 / 0.01 = -12241, floor(-12241) = -12241
    # -122.4099 / 0.01 = -12240.99, floor(-12240.99) = -12241
    zone_id1 = service.get_zone_id(37.7700, -122.4100)
    zone_id2 = service.get_zone_id(37.7709, -122.4099)  # Within same grid cell
    assert zone_id1 == zone_id2
    
    # Test coordinates in different grid cells produce different zone IDs
    zone_id3 = service.get_zone_id(37.7800, -122.4100)
    assert zone_id1 != zone_id3


def test_get_zone_id_validation():
    """Test coordinate validation."""
    service = ZoneCalculationService()
    
    # Test invalid latitude
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        service.get_zone_id(91.0, 0.0)
    
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        service.get_zone_id(-91.0, 0.0)
    
    # Test invalid longitude
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        service.get_zone_id(0.0, 181.0)
    
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        service.get_zone_id(0.0, -181.0)


def test_get_zone_bounds():
    """Test zone bounds calculation."""
    service = ZoneCalculationService()
    
    # Get zone ID and bounds
    zone_id = service.get_zone_id(37.7749, -122.4194)
    bounds = service.get_zone_bounds(zone_id)
    
    # Verify bounds is GeoBounds instance
    assert isinstance(bounds, GeoBounds)
    
    # Verify bounds are valid
    assert bounds.south < bounds.north
    assert bounds.west < bounds.east
    
    # Verify the original coordinates fall within bounds
    assert bounds.south <= 37.7749 < bounds.north
    assert bounds.west <= -122.4194 < bounds.east


def test_get_zone_bounds_invalid_format():
    """Test zone bounds with invalid zone ID format."""
    service = ZoneCalculationService()
    
    # Test invalid format
    with pytest.raises(ValueError, match="Invalid zone ID format"):
        service.get_zone_bounds("invalid_zone")
    
    with pytest.raises(ValueError, match="Invalid zone ID format"):
        service.get_zone_bounds("zone_abc_def")


def test_create_zone():
    """Test zone creation."""
    service = ZoneCalculationService()
    
    # Create a zone
    zone = service.create_zone(37.7749, -122.4194)
    
    # Verify zone properties
    assert zone.id.startswith("zone_")
    assert zone.vape_debt == 0.0
    assert zone.vape_restore == 0.0
    assert zone.smoke_debt == 0.0
    assert zone.smoke_restore == 0.0
    assert zone.last_updated is not None


def test_create_zone_idempotent():
    """Test that creating a zone twice returns the same zone."""
    service = ZoneCalculationService()
    
    # Create zone twice
    zone1 = service.create_zone(37.7749, -122.4194)
    zone2 = service.create_zone(37.7749, -122.4194)
    
    # Should be the same zone object
    assert zone1 is zone2
    assert zone1.id == zone2.id


def test_get_all_zones():
    """Test retrieving all zones."""
    service = ZoneCalculationService()
    
    # Initially empty
    zones = service.get_all_zones()
    assert len(zones) == 0
    
    # Create some zones
    service.create_zone(37.7749, -122.4194)
    service.create_zone(40.7128, -74.0060)
    service.create_zone(51.5074, -0.1278)
    
    # Should have 3 zones
    zones = service.get_all_zones()
    assert len(zones) == 3


def test_get_zone():
    """Test getting a specific zone by ID."""
    service = ZoneCalculationService()
    
    # Create a zone
    created_zone = service.create_zone(37.7749, -122.4194)
    
    # Get the zone by ID
    retrieved_zone = service.get_zone(created_zone.id)
    
    # Should be the same zone
    assert retrieved_zone is created_zone
    
    # Non-existent zone should return None
    assert service.get_zone("zone_999_999") is None


def test_clear_all_zones():
    """Test clearing all zones."""
    service = ZoneCalculationService()
    
    # Create some zones
    service.create_zone(37.7749, -122.4194)
    service.create_zone(40.7128, -74.0060)
    
    # Verify zones exist
    assert len(service.get_all_zones()) == 2
    
    # Clear all zones
    service.clear_all_zones()
    
    # Verify zones are cleared
    assert len(service.get_all_zones()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
