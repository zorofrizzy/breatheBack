"""
Simplified Comprehensive Integration Test for Task 21 Checkpoint
Tests all components and integration flows for BreatheBack application
"""

import pytest
import json
from app import app
from backend.services.local_storage_service import LocalStorageService


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    storage = LocalStorageService()
    storage.clear_all_data()
    yield
    storage.clear_all_data()


def test_navigation_views_accessible(client):
    """Test 1: Navigation - All views accessible"""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'id="report-view"' in html
    assert 'id="heatmap-view"' in html
    assert 'id="community-view"' in html
    assert 'id="mypoints-view"' in html
    print("✓ All navigation views accessible")


def test_report_action_zone_flow(client):
    """Test 2: Report → Action → Zone Update Flow"""
    # Submit report
    report = {
        'type': 'vape',
        'context': 'indoor',
        'location': {'latitude': 37.7749, 'longitude': -122.4194}
    }
    resp = client.post('/api/reports', json=report)
    assert resp.status_code == 201
    zone_id = resp.json['zone_id']
    print(f"✓ Report submitted, zone: {zone_id}")
    
    # Verify zone debt
    zones = client.get('/api/zones').json
    zone = next(z for z in zones if z['id'] == zone_id)
    assert zone['vape_debt'] == 10
    print("✓ Zone debt increased")
    
    # Complete action
    action = {
        'action_id': 'indoor_1',
        'points': 10,
        'type': 'vape',
        'zone_id': zone_id
    }
    resp = client.post('/api/actions', json=action)
    assert resp.status_code == 200
    print("✓ Action completed")
    
    # Verify zone restoration
    zones = client.get('/api/zones').json
    zone = next(z for z in zones if z['id'] == zone_id)
    assert zone['vape_restore'] == 10
    print("✓ Zone restoration increased")
    
    # Verify points
    points = client.get('/api/points').json
    assert points['total_points'] == 10
    assert points['actions_completed'] == 1
    print("✓ User points increased")


def test_heatmap_toggle_and_zones(client):
    """Test 3: Heatmap Toggle and Zone Inspection"""
    # Create vape zone
    client.post('/api/reports', json={
        'type': 'vape',
        'location': {'latitude': 37.7749, 'longitude': -122.4194}
    })
    
    # Create smoke zone (further away to ensure different zone)
    client.post('/api/reports', json={
        'type': 'smoke',
        'location': {'latitude': 37.7850, 'longitude': -122.4295}
    })
    
    zones = client.get('/api/zones').json
    assert len(zones) >= 2, f"Expected at least 2 zones, got {len(zones)}"
    print(f"✓ Multiple zones created: {len(zones)}")
    
    # Verify data isolation
    vape_zone = next((z for z in zones if z['vape_debt'] > 0 and z['smoke_debt'] == 0), None)
    smoke_zone = next((z for z in zones if z['smoke_debt'] > 0 and z['vape_debt'] == 0), None)
    assert vape_zone is not None, "No vape-only zone found"
    assert smoke_zone is not None, "No smoke-only zone found"
    print("✓ Vape/smoke data isolated")
    
    # Verify zone structure
    zone = zones[0]
    assert all(k in zone for k in ['id', 'vape_debt', 'vape_restore', 'smoke_debt', 'smoke_restore'])
    print("✓ Zone structure correct")


def test_points_summary_and_reset(client):
    """Test 4: Points Summary and Daily Reset"""
    # Reset first to ensure clean state
    client.post('/api/reset')
    
    # Create a zone first
    resp = client.post('/api/reports', json={
        'type': 'vape',
        'location': {'latitude': 37.7749, 'longitude': -122.4194}
    })
    zone_id = resp.json['zone_id']
    
    # Complete multiple actions
    actions = [
        {'action_id': 'indoor_1', 'points': 10, 'type': 'vape', 'zone_id': zone_id},
        {'action_id': 'indoor_2', 'points': 5, 'type': 'vape', 'zone_id': zone_id},
        {'action_id': 'universal_1', 'points': 5, 'type': 'smoke', 'zone_id': zone_id}
    ]
    
    for action in actions:
        client.post('/api/actions', json=action)
    
    # Check accumulation
    points = client.get('/api/points').json
    assert points['total_points'] == 20, f"Expected 20 points, got {points['total_points']}"
    assert points['actions_completed'] == 3
    assert points['vape_points'] == 15
    assert points['smoke_points'] == 5
    print("✓ Points accumulated correctly")
    
    # Reset points
    client.post('/api/points/reset')
    points = client.get('/api/points').json
    assert points['total_points'] == 0
    assert points['actions_completed'] == 0
    print("✓ Points reset successfully")


def test_event_creation_and_display(client):
    """Test 5: Event Creation and Display"""
    # Create events
    events_data = [
        {
            'name': 'Morning Restoration',
            'location': 'North Zone',
            'date_time': '2026-02-15T09:00:00',
            'duration': 60,
            'type_focus': 'vape'
        },
        {
            'name': 'Evening Cleanup',
            'location': 'South Zone',
            'date_time': '2026-02-15T18:00:00',
            'duration': 90,
            'type_focus': 'smoke'
        }
    ]
    
    for event_data in events_data:
        resp = client.post('/api/events', json=event_data)
        assert resp.status_code == 201
        print(f"✓ Event created: {event_data['name']}")
    
    # Retrieve events
    events = client.get('/api/events').json
    assert len(events) >= 2
    print(f"✓ Events retrieved: {len(events)}")
    
    # Verify structure
    event = events[0]
    assert all(k in event for k in ['id', 'name', 'location', 'date_time', 'type_focus'])
    print("✓ Event structure correct")


def test_reset_functionality(client):
    """Test 6: Reset Functionality"""
    # Create data
    client.post('/api/reports', json={
        'type': 'vape',
        'location': {'latitude': 37.7749, 'longitude': -122.4194}
    })
    
    resp = client.post('/api/reports', json={
        'type': 'vape',
        'location': {'latitude': 37.7749, 'longitude': -122.4194}
    })
    zone_id = resp.json['zone_id']
    
    client.post('/api/actions', json={
        'action_id': 'indoor_1',
        'points': 10,
        'type': 'vape',
        'zone_id': zone_id
    })
    
    client.post('/api/events', json={
        'name': 'Test Event',
        'location': 'Test',
        'date_time': '2026-02-15T14:00:00',
        'duration': 60,
        'type_focus': 'both'
    })
    
    # Verify data exists
    assert len(client.get('/api/zones').json) > 0
    assert client.get('/api/points').json['total_points'] > 0
    assert len(client.get('/api/events').json) > 0
    print("✓ Data exists before reset")
    
    # Reset
    resp = client.post('/api/reset')
    assert resp.status_code == 200
    print("✓ Reset successful")
    
    # Verify cleared
    assert len(client.get('/api/zones').json) == 0
    assert client.get('/api/points').json['total_points'] == 0
    assert len(client.get('/api/events').json) == 0
    print("✓ All data cleared")


def test_complete_user_journey(client):
    """Test 7: Complete End-to-End User Journey"""
    # 1. Submit report
    resp = client.post('/api/reports', json={
        'type': 'vape',
        'context': 'indoor',
        'location': {'latitude': 37.7749, 'longitude': -122.4194}
    })
    zone_id = resp.json['zone_id']
    print("✓ Step 1: Report submitted")
    
    # 2. Complete action
    client.post('/api/actions', json={
        'action_id': 'indoor_1',
        'points': 10,
        'type': 'vape',
        'zone_id': zone_id
    })
    print("✓ Step 2: Action completed")
    
    # 3. View heatmap
    zones = client.get('/api/zones').json
    assert len(zones) > 0
    print("✓ Step 3: Heatmap viewed")
    
    # 4. View points
    points = client.get('/api/points').json
    assert points['total_points'] == 10
    print("✓ Step 4: Points viewed")
    
    # 5. Create event
    resp = client.post('/api/events', json={
        'name': 'Weekend Restoration',
        'location': 'Community Center',
        'date_time': '2026-02-15T10:00:00',
        'duration': 120,
        'type_focus': 'both'
    })
    assert resp.status_code == 201
    print("✓ Step 5: Event created")
    
    # 6. View events
    events = client.get('/api/events').json
    assert len(events) > 0
    print("✓ Step 6: Events viewed")
    
    print("✓ Complete user journey successful!")


def test_multiple_users_same_zone(client):
    """Test 8: Multiple Users Affecting Same Zone"""
    # Reset first to ensure clean state
    client.post('/api/reset')
    
    location = {'location': {'latitude': 37.7749, 'longitude': -122.4194}}
    
    # User 1 reports
    resp1 = client.post('/api/reports', json={'type': 'vape', **location})
    zone_id = resp1.json['zone_id']
    
    # User 2 reports
    client.post('/api/reports', json={'type': 'vape', **location})
    
    # Verify debt accumulated
    zones = client.get('/api/zones').json
    zone = next(z for z in zones if z['id'] == zone_id)
    assert zone['vape_debt'] == 20, f"Expected 20 debt, got {zone['vape_debt']}"
    print("✓ Debt accumulated from multiple reports")
    
    # User 1 completes action
    client.post('/api/actions', json={
        'action_id': 'indoor_1',
        'points': 10,
        'type': 'vape',
        'zone_id': zone_id
    })
    
    # User 2 completes action
    client.post('/api/actions', json={
        'action_id': 'indoor_2',
        'points': 5,
        'type': 'vape',
        'zone_id': zone_id
    })
    
    # Verify restoration accumulated
    zones = client.get('/api/zones').json
    zone = next(z for z in zones if z['id'] == zone_id)
    assert zone['vape_restore'] == 15, f"Expected 15 restore, got {zone['vape_restore']}"
    print("✓ Restoration accumulated from multiple actions")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
