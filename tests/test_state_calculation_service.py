"""Unit tests for StateCalculationService.

Tests state calculation logic, color mapping, and message generation.
"""

import pytest
from backend.services.state_calculation_service import StateCalculationService
from backend.models.zone import Zone, GeoBounds
from backend.constants import RECOVERED_THRESHOLD, HEALING_THRESHOLD


class TestStateCalculationService:
    """Test suite for StateCalculationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = StateCalculationService()
        self.bounds = GeoBounds(north=40.01, south=40.00, east=-74.00, west=-74.01)
    
    def test_calculate_state_needs_restoration(self):
        """Test state calculation for needs_restoration state."""
        # Net score < HEALING_THRESHOLD (-20)
        zone = Zone(
            id='zone_test',
            bounds=self.bounds,
            vape_debt=50.0,
            vape_restore=20.0  # Net: 20 - 50 = -30 < -20
        )
        
        state = self.service.calculate_state(zone, 'vape')
        assert state == 'needs_restoration'
    
    def test_calculate_state_healing(self):
        """Test state calculation for healing state."""
        # Net score between HEALING_THRESHOLD (-20) and RECOVERED_THRESHOLD (20)
        zone = Zone(
            id='zone_test',
            bounds=self.bounds,
            smoke_debt=30.0,
            smoke_restore=40.0  # Net: 40 - 30 = 10 (between -20 and 20)
        )
        
        state = self.service.calculate_state(zone, 'smoke')
        assert state == 'healing'
    
    def test_calculate_state_recovered(self):
        """Test state calculation for recovered state."""
        # Net score > RECOVERED_THRESHOLD (20)
        zone = Zone(
            id='zone_test',
            bounds=self.bounds,
            vape_debt=10.0,
            vape_restore=50.0  # Net: 50 - 10 = 40 > 20
        )
        
        state = self.service.calculate_state(zone, 'vape')
        assert state == 'recovered'
    
    def test_calculate_state_at_healing_threshold(self):
        """Test state calculation at exact healing threshold."""
        # Net score exactly at HEALING_THRESHOLD (-20)
        zone = Zone(
            id='zone_test',
            bounds=self.bounds,
            smoke_debt=50.0,
            smoke_restore=30.0  # Net: 30 - 50 = -20
        )
        
        state = self.service.calculate_state(zone, 'smoke')
        # At threshold, should be needs_restoration (not > HEALING_THRESHOLD)
        assert state == 'needs_restoration'
    
    def test_calculate_state_at_recovered_threshold(self):
        """Test state calculation at exact recovered threshold."""
        # Net score exactly at RECOVERED_THRESHOLD (20)
        zone = Zone(
            id='zone_test',
            bounds=self.bounds,
            vape_debt=10.0,
            vape_restore=30.0  # Net: 30 - 10 = 20
        )
        
        state = self.service.calculate_state(zone, 'vape')
        # At threshold, should be healing (not > RECOVERED_THRESHOLD)
        assert state == 'healing'
    
    def test_calculate_state_vape_vs_smoke_isolation(self):
        """Test that vape and smoke states are calculated independently."""
        zone = Zone(
            id='zone_test',
            bounds=self.bounds,
            vape_debt=10.0,
            vape_restore=50.0,  # Vape net: 40 (recovered)
            smoke_debt=50.0,
            smoke_restore=20.0  # Smoke net: -30 (needs restoration)
        )
        
        vape_state = self.service.calculate_state(zone, 'vape')
        smoke_state = self.service.calculate_state(zone, 'smoke')
        
        assert vape_state == 'recovered'
        assert smoke_state == 'needs_restoration'
    
    def test_calculate_state_invalid_type(self):
        """Test that invalid type raises ValueError."""
        zone = Zone(
            id='zone_test',
            bounds=self.bounds,
            vape_debt=10.0,
            vape_restore=20.0
        )
        
        with pytest.raises(ValueError, match="Invalid type"):
            self.service.calculate_state(zone, 'invalid')
    
    def test_get_state_color_needs_restoration(self):
        """Test color for needs_restoration state."""
        color = self.service.get_state_color('needs_restoration')
        assert color == '#F4D03F'  # Yellow
    
    def test_get_state_color_healing(self):
        """Test color for healing state."""
        color = self.service.get_state_color('healing')
        assert color == '#52BE80'  # Green
    
    def test_get_state_color_recovered(self):
        """Test color for recovered state."""
        color = self.service.get_state_color('recovered')
        assert color == '#5DADE2'  # Blue
    
    def test_get_state_color_invalid_state(self):
        """Test that invalid state raises ValueError."""
        with pytest.raises(ValueError, match="Invalid state"):
            self.service.get_state_color('invalid_state')
    
    def test_get_state_message_needs_restoration(self):
        """Test message for needs_restoration state."""
        message = self.service.get_state_message('needs_restoration')
        assert message == 'This space needs care'
    
    def test_get_state_message_healing(self):
        """Test message for healing state."""
        message = self.service.get_state_message('healing')
        assert message == 'This space is healing'
    
    def test_get_state_message_recovered(self):
        """Test message for recovered state."""
        message = self.service.get_state_message('recovered')
        assert message == 'This space has recovered'
    
    def test_get_state_message_invalid_state(self):
        """Test that invalid state raises ValueError."""
        with pytest.raises(ValueError, match="Invalid state"):
            self.service.get_state_message('invalid_state')
    
    def test_zero_debt_and_restore(self):
        """Test state calculation with zero debt and restore."""
        zone = Zone(
            id='zone_test',
            bounds=self.bounds,
            vape_debt=0.0,
            vape_restore=0.0  # Net: 0 (between -20 and 20)
        )
        
        state = self.service.calculate_state(zone, 'vape')
        assert state == 'healing'

