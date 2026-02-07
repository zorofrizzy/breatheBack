"""Verification script for data model serialization/deserialization."""

import json
from datetime import datetime

from backend.models.zone import Zone, GeoBounds
from backend.models.user_points import UserPoints, CompletedAction
from backend.models.community_event import CommunityEvent
from backend.models.air_impact_report import AirImpactReport, Coordinates


def verify_zone_serialization():
    """Verify Zone model serialization."""
    print("Testing Zone serialization...")
    
    # Create a zone
    bounds = GeoBounds(north=37.78, south=37.77, east=-122.40, west=-122.41)
    zone = Zone(
        id="zone_3777_-12241",
        bounds=bounds,
        vape_debt=10.0,
        vape_restore=5.0,
        smoke_debt=20.0,
        smoke_restore=15.0
    )
    
    # Serialize
    zone_dict = zone.to_dict()
    zone_json = json.dumps(zone_dict)
    
    # Deserialize
    zone_dict_loaded = json.loads(zone_json)
    zone_loaded = Zone.from_dict(zone_dict_loaded)
    
    # Verify
    assert zone.id == zone_loaded.id
    assert zone.vape_debt == zone_loaded.vape_debt
    assert zone.vape_restore == zone_loaded.vape_restore
    assert zone.smoke_debt == zone_loaded.smoke_debt
    assert zone.smoke_restore == zone_loaded.smoke_restore
    
    print("✓ Zone serialization works correctly")


def verify_user_points_serialization():
    """Verify UserPoints model serialization."""
    print("Testing UserPoints serialization...")
    
    # Create user points
    action = CompletedAction(
        action_id="action_1",
        timestamp=datetime.now(),
        points=10,
        type="vape",
        zone_id="zone_3777_-12241"
    )
    
    user_points = UserPoints(
        date="2026-02-06",
        total_points=10,
        actions_completed=1,
        vape_points=10,
        smoke_points=0,
        actions=[action]
    )
    
    # Serialize
    points_dict = user_points.to_dict()
    points_json = json.dumps(points_dict)
    
    # Deserialize
    points_dict_loaded = json.loads(points_json)
    points_loaded = UserPoints.from_dict(points_dict_loaded)
    
    # Verify
    assert user_points.date == points_loaded.date
    assert user_points.total_points == points_loaded.total_points
    assert user_points.actions_completed == points_loaded.actions_completed
    assert len(user_points.actions) == len(points_loaded.actions)
    
    print("✓ UserPoints serialization works correctly")


def verify_community_event_serialization():
    """Verify CommunityEvent model serialization."""
    print("Testing CommunityEvent serialization...")
    
    # Create event
    event = CommunityEvent(
        id="event_1",
        name="Community Cleanup",
        location="Downtown Park",
        date_time=datetime(2026, 2, 10, 14, 0),
        duration=120,
        type_focus="both",
        description="Let's help the air heal together",
        created_at=datetime.now(),
        context_hint="outdoor"
    )
    
    # Serialize
    event_dict = event.to_dict()
    event_json = json.dumps(event_dict)
    
    # Deserialize
    event_dict_loaded = json.loads(event_json)
    event_loaded = CommunityEvent.from_dict(event_dict_loaded)
    
    # Verify
    assert event.id == event_loaded.id
    assert event.name == event_loaded.name
    assert event.location == event_loaded.location
    assert event.type_focus == event_loaded.type_focus
    assert event.context_hint == event_loaded.context_hint
    
    print("✓ CommunityEvent serialization works correctly")


def verify_air_impact_report_serialization():
    """Verify AirImpactReport model serialization."""
    print("Testing AirImpactReport serialization...")
    
    # Create report
    coords = Coordinates(latitude=37.7749, longitude=-122.4194)
    report = AirImpactReport(
        type="vape",
        location=coords,
        timestamp=datetime.now(),
        context="indoor"
    )
    
    # Serialize
    report_dict = report.to_dict()
    report_json = json.dumps(report_dict)
    
    # Deserialize
    report_dict_loaded = json.loads(report_json)
    report_loaded = AirImpactReport.from_dict(report_dict_loaded)
    
    # Verify
    assert report.type == report_loaded.type
    assert report.location.latitude == report_loaded.location.latitude
    assert report.location.longitude == report_loaded.location.longitude
    assert report.context == report_loaded.context
    
    print("✓ AirImpactReport serialization works correctly")


if __name__ == "__main__":
    print("\n=== Verifying Data Model Serialization ===\n")
    
    verify_zone_serialization()
    verify_user_points_serialization()
    verify_community_event_serialization()
    verify_air_impact_report_serialization()
    
    print("\n✓ All data models serialize/deserialize correctly!\n")
