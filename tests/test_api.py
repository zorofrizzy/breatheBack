"""Simple test script to verify Flask API endpoints."""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"


def test_health():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed")


def test_get_zones_empty():
    """Test getting zones when empty."""
    print("\n=== Testing GET /api/zones (empty) ===")
    response = requests.get(f"{BASE_URL}/api/zones")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
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
    
    response = requests.post(
        f"{BASE_URL}/api/reports",
        json=report_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 201
    
    data = response.json()
    assert 'zone_id' in data
    assert 'suggestions' in data
    assert len(data['suggestions']) >= 3
    assert len(data['suggestions']) <= 5
    
    print("✓ Submit report passed")
    return data['zone_id'], data['suggestions'][0]


def test_get_zones_with_data():
    """Test getting zones after submitting a report."""
    print("\n=== Testing GET /api/zones (with data) ===")
    response = requests.get(f"{BASE_URL}/api/zones")
    print(f"Status: {response.status_code}")
    
    data = response.json()
    print(f"Number of zones: {len(data)}")
    if len(data) > 0:
        print(f"First zone: {json.dumps(data[0], indent=2)}")
    
    assert response.status_code == 200
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
    
    response = requests.post(
        f"{BASE_URL}/api/actions",
        json=action_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    
    data = response.json()
    assert 'total_points' in data
    assert 'feedback' in data
    assert data['total_points'] == action['points']
    
    print("✓ Complete action passed")


def test_get_points():
    """Test getting user points."""
    print("\n=== Testing GET /api/points ===")
    response = requests.get(f"{BASE_URL}/api/points")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    
    data = response.json()
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
    
    response = requests.post(
        f"{BASE_URL}/api/events",
        json=event_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 201
    
    data = response.json()
    assert 'event' in data
    assert 'message' in data
    
    print("✓ Create event passed")


def test_get_events():
    """Test getting community events."""
    print("\n=== Testing GET /api/events ===")
    response = requests.get(f"{BASE_URL}/api/events")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    print("✓ Get events passed")


def test_reset_all():
    """Test resetting all data."""
    print("\n=== Testing POST /api/reset ===")
    response = requests.post(f"{BASE_URL}/api/reset")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    
    # Verify zones are cleared
    zones_response = requests.get(f"{BASE_URL}/api/zones")
    assert len(zones_response.json()) == 0
    
    # Verify points are reset
    points_response = requests.get(f"{BASE_URL}/api/points")
    assert points_response.json()['total_points'] == 0
    
    print("✓ Reset all data passed")


def run_all_tests():
    """Run all API tests."""
    print("=" * 60)
    print("BreatheBack API Test Suite")
    print("=" * 60)
    
    try:
        # First reset to ensure clean state
        print("\n=== Resetting data for clean test ===")
        requests.post(f"{BASE_URL}/api/reset")
        
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
        return False
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to Flask server.")
        print("Make sure the server is running: python app.py")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        return False
    
    return True


if __name__ == "__main__":
    run_all_tests()
