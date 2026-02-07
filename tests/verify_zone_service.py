"""Simple verification script for ZoneCalculationService."""

from backend.services.zone_calculation_service import ZoneCalculationService


def verify_zone_service():
    """Verify the zone calculation service works correctly."""
    print("Testing ZoneCalculationService...")
    
    service = ZoneCalculationService()
    
    # Test 1: get_zone_id
    print("\n1. Testing get_zone_id...")
    zone_id = service.get_zone_id(37.7749, -122.4194)
    print(f"   Zone ID for San Francisco (37.7749, -122.4194): {zone_id}")
    assert zone_id.startswith("zone_"), "Zone ID should start with 'zone_'"
    
    # Test same coordinates produce same zone ID
    zone_id2 = service.get_zone_id(37.7749, -122.4194)
    assert zone_id == zone_id2, "Same coordinates should produce same zone ID"
    print("   ✓ Same coordinates produce same zone ID")
    
    # Test 2: get_zone_bounds
    print("\n2. Testing get_zone_bounds...")
    bounds = service.get_zone_bounds(zone_id)
    print(f"   Bounds: N={bounds.north}, S={bounds.south}, E={bounds.east}, W={bounds.west}")
    assert bounds.south < bounds.north, "South should be less than North"
    assert bounds.west < bounds.east, "West should be less than East"
    assert bounds.south <= 37.7749 < bounds.north, "Latitude should be within bounds"
    assert bounds.west <= -122.4194 < bounds.east, "Longitude should be within bounds"
    print("   ✓ Bounds are valid and contain original coordinates")
    
    # Test 3: create_zone
    print("\n3. Testing create_zone...")
    zone = service.create_zone(40.7128, -74.0060)  # New York
    print(f"   Created zone: {zone.id}")
    assert zone.vape_debt == 0.0, "Initial vape debt should be 0"
    assert zone.smoke_debt == 0.0, "Initial smoke debt should be 0"
    assert zone.vape_restore == 0.0, "Initial vape restore should be 0"
    assert zone.smoke_restore == 0.0, "Initial smoke restore should be 0"
    print("   ✓ Zone created with correct initial values")
    
    # Test idempotency
    zone2 = service.create_zone(40.7128, -74.0060)
    assert zone is zone2, "Creating same zone twice should return same object"
    print("   ✓ Zone creation is idempotent")
    
    # Test 4: get_all_zones
    print("\n4. Testing get_all_zones...")
    service.create_zone(51.5074, -0.1278)  # London
    zones = service.get_all_zones()
    print(f"   Total zones: {len(zones)}")
    assert len(zones) == 2, "Should have 2 zones (NY and London)"
    print("   ✓ get_all_zones returns correct count")
    
    # Test 5: get_zone
    print("\n5. Testing get_zone...")
    retrieved = service.get_zone(zone.id)
    assert retrieved is zone, "Retrieved zone should be same object"
    print("   ✓ get_zone retrieves correct zone")
    
    # Test 6: clear_all_zones
    print("\n6. Testing clear_all_zones...")
    service.clear_all_zones()
    zones = service.get_all_zones()
    assert len(zones) == 0, "All zones should be cleared"
    print("   ✓ clear_all_zones works correctly")
    
    # Test 7: Validation
    print("\n7. Testing coordinate validation...")
    try:
        service.get_zone_id(91.0, 0.0)
        assert False, "Should raise ValueError for invalid latitude"
    except ValueError as e:
        print(f"   ✓ Invalid latitude rejected: {e}")
    
    try:
        service.get_zone_id(0.0, 181.0)
        assert False, "Should raise ValueError for invalid longitude"
    except ValueError as e:
        print(f"   ✓ Invalid longitude rejected: {e}")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    verify_zone_service()
