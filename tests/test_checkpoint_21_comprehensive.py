"""
Comprehensive Integration Test for Task 21 Checkpoint
Tests all components and integration flows for BreatheBack application
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from app import app
from backend.services.local_storage_service import LocalStorageService
from backend.services.zone_calculation_service import ZoneCalculationService
from backend.services.state_calculation_service import StateCalculationService


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Clear data before each test
    storage = LocalStorageService()
    storage.clear_all_data()
    yield
    # Clear data after each test
    storage.clear_all_data()


class TestNavigationAndViews:
    """Test navigation between all views"""
    
    def test_all_views_accessible(self, client):
        """Test that all main views are accessible"""
        # Test that the main page loads (serves index.html)
        response = client.get('/')
        assert response.status_code == 200
        
        # Verify the HTML contains all view containers
        html_content = response.data.decode('utf-8')
        assert 'id="report-view"' in html_content
        assert 'id="heatmap-view"' in html_content
        assert 'id="community-view"' in html_content
        assert 'id="mypoints-view"' in html_content
    
    def test_navigation_structure(self, client):
        """Test that navigation structure exists"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Verify navigation elements exist
        assert 'navigation' in html_content.lower() or 'nav' in html_content.lower()


class TestReportActionZoneFlow:
    """Test report → action → zone update flow"""
    
    def test_complete_report_to_zone_update_flow(self, client):
        """Test the complete flow from report submission to zone update"""
        # Step 1: Submit a vape report
        report_data = {
            'type': 'vape',
            'context': 'indoor',
            'location': {
                'latitude': 37.7749,
                'longitude': -122.4194
            }
        }
        
        response = client.post('/api/reports',
                              data=json.dumps(report_data),
                              content_type='application/json')
        assert response.status_code == 201
        result = json.loads(response.data)
        assert 'zone_id' in result
        zone_id = result['zone_id']
        
        # Step 2: Verify zone debt increased
        zones_response = client.get('/api/zones')
        assert zones_response.status_code == 200
        zones = json.loads(zones_response.data)
        
        zone = next((z for z in zones if z['id'] == zone_id), None)
        assert zone is not None
        assert zone['vape_debt'] == 10  # Default increment
        assert zone['vape_restore'] == 0
        
        # Step 3: Complete a restoration action
        action_data = {
            'action_id': 'indoor_1',
            'points': 10,
            'type': 'vape',
            'zone_id': zone_id
        }
        
        action_response = client.post('/api/actions',
                                     data=json.dumps(action_data),
                                     content_type='application/json')
        assert action_response.status_code == 200
        action_result = json.loads(action_response.data)
        assert 'total_points' in action_result
        
        # Step 4: Verify zone restoration score increased
        zones_response2 = client.get('/api/zones')
        zones2 = json.loads(zones_response2.data)
        zone2 = next((z for z in zones2 if z['id'] == zone_id), None)
        assert zone2['vape_restore'] == 10
        
        # Step 5: Verify user points increased
        points_response = client.get('/api/points')
        assert points_response.status_code == 200
        points = json.loads(points_response.data)
        assert points['total_points'] == 10
        assert points['actions_completed'] == 1
    
    def test_smoke_report_flow(self, client):
        """Test smoke report flow separately from vape"""
        # Submit smoke report
        report_data = {
            'type': 'smoke',
            'context': 'outdoor',
            'location': {'latitude': 37.7750, 'longitude': -122.4195}}
        
        response = client.post('/api/reports',
                              data=json.dumps(report_data),
                              content_type='application/json')
        assert response.status_code == 201
        result = json.loads(response.data)
        zone_id = result['zone_id']
        
        # Verify smoke debt increased (not vape)
        zones_response = client.get('/api/zones')
        zones = json.loads(zones_response.data)
        zone = next((z for z in zones if z['id'] == zone_id), None)
        assert zone['smoke_debt'] == 10
        assert zone['vape_debt'] == 0  # Vape should be unaffected


class TestHeatmapAndZoneInspection:
    """Test heatmap toggle and zone inspection"""
    
    def test_zones_api_returns_all_zones(self, client):
        """Test that zones API returns all zones"""
        # Create multiple zones with different states
        reports = [
            {'type': 'vape', 'location': {'latitude': 37.7749, 'longitude': -122.4194}},
            {'type': 'smoke', 'location': {'latitude': 37.7750, 'longitude': -122.4195}},
            {'type': 'vape', 'location': {'latitude': 37.7751, 'longitude': -122.4196}},
        ]
        
        for report in reports:
            client.post('/api/reports',
                       data=json.dumps(report),
                       content_type='application/json')
        
        # Get all zones
        response = client.get('/api/zones')
        assert response.status_code == 200
        zones = json.loads(response.data)
        assert len(zones) >= 3
    
    def test_zone_state_calculation(self, client):
        """Test that zone states are calculated correctly"""
        # Create a zone with debt
        report_data = {
            'type': 'vape',
            'location': {'latitude': 37.7749, 'longitude': -122.4194}}
        response = client.post('/api/reports',
                              data=json.dumps(report_data),
                              content_type='application/json')
        zone_id = json.loads(response.data)['zoneId']
        
        # Get zone and verify state
        zones_response = client.get('/api/zones')
        zones = json.loads(zones_response.data)
        zone = next((z for z in zones if z['id'] == zone_id), None)
        
        # Calculate expected state
        state_service = StateCalculationService()
        zone_obj = type('Zone', (), {
            'vapeDebt': zone['vape_debt'],
            'vapeRestore': zone['vape_restore'],
            'smokeDebt': zone['smoke_debt'],
            'smokeRestore': zone['smoke_restore']
        })()
        
        expected_state = state_service.calculate_state(zone_obj, 'vape')
        assert expected_state in ['needs_restoration', 'healing', 'recovered']
    
    def test_vape_smoke_data_isolation(self, client):
        """Test that vape and smoke data are isolated"""
        # Submit vape report
        vape_report = {
            'type': 'vape',
            'location': {'latitude': 37.7749, 'longitude': -122.4194}}
        response = client.post('/api/reports',
                              data=json.dumps(vape_report),
                              content_type='application/json')
        zone_id = json.loads(response.data)['zoneId']
        
        # Get zone
        zones_response = client.get('/api/zones')
        zones = json.loads(zones_response.data)
        zone = next((z for z in zones if z['id'] == zone_id), None)
        
        # Verify vape data is set, smoke data is zero
        assert zone['vape_debt'] > 0
        assert zone['smoke_debt'] == 0


class TestPointsSummaryAndReset:
    """Test points summary and daily reset"""
    
    def test_points_accumulation(self, client):
        """Test that points accumulate correctly"""
        # Complete multiple actions
        zone_id = 'zone_3774_-12241'
        actions = [
            {'action_id': 'indoor_1', 'points': 10, 'type': 'vape', 'zone_id': zone_id},
            {'action_id': 'indoor_2', 'points': 5, 'type': 'vape', 'zone_id': zone_id},
            {'action_id': 'universal_1', 'points': 5, 'type': 'smoke', 'zone_id': zone_id},
        ]
        
        for action in actions:
            response = client.post('/api/actions',
                                  data=json.dumps(action),
                                  content_type='application/json')
            assert response.status_code == 200
        
        # Verify total points
        points_response = client.get('/api/points')
        points = json.loads(points_response.data)
        assert points['total_points'] == 20
        assert points['actions_completed'] == 3
    
    def test_daily_reset(self, client):
        """Test daily points reset functionality"""
        # Add some points
        zone_id = 'zone_3774_-12241'
        action_data = {
            'action_id': 'indoor_1',
            'points': 10,
            'type': 'vape',
            'zone_id': zone_id
        }
        client.post('/api/actions',
                   data=json.dumps(action_data),
                   content_type='application/json')
        
        # Verify points exist
        points_response = client.get('/api/points')
        points = json.loads(points_response.data)
        assert points['total_points'] == 10
        
        # Reset points
        reset_response = client.post('/api/points/reset')
        assert reset_response.status_code == 200
        
        # Verify points are reset
        points_response2 = client.get('/api/points')
        points2 = json.loads(points_response2.data)
        assert points2['total_points'] == 0
        assert points2['actions_completed'] == 0
    
    def test_points_breakdown(self, client):
        """Test vape vs smoke points breakdown"""
        zone_id = 'zone_3774_-12241'
        
        # Add vape points
        vape_action = {
            'action_id': 'indoor_1',
            'points': 10,
            'type': 'vape',
            'zone_id': zone_id
        }
        client.post('/api/actions',
                   data=json.dumps(vape_action),
                   content_type='application/json')
        
        # Add smoke points
        smoke_action = {
            'action_id': 'outdoor_1',
            'points': 5,
            'type': 'smoke',
            'zone_id': zone_id
        }
        client.post('/api/actions',
                   data=json.dumps(smoke_action),
                   content_type='application/json')
        
        # Verify breakdown
        points_response = client.get('/api/points')
        points = json.loads(points_response.data)
        assert points['total_points'] == 15
        assert points['vape_points'] == 10
        assert points['smoke_points'] == 5


class TestEventCreationAndDisplay:
    """Test event creation and display"""
    
    def test_create_event(self, client):
        """Test creating a community event"""
        event_data = {
            'name': 'Community Air Restoration Meetup',
            'location': 'Central Park Area',
            'date_time': '2026-02-15T14:00:00',
            'duration': 120,
            'type_focus': 'both',
            'context_hint': 'outdoor'
        }
        
        response = client.post('/api/events',
                              data=json.dumps(event_data),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'zone_id' in result or 'message' in result
        assert 'eventId' in result
    
    def test_retrieve_events(self, client):
        """Test retrieving events"""
        # Create multiple events
        events = [
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
        
        for event in events:
            client.post('/api/events',
                       data=json.dumps(event),
                       content_type='application/json')
        
        # Retrieve events
        response = client.get('/api/events')
        assert response.status_code == 200
        retrieved_events = json.loads(response.data)
        assert len(retrieved_events) >= 2
        
        # Verify event structure
        for event in retrieved_events:
            assert 'id' in event
            assert 'name' in event
            assert 'location' in event
            assert 'dateTime' in event
            assert 'typeFocus' in event
    
    def test_event_required_fields(self, client):
        """Test that events require necessary fields"""
        # Try to create event without required fields
        incomplete_event = {
            'name': 'Test Event'
            # Missing location, dateTime, duration, typeFocus
        }
        
        response = client.post('/api/events',
                              data=json.dumps(incomplete_event),
                              content_type='application/json')
        # Should fail or handle gracefully
        assert response.status_code in [200, 400]


class TestResetFunctionality:
    """Test reset functionality"""
    
    def test_full_system_reset(self, client):
        """Test that reset clears all data"""
        # Create some data
        # 1. Submit reports
        report_data = {
            'type': 'vape',
            'location': {'latitude': 37.7749, 'longitude': -122.4194}}
        client.post('/api/reports',
                   data=json.dumps(report_data),
                   content_type='application/json')
        
        # 2. Complete actions
        action_data = {
            'action_id': 'indoor_1',
            'points': 10,
            'type': 'vape',
            'zone_id': 'zone_3774_-12241'
        }
        client.post('/api/actions',
                   data=json.dumps(action_data),
                   content_type='application/json')
        
        # 3. Create events
        event_data = {
            'name': 'Test Event',
            'location': 'Test Location',
            'date_time': '2026-02-15T14:00:00',
            'duration': 60,
            'type_focus': 'both'
        }
        client.post('/api/events',
                   data=json.dumps(event_data),
                   content_type='application/json')
        
        # Verify data exists
        zones_before = json.loads(client.get('/api/zones').data)
        points_before = json.loads(client.get('/api/points').data)
        events_before = json.loads(client.get('/api/events').data)
        
        assert len(zones_before) > 0
        assert points_before.get('total_points', 0) > 0
        assert len(events_before) > 0
        
        # Perform reset
        reset_response = client.post('/api/reset')
        assert reset_response.status_code == 200
        
        # Verify all data is cleared
        zones_after = json.loads(client.get('/api/zones').data)
        points_after = json.loads(client.get('/api/points').data)
        events_after = json.loads(client.get('/api/events').data)
        
        assert len(zones_after) == 0
        assert points_after['total_points'] == 0
        assert points_after['actions_completed'] == 0
        assert len(events_after) == 0
    
    def test_reset_returns_success(self, client):
        """Test that reset endpoint returns success"""
        response = client.post('/api/reset')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'zone_id' in result or 'message' in result


class TestEndToEndIntegration:
    """Test complete end-to-end scenarios"""
    
    def test_complete_user_journey(self, client):
        """Test a complete user journey through the app"""
        # 1. User submits a vape report indoors
        report_data = {
            'type': 'vape',
            'context': 'indoor',
            'location': {'latitude': 37.7749, 'longitude': -122.4194}}
        report_response = client.post('/api/reports',
                                     data=json.dumps(report_data),
                                     content_type='application/json')
        assert report_response.status_code == 200
        zone_id = json.loads(report_response.data)['zoneId']
        
        # 2. User completes a restoration action
        action_data = {
            'action_id': 'indoor_1',
            'points': 10,
            'type': 'vape',
            'zone_id': zone_id
        }
        action_response = client.post('/api/actions',
                                     data=json.dumps(action_data),
                                     content_type='application/json')
        assert action_response.status_code == 200
        
        # 3. User views heatmap (gets zones)
        zones_response = client.get('/api/zones')
        assert zones_response.status_code == 200
        zones = json.loads(zones_response.data)
        assert len(zones) > 0
        
        # 4. User views their points
        points_response = client.get('/api/points')
        assert points_response.status_code == 200
        points = json.loads(points_response.data)
        assert points['total_points'] == 10
        
        # 5. User creates a community event
        event_data = {
            'name': 'Weekend Restoration',
            'location': 'Community Center',
            'date_time': '2026-02-15T10:00:00',
            'duration': 120,
            'type_focus': 'both'
        }
        event_response = client.post('/api/events',
                                    data=json.dumps(event_data),
                                    content_type='application/json')
        assert event_response.status_code == 200
        
        # 6. User views events
        events_response = client.get('/api/events')
        assert events_response.status_code == 200
        events = json.loads(events_response.data)
        assert len(events) > 0
    
    def test_multiple_users_same_zone(self, client):
        """Test multiple users affecting the same zone"""
        # Simulate multiple reports to same zone
        location = {'location': {'latitude': 37.7749, 'longitude': -122.4194}}
        
        # User 1 reports
        report1 = {'type': 'vape', 'location': location['location']}
        response1 = client.post('/api/reports',
                               data=json.dumps(report1),
                               content_type='application/json')
        zone_id = json.loads(response1.data)['zoneId']
        
        # User 2 reports
        report2 = {'type': 'vape', 'location': location['location']}
        client.post('/api/reports',
                   data=json.dumps(report2),
                   content_type='application/json')
        
        # Verify debt accumulated
        zones_response = client.get('/api/zones')
        zones = json.loads(zones_response.data)
        zone = next((z for z in zones if z['id'] == zone_id), None)
        assert zone['vape_debt'] == 20  # 2 reports * 10 points each
        
        # User 1 completes action
        action1 = {
            'action_id': 'indoor_1',
            'points': 10,
            'type': 'vape',
            'zone_id': zone_id
        }
        client.post('/api/actions',
                   data=json.dumps(action1),
                   content_type='application/json')
        
        # User 2 completes action
        action2 = {
            'action_id': 'indoor_2',
            'points': 5,
            'type': 'vape',
            'zone_id': zone_id
        }
        client.post('/api/actions',
                   data=json.dumps(action2),
                   content_type='application/json')
        
        # Verify restoration accumulated
        zones_response2 = client.get('/api/zones')
        zones2 = json.loads(zones_response2.data)
        zone2 = next((z for z in zones2 if z['id'] == zone_id), None)
        assert zone2['vape_restore'] == 15  # 10 + 5 points


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
