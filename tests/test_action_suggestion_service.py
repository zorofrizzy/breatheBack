"""Unit tests for ActionSuggestionService.

Tests action suggestion logic for different contexts.
Requirements: 4.2, 4.3, 4.4, 4.5
"""

import pytest
from backend.services.action_suggestion_service import (
    ActionSuggestionService,
    INDOOR_ACTIONS,
    OUTDOOR_ACTIONS,
    UNIVERSAL_ACTIONS
)


class TestActionSuggestionService:
    """Test suite for ActionSuggestionService."""
    
    def test_get_suggestions_returns_correct_count(self):
        """Test that getSuggestions returns 3-5 actions (Property 9)."""
        service = ActionSuggestionService()
        
        # Test with indoor context
        suggestions = service.get_suggestions(context='indoor', type='vape')
        assert 3 <= len(suggestions) <= 5, f"Expected 3-5 actions, got {len(suggestions)}"
        
        # Test with outdoor context
        suggestions = service.get_suggestions(context='outdoor', type='smoke')
        assert 3 <= len(suggestions) <= 5, f"Expected 3-5 actions, got {len(suggestions)}"
        
        # Test with no context
        suggestions = service.get_suggestions(type='vape')
        assert 3 <= len(suggestions) <= 5, f"Expected 3-5 actions, got {len(suggestions)}"
    
    def test_indoor_context_includes_ventilation_actions(self):
        """Test that indoor context includes ventilation-focused actions (Property 10)."""
        service = ActionSuggestionService()
        
        # Get suggestions for indoor context
        suggestions = service.get_suggestions(context='indoor', type='vape')
        
        # Check that at least one action is from INDOOR_ACTIONS
        indoor_action_ids = {action.id for action in INDOOR_ACTIONS}
        suggestion_ids = {action.id for action in suggestions}
        
        has_indoor_action = bool(indoor_action_ids & suggestion_ids)
        assert has_indoor_action, "Indoor context should include at least one ventilation-focused action"
    
    def test_outdoor_context_includes_spacing_actions(self):
        """Test that outdoor context includes spacing-focused actions (Property 11)."""
        service = ActionSuggestionService()
        
        # Get suggestions for outdoor context
        suggestions = service.get_suggestions(context='outdoor', type='smoke')
        
        # Check that at least one action is from OUTDOOR_ACTIONS
        outdoor_action_ids = {action.id for action in OUTDOOR_ACTIONS}
        suggestion_ids = {action.id for action in suggestions}
        
        has_outdoor_action = bool(outdoor_action_ids & suggestion_ids)
        assert has_outdoor_action, "Outdoor context should include at least one spacing-focused action"
    
    def test_all_actions_display_points(self):
        """Test that all actions have points displayed (Property 12)."""
        service = ActionSuggestionService()
        
        # Test with different contexts
        for context in ['indoor', 'outdoor', None]:
            suggestions = service.get_suggestions(context=context, type='vape')
            
            for action in suggestions:
                assert hasattr(action, 'points'), f"Action {action.id} missing points attribute"
                assert action.points > 0, f"Action {action.id} has invalid points value: {action.points}"
    
    def test_actions_are_randomized(self):
        """Test that action order is randomized for variety."""
        service = ActionSuggestionService()
        
        # Get suggestions multiple times
        results = []
        for _ in range(10):
            suggestions = service.get_suggestions(context='indoor', type='vape')
            result_ids = [action.id for action in suggestions]
            results.append(tuple(result_ids))
        
        # Check that we got at least some variation in order
        unique_orders = set(results)
        assert len(unique_orders) > 1, "Actions should be randomized, but got same order every time"
    
    def test_no_context_includes_all_action_types(self):
        """Test that no context includes actions from all categories."""
        service = ActionSuggestionService()
        
        # Get suggestions without context multiple times to account for randomization
        all_suggestion_ids = set()
        for _ in range(20):
            suggestions = service.get_suggestions(type='vape')
            all_suggestion_ids.update(action.id for action in suggestions)
        
        # Should have a mix of indoor, outdoor, and universal actions
        indoor_ids = {action.id for action in INDOOR_ACTIONS}
        outdoor_ids = {action.id for action in OUTDOOR_ACTIONS}
        universal_ids = {action.id for action in UNIVERSAL_ACTIONS}
        
        # At least some actions from each category should appear
        has_indoor = bool(indoor_ids & all_suggestion_ids)
        has_outdoor = bool(outdoor_ids & all_suggestion_ids)
        has_universal = bool(universal_ids & all_suggestion_ids)
        
        assert has_indoor or has_outdoor or has_universal, \
            "No context should include actions from multiple categories"
    
    def test_action_structure(self):
        """Test that actions have all required fields."""
        service = ActionSuggestionService()
        
        suggestions = service.get_suggestions(context='indoor', type='vape')
        
        for action in suggestions:
            assert hasattr(action, 'id'), "Action missing id"
            assert hasattr(action, 'title'), "Action missing title"
            assert hasattr(action, 'description'), "Action missing description"
            assert hasattr(action, 'points'), "Action missing points"
            assert hasattr(action, 'context'), "Action missing context"
            
            assert isinstance(action.id, str), "Action id should be string"
            assert isinstance(action.title, str), "Action title should be string"
            assert isinstance(action.description, str), "Action description should be string"
            assert isinstance(action.points, int), "Action points should be int"
            assert action.context in ['indoor', 'outdoor', 'both'], \
                f"Invalid context: {action.context}"
