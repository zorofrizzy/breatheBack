"""Unit tests for LocalStorageService."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, date

from backend.services.local_storage_service import LocalStorageService
from backend.models.zone import Zone, GeoBounds
from backend.models.user_points import UserPoints, CompletedAction
from backend.models.community_event import CommunityEvent


class TestLocalStorageService:
    """Test suite for LocalStorageService."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # Cleanup after test
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def storage_service(self, temp_dir):
        """Create a LocalStorageService instance with temp directory."""
        return LocalStorageService(storage_dir=temp_dir)
    
    @pytest.fixture
    def sample_zone(self):
        """Create a sample zone for testing."""
        bounds = GeoBounds(north=37.46, south=37.45, east=-122.23, west=-122.24)
        return Zone(
            id="zone_3745_-12223",
            bounds=bounds,
            vape_debt=10.0,
            vape_restore=5.0,
            smoke_debt=20.0,
            smoke_restore=15.0,
            last_updated=datetime(2024, 1, 15, 12, 0, 0)
        )
    
    @pytest.fixture
    def sample_user_points(self):
        """Create sample user points for testing."""
        action = CompletedAction(
            action_id="indoor_1",
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            points=10,
            type="vape",
            zone_id="zone_3745_-12223"
        )
        return UserPoints(
            date="2024-01-15",
            total_points=10,
            actions_completed=1,
            vape_points=10,
            smoke_points=0,
            actions=[action]
        )
    
    @pytest.fixture
    def sample_event(self):
        """Create a sample community event for testing."""
        return CommunityEvent(
            id="event_123",
            name="Community Cleanup",
            location="Central Park",
            date_time=datetime(2024, 2, 1, 14, 0, 0),
            duration=120,
            type_focus="both",
            description="We're meeting to help this area heal",
            created_at=datetime(2024, 1, 15, 12, 0, 0),
            context_hint="outdoor"
        )
    
    # Zone storage tests
    
    def test_save_zones_creates_file(self, storage_service, sample_zone):
        """Test that save_zones creates a JSON file."""
        zones = [sample_zone]
        storage_service.save_zones(zones)
        
        assert storage_service.zones_file.exists()
    
    def test_save_zones_writes_valid_json(self, storage_service, sample_zone):
        """Test that save_zones writes valid JSON data."""
        zones = [sample_zone]
        storage_service.save_zones(zones)
        
        with open(storage_service.zones_file, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]['id'] == "zone_3745_-12223"
        assert data[0]['vape_debt'] == 10.0
        assert data[0]['smoke_debt'] == 20.0
    
    def test_save_multiple_zones(self, storage_service, sample_zone):
        """Test saving multiple zones."""
        bounds2 = GeoBounds(north=37.47, south=37.46, east=-122.22, west=-122.23)
        zone2 = Zone(
            id="zone_3746_-12222",
            bounds=bounds2,
            vape_debt=5.0,
            vape_restore=10.0,
            smoke_debt=8.0,
            smoke_restore=12.0
        )
        
        zones = [sample_zone, zone2]
        storage_service.save_zones(zones)
        
        loaded_zones = storage_service.load_zones()
        assert len(loaded_zones) == 2
        assert loaded_zones[0].id == "zone_3745_-12223"
        assert loaded_zones[1].id == "zone_3746_-12222"
    
    def test_load_zones_returns_empty_list_when_file_missing(self, storage_service):
        """Test that load_zones returns empty list when file doesn't exist."""
        zones = storage_service.load_zones()
        assert zones == []
    
    def test_load_zones_returns_saved_zones(self, storage_service, sample_zone):
        """Test that load_zones returns previously saved zones."""
        zones = [sample_zone]
        storage_service.save_zones(zones)
        
        loaded_zones = storage_service.load_zones()
        
        assert len(loaded_zones) == 1
        assert loaded_zones[0].id == sample_zone.id
        assert loaded_zones[0].vape_debt == sample_zone.vape_debt
        assert loaded_zones[0].smoke_restore == sample_zone.smoke_restore
    
    def test_load_zones_handles_corrupted_file(self, storage_service):
        """Test that load_zones handles corrupted JSON gracefully."""
        # Write invalid JSON to file
        with open(storage_service.zones_file, 'w') as f:
            f.write("{ invalid json }")
        
        zones = storage_service.load_zones()
        assert zones == []
    
    # User points storage tests
    
    def test_save_user_points_creates_file(self, storage_service, sample_user_points):
        """Test that save_user_points creates a JSON file."""
        storage_service.save_user_points(sample_user_points)
        
        assert storage_service.points_file.exists()
    
    def test_save_user_points_writes_valid_json(self, storage_service, sample_user_points):
        """Test that save_user_points writes valid JSON data."""
        storage_service.save_user_points(sample_user_points)
        
        with open(storage_service.points_file, 'r') as f:
            data = json.load(f)
        
        assert data['date'] == "2024-01-15"
        assert data['total_points'] == 10
        assert data['actions_completed'] == 1
        assert len(data['actions']) == 1
    
    def test_load_user_points_returns_new_when_file_missing(self, storage_service):
        """Test that load_user_points returns new UserPoints when file doesn't exist."""
        points = storage_service.load_user_points()
        
        assert points.date == date.today().isoformat()
        assert points.total_points == 0
        assert points.actions_completed == 0
    
    def test_load_user_points_returns_saved_points(self, storage_service, sample_user_points):
        """Test that load_user_points returns previously saved points."""
        # Save with today's date
        action1 = CompletedAction(
            action_id="indoor_1",
            timestamp=datetime.now(),
            points=15,
            type="vape",
            zone_id="zone_1"
        )
        action2 = CompletedAction(
            action_id="outdoor_1",
            timestamp=datetime.now(),
            points=10,
            type="smoke",
            zone_id="zone_2"
        )
        today_points = UserPoints(
            date=date.today().isoformat(),
            total_points=25,
            actions_completed=2,
            vape_points=15,
            smoke_points=10,
            actions=[action1, action2]
        )
        storage_service.save_user_points(today_points)
        
        loaded_points = storage_service.load_user_points()
        
        assert loaded_points.date == date.today().isoformat()
        assert loaded_points.total_points == 25
        assert loaded_points.actions_completed == 2
    
    def test_load_user_points_resets_on_date_change(self, storage_service):
        """Test that load_user_points resets when date has changed (daily reset)."""
        # Save points with yesterday's date - create valid actions list
        actions = [
            CompletedAction(
                action_id=f"action_{i}",
                timestamp=datetime(2024, 1, 14, 12, 0, 0),
                points=10,
                type="vape" if i < 3 else "smoke",
                zone_id=f"zone_{i}"
            )
            for i in range(5)
        ]
        old_points = UserPoints(
            date="2024-01-14",
            total_points=50,
            actions_completed=5,
            vape_points=30,
            smoke_points=20,
            actions=actions
        )
        storage_service.save_user_points(old_points)
        
        # Load points - should get new UserPoints for today
        loaded_points = storage_service.load_user_points()
        
        assert loaded_points.date == date.today().isoformat()
        assert loaded_points.total_points == 0
        assert loaded_points.actions_completed == 0
    
    def test_load_user_points_handles_corrupted_file(self, storage_service):
        """Test that load_user_points handles corrupted JSON gracefully."""
        # Write invalid JSON to file
        with open(storage_service.points_file, 'w') as f:
            f.write("{ invalid json }")
        
        points = storage_service.load_user_points()
        assert points.date == date.today().isoformat()
        assert points.total_points == 0
    
    # Events storage tests
    
    def test_save_events_creates_file(self, storage_service, sample_event):
        """Test that save_events creates a JSON file."""
        events = [sample_event]
        storage_service.save_events(events)
        
        assert storage_service.events_file.exists()
    
    def test_save_events_writes_valid_json(self, storage_service, sample_event):
        """Test that save_events writes valid JSON data."""
        events = [sample_event]
        storage_service.save_events(events)
        
        with open(storage_service.events_file, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]['id'] == "event_123"
        assert data[0]['name'] == "Community Cleanup"
        assert data[0]['type_focus'] == "both"
    
    def test_save_multiple_events(self, storage_service, sample_event):
        """Test saving multiple events."""
        event2 = CommunityEvent(
            id="event_456",
            name="Air Quality Workshop",
            location="Community Center",
            date_time=datetime(2024, 2, 15, 18, 0, 0),
            duration=90,
            type_focus="vape",
            description="Learn about air restoration",
            created_at=datetime(2024, 1, 15, 12, 0, 0)
        )
        
        events = [sample_event, event2]
        storage_service.save_events(events)
        
        loaded_events = storage_service.load_events()
        assert len(loaded_events) == 2
        assert loaded_events[0].id == "event_123"
        assert loaded_events[1].id == "event_456"
    
    def test_load_events_returns_empty_list_when_file_missing(self, storage_service):
        """Test that load_events returns empty list when file doesn't exist."""
        events = storage_service.load_events()
        assert events == []
    
    def test_load_events_returns_saved_events(self, storage_service, sample_event):
        """Test that load_events returns previously saved events."""
        events = [sample_event]
        storage_service.save_events(events)
        
        loaded_events = storage_service.load_events()
        
        assert len(loaded_events) == 1
        assert loaded_events[0].id == sample_event.id
        assert loaded_events[0].name == sample_event.name
        assert loaded_events[0].duration == sample_event.duration
    
    def test_load_events_handles_corrupted_file(self, storage_service):
        """Test that load_events handles corrupted JSON gracefully."""
        # Write invalid JSON to file
        with open(storage_service.events_file, 'w') as f:
            f.write("{ invalid json }")
        
        events = storage_service.load_events()
        assert events == []
    
    # Clear all data tests
    
    def test_clear_all_data_removes_all_files(self, storage_service, sample_zone, sample_user_points, sample_event):
        """Test that clear_all_data removes all data files."""
        # Save data to all files
        storage_service.save_zones([sample_zone])
        storage_service.save_user_points(sample_user_points)
        storage_service.save_events([sample_event])
        
        # Verify files exist
        assert storage_service.zones_file.exists()
        assert storage_service.points_file.exists()
        assert storage_service.events_file.exists()
        
        # Clear all data
        storage_service.clear_all_data()
        
        # Verify files are deleted
        assert not storage_service.zones_file.exists()
        assert not storage_service.points_file.exists()
        assert not storage_service.events_file.exists()
    
    def test_clear_all_data_handles_missing_files(self, storage_service):
        """Test that clear_all_data handles missing files gracefully."""
        # Should not raise error even if files don't exist
        storage_service.clear_all_data()
        
        assert not storage_service.zones_file.exists()
        assert not storage_service.points_file.exists()
        assert not storage_service.events_file.exists()
    
    def test_clear_all_data_allows_fresh_start(self, storage_service, sample_zone):
        """Test that after clearing data, new data can be saved."""
        # Save, clear, and save again
        storage_service.save_zones([sample_zone])
        storage_service.clear_all_data()
        
        # Create new zone and save
        bounds = GeoBounds(north=37.48, south=37.47, east=-122.21, west=-122.22)
        new_zone = Zone(id="zone_new", bounds=bounds)
        storage_service.save_zones([new_zone])
        
        # Verify new data is saved
        loaded_zones = storage_service.load_zones()
        assert len(loaded_zones) == 1
        assert loaded_zones[0].id == "zone_new"
    
    # Error handling tests
    
    def test_save_zones_validates_data(self, storage_service):
        """Test that save_zones validates zone data before saving."""
        # Create zone with valid data, then manually set invalid value
        bounds = GeoBounds(north=37.46, south=37.45, east=-122.23, west=-122.24)
        zone = Zone(
            id="zone_test",
            bounds=bounds,
            vape_debt=10.0
        )
        # Manually set invalid value to bypass constructor validation
        zone.vape_debt = -10.0
        
        with pytest.raises(IOError):
            storage_service.save_zones([zone])
    
    def test_save_user_points_validates_data(self, storage_service):
        """Test that save_user_points validates points data before saving."""
        # Create valid user points, then manually set invalid value
        points = UserPoints(
            date="2024-01-15",
            total_points=80,
            actions_completed=0,
            vape_points=50,
            smoke_points=30
        )
        # Manually set invalid total to bypass constructor validation
        points.total_points = 100  # Now 50 + 30 != 100
        
        with pytest.raises(IOError):
            storage_service.save_user_points(points)
    
    def test_save_events_validates_data(self, storage_service):
        """Test that save_events validates event data before saving."""
        # Create valid event, then manually set invalid value
        event = CommunityEvent(
            id="event_test",
            name="Test Event",
            location="Somewhere",
            date_time=datetime(2024, 2, 1, 14, 0, 0),
            duration=30,
            type_focus="both",
            description="Test",
            created_at=datetime.now()
        )
        # Manually set invalid duration to bypass constructor validation
        event.duration = -30
        
        with pytest.raises(IOError):
            storage_service.save_events([event])
