"""Test event API endpoints"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000'

# Test 1: Get events (should be empty initially)
print("Test 1: Get events")
response = requests.get(f'{BASE_URL}/api/events')
print(f"Status: {response.status_code}")
print(f"Events: {response.json()}")
print()

# Test 2: Create an event
print("Test 2: Create an event")
event_data = {
    'name': 'Community Air Healing Meetup',
    'location': 'Central Park',
    'date_time': (datetime.now() + timedelta(days=1)).isoformat(),
    'duration': 60,
    'type_focus': 'both',
    'context_hint': 'outdoor'
}
response = requests.post(f'{BASE_URL}/api/events', json=event_data)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Message: {result.get('message')}")
print(f"Event ID: {result.get('event', {}).get('id')}")
print()

# Test 3: Get events again (should have one event)
print("Test 3: Get events after creation")
response = requests.get(f'{BASE_URL}/api/events')
print(f"Status: {response.status_code}")
events = response.json()
print(f"Number of events: {len(events)}")
if events:
    print(f"First event: {events[0]['name']}")
print()

# Test 4: Create another event with different type
print("Test 4: Create vape-focused event")
event_data = {
    'name': 'Indoor Vape Restoration Workshop',
    'location': 'Community Center',
    'date_time': (datetime.now() + timedelta(days=2)).isoformat(),
    'duration': 90,
    'type_focus': 'vape',
    'context_hint': 'indoor'
}
response = requests.post(f'{BASE_URL}/api/events', json=event_data)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Message: {result.get('message')}")
print()

# Test 5: Get all events (should be sorted by date)
print("Test 5: Get all events (sorted)")
response = requests.get(f'{BASE_URL}/api/events')
events = response.json()
print(f"Number of events: {len(events)}")
for i, event in enumerate(events, 1):
    print(f"{i}. {event['name']} - {event['type_focus']} - {event['date_time']}")
print()

# Test 6: Test validation - missing required field
print("Test 6: Test validation (missing type_focus)")
event_data = {
    'name': 'Invalid Event',
    'location': 'Somewhere',
    'date_time': datetime.now().isoformat(),
    'duration': 60
}
response = requests.post(f'{BASE_URL}/api/events', json=event_data)
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error')}")
print()

print("All tests completed!")
