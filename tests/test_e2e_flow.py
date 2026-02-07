"""
End-to-End Integration Test for BreatheBack Report and Restoration Flow

This test validates the complete user journey:
1. Submit an air impact report
2. Receive restoration action suggestions
3. Complete a restoration action
4. Verify zone state updates
5. Verify user points updates

Tests Requirements: 3.5, 3.6, 4.1, 5.1, 5.2, 5.3, 5.5, 13.1, 13.2
"""

import urllib.request
import urllib.error
import json
from datetime import datetime


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


def test_end_to_end_flow():
    """
    Test the complete end-to-end flow:
    Submit report → See action card → Complete action → Verify updates
    """
    print("\n" + "=" * 70)
    print("END-TO-END INTEGRATION TEST: Report and Restoration Flow")
    print("=" * 70)
    
    # Step 0: Reset to clean state
    print("\n[STEP 0] Resetting to clean state...")
    status, _ = make_request('POST', '/api/reset')
    assert status == 200, f"Reset failed with status {status}"
    print("✓ Clean state established")
    
    # Step 1: Submit an air impact report
    print("\n[STEP 1] Submitting air impact report...")
    report_data = {
        "type": "vape",
        "context": "indoor",
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
    }
    
    status, report_response = make_request('POST', '/api/reports', report_data)
    assert status == 201, f"Report submission failed with status {status}"
    
    zone_id = report_response.get('zone_id')
    suggestions = report_response.get('suggestions', [])
    
    print(f"✓ Report submitted successfully")
    print(f"  - Zone ID: {zone_id}")
    print(f"  - Suggestions received: {len(suggestions)}")
    
    # Validate report response
    assert zone_id is not None, "Zone ID should be returned"
    assert len(suggestions) >= 3, f"Should have at least 3 suggestions, got {len(suggestions)}"
    assert len(suggestions) <= 5, f"Should have at most 5 suggestions, got {len(suggestions)}"
    
    # Validate suggestion structure
    first_suggestion = suggestions[0]
    assert 'id' in first_suggestion, "Suggestion should have 'id'"
    assert 'title' in first_suggestion, "Suggestion should have 'title'"
    assert 'description' in first_suggestion, "Suggestion should have 'description'"
    assert 'points' in first_suggestion, "Suggestion should have 'points'"
    assert 'context' in first_suggestion, "Suggestion should have 'context'"
    
    print(f"  - First suggestion: {first_suggestion['title']} (+{first_suggestion['points']} points)")
    
    # Step 2: Verify zone was created with correct debt
    print("\n[STEP 2] Verifying zone creation and debt increase...")
    status, zones = make_request('GET', '/api/zones')
    assert status == 200, f"Get zones failed with status {status}"
    assert len(zones) == 1, f"Should have exactly 1 zone, got {len(zones)}"
    
    zone = zones[0]
    assert zone['id'] == zone_id, f"Zone ID mismatch: {zone['id']} != {zone_id}"
    assert zone['vape_debt'] > 0, "Vape debt should be greater than 0"
    assert zone['vape_restore'] == 0, "Vape restore should be 0 initially"
    assert zone['smoke_debt'] == 0, "Smoke debt should be 0 (we reported vape)"
    assert zone['smoke_restore'] == 0, "Smoke restore should be 0"
    
    initial_vape_debt = zone['vape_debt']
    print(f"✓ Zone created with correct debt")
    print(f"  - Vape debt: {zone['vape_debt']}")
    print(f"  - Vape state: {zone['vape_state']}")
    
    # Step 3: Verify initial user points (should be 0)
    print("\n[STEP 3] Verifying initial user points...")
    status, points_before = make_request('GET', '/api/points')
    assert status == 200, f"Get points failed with status {status}"
    assert points_before['total_points'] == 0, "Initial points should be 0"
    assert points_before['actions_completed'] == 0, "Initial actions completed should be 0"
    print(f"✓ Initial points verified: {points_before['total_points']}")
    
    # Step 4: Complete a restoration action
    print("\n[STEP 4] Completing restoration action...")
    action_to_complete = suggestions[0]
    action_data = {
        "action_id": action_to_complete['id'],
        "points": action_to_complete['points'],
        "type": "vape",
        "zone_id": zone_id
    }
    
    status, action_response = make_request('POST', '/api/actions', action_data)
    assert status == 200, f"Action completion failed with status {status}"
    
    assert 'total_points' in action_response, "Response should include total_points"
    assert 'feedback' in action_response, "Response should include feedback"
    assert action_response['total_points'] == action_to_complete['points'], \
        f"Points mismatch: {action_response['total_points']} != {action_to_complete['points']}"
    
    print(f"✓ Action completed successfully")
    print(f"  - Action: {action_to_complete['title']}")
    print(f"  - Points earned: {action_to_complete['points']}")
    print(f"  - Feedback: {action_response['feedback']}")
    
    # Step 5: Verify zone restoration score increased
    print("\n[STEP 5] Verifying zone restoration score update...")
    status, zones_after = make_request('GET', '/api/zones')
    assert status == 200, f"Get zones failed with status {status}"
    
    zone_after = zones_after[0]
    assert zone_after['vape_restore'] == action_to_complete['points'], \
        f"Vape restore should be {action_to_complete['points']}, got {zone_after['vape_restore']}"
    assert zone_after['vape_debt'] == initial_vape_debt, \
        f"Vape debt should remain {initial_vape_debt}, got {zone_after['vape_debt']}"
    
    print(f"✓ Zone restoration score updated")
    print(f"  - Vape restore: {zone_after['vape_restore']}")
    print(f"  - Vape debt: {zone_after['vape_debt']}")
    print(f"  - Net score: {zone_after['vape_restore'] - zone_after['vape_debt']}")
    print(f"  - Vape state: {zone_after['vape_state']}")
    
    # Step 6: Verify user points increased
    print("\n[STEP 6] Verifying user points update...")
    status, points_after = make_request('GET', '/api/points')
    assert status == 200, f"Get points failed with status {status}"
    
    assert points_after['total_points'] == action_to_complete['points'], \
        f"Total points should be {action_to_complete['points']}, got {points_after['total_points']}"
    assert points_after['actions_completed'] == 1, \
        f"Actions completed should be 1, got {points_after['actions_completed']}"
    
    print(f"✓ User points updated")
    print(f"  - Total points: {points_after['total_points']}")
    print(f"  - Actions completed: {points_after['actions_completed']}")
    print(f"  - Vape points: {points_after.get('vape_points', 0)}")
    
    # Step 7: Test multiple actions to verify accumulation
    print("\n[STEP 7] Testing multiple action completions...")
    second_action = suggestions[1] if len(suggestions) > 1 else suggestions[0]
    action_data_2 = {
        "action_id": second_action['id'],
        "points": second_action['points'],
        "type": "vape",
        "zone_id": zone_id
    }
    
    status, action_response_2 = make_request('POST', '/api/actions', action_data_2)
    assert status == 200, f"Second action completion failed with status {status}"
    
    expected_total = action_to_complete['points'] + second_action['points']
    assert action_response_2['total_points'] == expected_total, \
        f"Total points should be {expected_total}, got {action_response_2['total_points']}"
    
    print(f"✓ Second action completed")
    print(f"  - Action: {second_action['title']}")
    print(f"  - Points earned: {second_action['points']}")
    print(f"  - Total points: {action_response_2['total_points']}")
    
    # Step 8: Verify final zone state
    print("\n[STEP 8] Verifying final zone state...")
    status, zones_final = make_request('GET', '/api/zones')
    zone_final = zones_final[0]
    
    expected_restore = action_to_complete['points'] + second_action['points']
    assert zone_final['vape_restore'] == expected_restore, \
        f"Vape restore should be {expected_restore}, got {zone_final['vape_restore']}"
    
    print(f"✓ Final zone state verified")
    print(f"  - Vape restore: {zone_final['vape_restore']}")
    print(f"  - Vape debt: {zone_final['vape_debt']}")
    print(f"  - Net score: {zone_final['vape_restore'] - zone_final['vape_debt']}")
    print(f"  - Vape state: {zone_final['vape_state']}")
    
    # Step 9: Test smoke report to verify data isolation
    print("\n[STEP 9] Testing data type isolation (smoke vs vape)...")
    smoke_report = {
        "type": "smoke",
        "context": "outdoor",
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
    }
    
    status, smoke_response = make_request('POST', '/api/reports', smoke_report)
    assert status == 201, f"Smoke report failed with status {status}"
    
    status, zones_smoke = make_request('GET', '/api/zones')
    zone_smoke = zones_smoke[0]
    
    # Verify vape data unchanged
    assert zone_smoke['vape_restore'] == expected_restore, "Vape restore should be unchanged"
    assert zone_smoke['vape_debt'] == initial_vape_debt, "Vape debt should be unchanged"
    
    # Verify smoke data updated
    assert zone_smoke['smoke_debt'] > 0, "Smoke debt should be greater than 0"
    assert zone_smoke['smoke_restore'] == 0, "Smoke restore should still be 0"
    
    print(f"✓ Data type isolation verified")
    print(f"  - Vape data unchanged: debt={zone_smoke['vape_debt']}, restore={zone_smoke['vape_restore']}")
    print(f"  - Smoke data updated: debt={zone_smoke['smoke_debt']}, restore={zone_smoke['smoke_restore']}")
    print(f"  - Vape state: {zone_smoke['vape_state']}")
    print(f"  - Smoke state: {zone_smoke['smoke_state']}")
    
    print("\n" + "=" * 70)
    print("✓ ALL END-TO-END TESTS PASSED!")
    print("=" * 70)
    print("\nSummary:")
    print(f"  - Reports submitted: 2 (1 vape, 1 smoke)")
    print(f"  - Actions completed: 2 (both vape)")
    print(f"  - Total points earned: {expected_total}")
    print(f"  - Zone state transitions verified: ✓")
    print(f"  - Data type isolation verified: ✓")
    print(f"  - Points accumulation verified: ✓")
    
    return True


def run_tests():
    """Run all end-to-end tests."""
    try:
        test_end_to_end_flow()
        return True
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except urllib.error.URLError:
        print("\n✗ ERROR: Could not connect to Flask server.")
        print("Make sure the server is running: python app.py")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
