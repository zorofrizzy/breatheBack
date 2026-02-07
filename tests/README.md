# BreatheBack Test Suite

This directory contains all tests for the BreatheBack application.

## Test Structure

### Backend Tests (Python)

**Service Tests:**
- `test_zone_calculation_service.py` - Zone grid calculation and management
- `test_state_calculation_service.py` - Restoration state calculations
- `test_action_suggestion_service.py` - Context-aware action suggestions
- `test_local_storage_service.py` - Data persistence and storage

**API Tests:**
- `test_api.py` - Comprehensive API endpoint tests
- `test_api_simple.py` - Basic API functionality tests
- `test_event_api.py` - Community event API tests

**Integration Tests:**
- `test_e2e_flow.py` - End-to-end user flow tests
- `test_main_integration.py` - Main application integration tests
- `test_task_18_e2e.py` - Task 18 end-to-end tests

**Checkpoint Tests:**
- `test_checkpoint_21_simple.py` - Simple checkpoint validation
- `test_checkpoint_21_comprehensive.py` - Comprehensive checkpoint tests

**Verification Scripts:**
- `verify_serialization.py` - Data serialization verification
- `verify_zone_service.py` - Zone service verification

### Frontend Tests (HTML)

**Component Tests:**
- `test_navigation.html` - Navigation bar component
- `test_report_form.html` - Report submission form
- `test_restoration_action_card.html` - Action card component
- `test_heatmap_view.html` - Heatmap visualization
- `test_zone_inspector.html` - Zone inspector modal
- `test_points_summary.html` - Points summary display
- `test_event_unit.html` - Event components unit tests
- `test_event_components.html` - Event component tests

**Integration Tests:**
- `test_state_management.html` - State management integration
- `test_e2e_flow.html` - End-to-end user flow
- `test_main_integration.html` - Main application integration
- `test_checkpoint_21_integration.html` - Checkpoint 21 integration
- `test_event_integration.html` - Event integration tests
- `test_points_summary_integration.html` - Points summary integration
- `test_zone_inspector_integration.html` - Zone inspector integration

**Demo Tests:**
- `test_reset_demo.html` - Reset and demo functionality

## Running Tests

### Backend Tests

Run all Python tests:
```bash
python -m pytest tests/
```

Run specific test file:
```bash
python -m pytest tests/test_api.py
```

Run with verbose output:
```bash
python -m pytest tests/ -v
```

### Frontend Tests

Frontend tests are HTML files that can be opened directly in a browser:

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open test files in browser:
   ```
   http://localhost:5000/tests/frontend/test_navigation.html
   ```

Or open the HTML files directly from the file system.

## Test Coverage

The test suite covers:
- ✓ All backend services
- ✓ All API endpoints
- ✓ All frontend components
- ✓ End-to-end user flows
- ✓ Integration between components
- ✓ Data persistence and state management
- ✓ Privacy and correctness properties

## Notes

- Backend tests use pytest framework
- Frontend tests use vanilla JavaScript (no framework)
- Integration tests validate complete user workflows
- Property-based tests validate correctness properties (optional)
