"""
End-to-end test for Task 18: EventList and EventForm components
Tests the complete workflow of creating and viewing community events
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000'

def test_event_workflow():
    """Test complete event creation and retrieval workflow"""
    
    print("=" * 60)
    print("Task 18 End-to-End Test: Community Events")
    print("=" * 60)
    print()
    
    # Step 1: Clear existing events (reset)
    print("Step 1: Resetting application data...")
    response = requests.post(f'{BASE_URL}/api/reset')
    assert response.status_code == 200, "Reset should succeed"
    print("✓ Data reset successful")
    print()
    
    # Step 2: Verify no events exist
    print("Step 2: Verifying empty event list...")
    response = requests.get(f'{BASE_URL}/api/events')
    assert response.status_code == 200, "GET events should succeed"
    events = response.json()
    assert len(events) == 0, "Should have no events initially"
    print(f"✓ Event list is empty: {len(events)} events")
    print()
    
    # Step 3: Create first event (Vape focus, outdoor)
    print("Step 3: Creating vape-focused outdoor event...")
    event1_data = {
        'name': 'Community Air Healing Meetup',
        'location': 'Central Park',
        'date_time': (datetime.now() + timedelta(days=1)).isoformat(),
        'duration': 60,
        'type_focus': 'vape',
        'context_hint': 'outdoor'
    }
    response = requests.post(f'{BASE_URL}/api/events', json=event1_data)
    assert response.status_code == 201, "Event creation should succeed"
    result = response.json()
    assert 'event' in result, "Response should contain event"
    assert 'message' in result, "Response should contain confirmation message"
    event1_id = result['event']['id']
    print(f"✓ Event created: {result['event']['name']}")
    print(f"  ID: {event1_id}")
    print(f"  Message: {result['message']}")
    print()
    
    # Step 4: Create second event (Smoke focus, indoor)
    print("Step 4: Creating smoke-focused indoor event...")
    event2_data = {
        'name': 'Indoor Smoke Restoration Workshop',
        'location': 'Community Center',
        'date_time': (datetime.now() + timedelta(days=2)).isoformat(),
        'duration': 90,
        'type_focus': 'smoke',
        'context_hint': 'indoor'
    }
    response = requests.post(f'{BASE_URL}/api/events', json=event2_data)
    assert response.status_code == 201, "Event creation should succeed"
    result = response.json()
    event2_id = result['event']['id']
    print(f"✓ Event created: {result['event']['name']}")
    print(f"  ID: {event2_id}")
    print()
    
    # Step 5: Create third event (Both types, no context)
    print("Step 5: Creating event with both types...")
    event3_data = {
        'name': 'General Air Quality Initiative',
        'location': 'Downtown Area',
        'date_time': (datetime.now() + timedelta(days=3)).isoformat(),
        'duration': 120,
        'type_focus': 'both'
    }
    response = requests.post(f'{BASE_URL}/api/events', json=event3_data)
    assert response.status_code == 201, "Event creation should succeed"
    result = response.json()
    event3_id = result['event']['id']
    print(f"✓ Event created: {result['event']['name']}")
    print(f"  ID: {event3_id}")
    print()
    
    # Step 6: Retrieve all events and verify sorting
    print("Step 6: Retrieving and verifying event list...")
    response = requests.get(f'{BASE_URL}/api/events')
    assert response.status_code == 200, "GET events should succeed"
    events = response.json()
    assert len(events) == 3, f"Should have 3 events, got {len(events)}"
    print(f"✓ Retrieved {len(events)} events")
    print()
    
    # Step 7: Verify events are sorted by date
    print("Step 7: Verifying event sorting...")
    dates = [datetime.fromisoformat(e['date_time']) for e in events]
    assert dates == sorted(dates), "Events should be sorted by date"
    print("✓ Events are correctly sorted by date/time")
    for i, event in enumerate(events, 1):
        print(f"  {i}. {event['name']} - {event['date_time']}")
    print()
    
    # Step 8: Verify event details
    print("Step 8: Verifying event details...")
    
    # Check first event
    event1 = events[0]
    assert event1['name'] == event1_data['name'], "Event name should match"
    assert event1['location'] == event1_data['location'], "Location should match"
    assert event1['duration'] == event1_data['duration'], "Duration should match"
    assert event1['type_focus'] == event1_data['type_focus'], "Type focus should match"
    assert event1['context_hint'] == event1_data['context_hint'], "Context hint should match"
    assert 'description' in event1, "Event should have description"
    assert "We're meeting to help this area heal" in event1['description'], "Should have default description"
    print(f"✓ Event 1 details verified:")
    print(f"  Name: {event1['name']}")
    print(f"  Location: {event1['location']}")
    print(f"  Duration: {event1['duration']} minutes")
    print(f"  Type Focus: {event1['type_focus']}")
    print(f"  Context: {event1['context_hint']}")
    print()
    
    # Check second event
    event2 = events[1]
    assert event2['type_focus'] == 'smoke', "Second event should be smoke focus"
    assert event2['context_hint'] == 'indoor', "Second event should be indoor"
    print(f"✓ Event 2 details verified:")
    print(f"  Name: {event2['name']}")
    print(f"  Type Focus: {event2['type_focus']}")
    print(f"  Context: {event2['context_hint']}")
    print()
    
    # Check third event (no context hint)
    event3 = events[2]
    assert event3['type_focus'] == 'both', "Third event should have both types"
    assert event3['context_hint'] is None, "Third event should have no context hint"
    print(f"✓ Event 3 details verified:")
    print(f"  Name: {event3['name']}")
    print(f"  Type Focus: {event3['type_focus']}")
    print(f"  Context: {event3['context_hint']}")
    print()
    
    # Step 9: Test validation - missing required field
    print("Step 9: Testing validation (missing type_focus)...")
    invalid_data = {
        'name': 'Invalid Event',
        'location': 'Somewhere',
        'date_time': datetime.now().isoformat(),
        'duration': 60
    }
    response = requests.post(f'{BASE_URL}/api/events', json=invalid_data)
    assert response.status_code == 400, "Should fail validation"
    error = response.json()
    assert 'error' in error, "Should return error message"
    print(f"✓ Validation working: {error['error']}")
    print()
    
    # Step 10: Test validation - invalid type_focus
    print("Step 10: Testing validation (invalid type_focus)...")
    invalid_data = {
        'name': 'Invalid Event',
        'location': 'Somewhere',
        'date_time': datetime.now().isoformat(),
        'duration': 60,
        'type_focus': 'invalid'
    }
    response = requests.post(f'{BASE_URL}/api/events', json=invalid_data)
    assert response.status_code == 400, "Should fail validation"
    print("✓ Invalid type_focus rejected")
    print()
    
    # Summary
    print("=" * 60)
    print("✅ All Task 18 tests passed!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  - Created 3 events successfully")
    print(f"  - Verified event sorting by date/time")
    print(f"  - Verified all event details (name, location, duration, type, context)")
    print(f"  - Verified default description template")
    print(f"  - Verified validation for required fields")
    print(f"  - Verified validation for type_focus values")
    print()
    print("Task 18 implementation is complete and working correctly!")
    print()

if __name__ == '__main__':
    try:
        test_event_workflow()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
