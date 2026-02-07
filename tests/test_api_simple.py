"""Simple test script to verify Flask API endpoints using urllib."""

import urllib.request
import urllib.error
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"


def make_request(method, endpoint, data=None):
    """Make HTTP request using urllib."""
    url = f"{BASE_URL}{endpoint}"
    
    if data:
        data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header('Content-Type', 'application/json')
    else:
        req = urllib.request.Request(url, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))


def test_health():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    status, data = make_request('GET', '/health')
    print(f"Status: {status}")
    print(f"Response: {data}")
    assert status == 200
    print("✓ Health check passed")


def test_get_zones_empty():
    """Test getting zones when empty."""
    print("\n=== Testing GET /api/zones (empty) ===")
    status, data = make_request('GET', '/api/zones')
    print(f"Status: {status}")
    print(f"Response: {data}")
    assert status == 200
    assert isinstance(data, list)
    print("✓ Get zones (empty) passed")


def test_submit_report():
    """Test submitting an air impact report."""
    print("\n=== Testing POST /api/reports ===")
    
    report_data = {
        "type": "vape",
        "context": "indoor",
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
    }
    
    status, data = make_request('POST', '/api/reports', report_data)
    
    print(f"Status: {status}")
    print(f"Response: {json.dumps(data, indent=2)}")
    assert status == 201
    
    assert 'zone_id' in data
    assert 'suggestions' in data
    assert len(data['suggestions']) >= 3
    assert len(data['suggestions']) <= 5
    
    print("✓ Submit report passed")
    return data['zone_id'], data['suggestions'][0]


def test_get_zones_with_data():
    """Test getting zones after submitting a report."""
    print("\n=== Testing GET /api/zones (with data) ===")
    status, data = make_request('GET', '/api/zones')
    print(f"Status: {status}")
    
    print(f"Number of zones: {len(data)}")
    if len(data) > 0:
        print(f"First zone: {json.dumps(data[0], indent=2)}")
    
    assert status == 200
    assert len(data) > 0
    assert 'vape_state' in data[0]
    assert 'smoke_state' in data[0]
    
    print("✓ Get zones (with data) passed")


def test_complete_action(zone_id, action):
    """Test completing a restoration action."""
    print("\n=== Testing POST /api/actions ===")
    
    action_data = {
        "action_id": action['id'],
        "points": action['points'],
        "type": "vape",
        "zone_id": zone_id
    }
    
    status, data = make_request('POST', '/api/actions', action_data)
    
    print(f"Status: {status}")
    print(f"Response: {json.dumps(data, indent=2)}")
    assert status == 200
    
    assert 'total_points' in data
    assert 'feedback' in data
    assert data['total_points'] == action['points']
    
    print("✓ Complete action passed")


def test_get_points():
    """Test getting user points."""
    print("\n=== Testing GET /api/points ===")
    status, data = make_request('GET', '/api/points')
    print(f"Status: {status}")
    print(f"Response: {json.dumps(data, indent=2)}")
    assert status == 200
    
    assert 'total_points' in data
    assert 'actions_completed' in data
    
    print("✓ Get points passed")


def test_create_event():
    """Test creating a community event."""
    print("\n=== Testing POST /api/events ===")
    
    event_data = {
        "name": "Community Air Restoration Meetup",
        "location": "Central Park",
        "date_time": (datetime.now() + timedelta(days=7)).isoformat(),
        "duration": 60,
        "type_focus": "both",
        "context_hint": "outdoor"
    }
    
    status, data = make_request('POST', '/api/events', event_data)
    
    print(f"Status: {status}")
    print(f"Response: {json.dumps(data, indent=2)}")
    assert status == 201
    
    assert 'event' in data
    assert 'message' in data
    
    print("✓ Create event passed")


def test_get_events():
    """Test getting community events."""
    print("\n=== Testing GET /api/events ===")
    status, data = make_request('GET', '/api/events')
    print(f"Status: {status}")
    print(f"Response: {json.dumps(data, indent=2)}")
    assert status == 200
    
    assert isinstance(data, list)
    assert len(data) > 0
    
    print("✓ Get events passed")


def test_reset_all():
    """Test resetting all data."""
    print("\n=== Testing POST /api/reset ===")
    status, data = make_request('POST', '/api/reset')
    print(f"Status: {status}")
    print(f"Response: {data}")
    assert status == 200
    
    # Verify zones are cleared
    status, zones_data = make_request('GET', '/api/zones')
    assert len(zones_data) == 0
    
    # Verify points are reset
    status, points_data = make_request('GET', '/api/points')
    assert points_data['total_points'] == 0
    
    print("✓ Reset all data passed")


def run_all_tests():
    """Run all API tests."""
    print("=" * 60)
    print("BreatheBack API Test Suite")
    print("=" * 60)
    
    try:
        # First reset to ensure clean state
        print("\n=== Resetting data for clean test ===")
        make_request('POST', '/api/reset')
        
        # Run tests in order
        test_health()
        test_get_zones_empty()
        zone_id, action = test_submit_report()
        test_get_zones_with_data()
        test_complete_action(zone_id, action)
        test_get_points()
        test_create_event()
        test_get_events()
        test_reset_all()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    run_all_tests()
