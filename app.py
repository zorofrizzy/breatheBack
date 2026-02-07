"""Flask application for BreatheBack API.

Provides REST API endpoints for air impact reporting, restoration actions,
zone management, user points, and community events.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import uuid
import os

from backend.models.zone import Zone
from backend.models.user_points import UserPoints, CompletedAction
from backend.models.community_event import CommunityEvent
from backend.models.air_impact_report import AirImpactReport, Coordinates
from backend.services.zone_calculation_service import ZoneCalculationService
from backend.services.state_calculation_service import StateCalculationService
from backend.services.action_suggestion_service import ActionSuggestionService
from backend.services.local_storage_service import LocalStorageService
from backend.constants import DEBT_INCREMENT


# Initialize Flask app
app = Flask(__name__, static_folder='frontend', static_url_path='')

# Enable CORS for local development
CORS(app)

# Initialize services
zone_service = ZoneCalculationService()
state_service = StateCalculationService()
action_service = ActionSuggestionService()
storage_service = LocalStorageService()

# Load initial data from storage
zones = storage_service.load_zones()
for zone in zones:
    zone_service._zones[zone.id] = zone

user_points = storage_service.load_user_points()
events = storage_service.load_events()


@app.route('/')
def index():
    """Serve the main application page."""
    return send_from_directory('frontend', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from the frontend directory."""
    return send_from_directory('frontend', path)


@app.route('/api/zones', methods=['GET'])
def get_zones():
    """
    Get all zones.
    
    PRIVACY CONTROLS (Property 32):
    - Returns ONLY aggregated zone-level data
    - No individual report data is included
    - No user identities are exposed
    - No venue-specific details are included
    
    Returns:
        JSON array of zone objects with state information
        
    Requirements: 3.5, 3.6, 11.1, 11.2, 11.5
    """
    try:
        zones = zone_service.get_all_zones()
        
        # Convert zones to dictionaries with state information
        # CRITICAL: Only aggregated data is returned (Property 32)
        zones_data = []
        for zone in zones:
            zone_dict = zone.to_dict()
            
            # Add state information for both vape and smoke
            zone_dict['vape_state'] = state_service.calculate_state(zone, 'vape')
            zone_dict['smoke_state'] = state_service.calculate_state(zone, 'smoke')
            
            # PRIVACY: Ensure no individual report data is included
            # Zone dict contains only: id, bounds, debt/restore scores, states
            # No context, no timestamps of individual reports, no user IDs
            
            zones_data.append(zone_dict)
        
        return jsonify(zones_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports', methods=['POST'])
def submit_report():
    """
    Submit an air impact report.
    
    PRIVACY CONTROL (Property 30, 31):
    - Context is used ONLY for action suggestions
    - Context is NOT stored in zone data
    - Context is NOT returned in zone API responses
    
    Request body:
        {
            "type": "smoke" | "vape",
            "context": "indoor" | "outdoor" (optional),
            "location": {
                "latitude": float,
                "longitude": float
            }
        }
    
    Returns:
        JSON object with zone_id and suggested actions
        
    Requirements: 3.5, 3.6, 4.1, 10.4, 10.5
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'type' not in data or 'location' not in data:
            return jsonify({'error': 'Missing required fields: type and location'}), 400
        
        # Create coordinates
        location_data = data['location']
        coordinates = Coordinates(
            latitude=location_data['latitude'],
            longitude=location_data['longitude']
        )
        
        # Create air impact report (transient - not stored)
        report = AirImpactReport(
            type=data['type'],
            location=coordinates,
            timestamp=datetime.utcnow(),
            context=data.get('context')  # Context captured but NOT stored in zones
        )
        
        # Get or create zone for this location
        zone = zone_service.create_zone(
            coordinates.latitude,
            coordinates.longitude
        )
        
        # Update zone debt based on report type
        # CRITICAL: Context is NOT stored in zone data (Privacy Property 30)
        if report.type == 'vape':
            zone.vape_debt += DEBT_INCREMENT
        elif report.type == 'smoke':
            zone.smoke_debt += DEBT_INCREMENT
        
        zone.last_updated = datetime.utcnow()
        
        # Save zones to storage (context is NOT included)
        storage_service.save_zones(zone_service.get_all_zones())
        
        # Get restoration action suggestions
        # CRITICAL: Context is ONLY used here for action suggestions (Property 30)
        suggestions = action_service.get_suggestions(
            context=report.context,  # Context used only for suggestions
            type=report.type
        )
        
        # Convert suggestions to dictionaries
        suggestions_data = [
            {
                'id': action.id,
                'title': action.title,
                'description': action.description,
                'points': action.points,
                'context': action.context
            }
            for action in suggestions
        ]
        
        # PRIVACY: Context is NOT returned in response (Property 31)
        # Only zone_id and suggestions are returned
        return jsonify({
            'zone_id': zone.id,
            'suggestions': suggestions_data,
            'message': 'Report submitted successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/actions', methods=['POST'])
def complete_action():
    """
    Complete a restoration action.
    
    Request body:
        {
            "action_id": string,
            "points": int,
            "type": "smoke" | "vape" | "both",
            "zone_id": string
        }
    
    Returns:
        JSON object with updated points and positive feedback
        
    Requirements: 5.1, 5.2, 5.3
    """
    try:
        global user_points
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['action_id', 'points', 'type', 'zone_id']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
        
        # Get zone or create it if it doesn't exist
        zone = zone_service.get_zone(data['zone_id'])
        if not zone:
            # Parse zone_id to extract coordinates
            # Format: zone_LATGRID_LNGGRID
            try:
                parts = data['zone_id'].split('_')
                if len(parts) == 3 and parts[0] == 'zone':
                    lat_grid = int(parts[1])
                    lng_grid = int(parts[2])
                    
                    # Calculate center coordinates from grid
                    ZONE_GRID_SIZE = 0.01
                    lat = (lat_grid + 0.5) * ZONE_GRID_SIZE
                    lng = (lng_grid + 0.5) * ZONE_GRID_SIZE
                    
                    # Create the zone
                    zone = zone_service.create_zone(lat, lng)
                    print(f"Created new zone: {zone.id} at ({lat}, {lng})")
                else:
                    return jsonify({'error': 'Invalid zone_id format'}), 400
            except (ValueError, IndexError) as e:
                return jsonify({'error': f'Invalid zone_id format: {str(e)}'}), 400
        
        # Update zone restoration score based on type
        if data['type'] == 'vape':
            zone.vape_restore += data['points']
            print(f"Updated zone {zone.id}: vape_restore = {zone.vape_restore}")
        elif data['type'] == 'smoke':
            zone.smoke_restore += data['points']
            print(f"Updated zone {zone.id}: smoke_restore = {zone.smoke_restore}")
        elif data['type'] == 'both':
            # Apply points to BOTH vape and smoke
            zone.vape_restore += data['points']
            zone.smoke_restore += data['points']
            print(f"Updated zone {zone.id}: vape_restore = {zone.vape_restore}, smoke_restore = {zone.smoke_restore}")
        else:
            return jsonify({'error': 'Invalid type. Must be "vape", "smoke", or "both"'}), 400
        
        zone.last_updated = datetime.utcnow()
        
        # Create completed action record
        completed_action = CompletedAction(
            action_id=data['action_id'],
            timestamp=datetime.utcnow(),
            points=data['points'],
            type=data['type'],
            zone_id=data['zone_id']
        )
        
        # Update user points
        user_points.total_points += data['points']
        user_points.actions_completed += 1
        
        # For "both" type, add points to both categories
        if data['type'] == 'vape':
            user_points.vape_points += data['points']
        elif data['type'] == 'smoke':
            user_points.smoke_points += data['points']
        elif data['type'] == 'both':
            user_points.vape_points += data['points']
            user_points.smoke_points += data['points']
        
        user_points.actions.append(completed_action)
        
        # Save data to storage
        storage_service.save_zones(zone_service.get_all_zones())
        storage_service.save_user_points(user_points)
        
        # Generate positive feedback message
        feedback_messages = [
            "Nice—this area is healing",
            "Great work! The air is getting better",
            "You're making a difference",
            "Small actions add up—nice work",
            "This space is healing thanks to you"
        ]
        
        import random
        feedback = random.choice(feedback_messages)
        
        return jsonify({
            'total_points': user_points.total_points,
            'actions_completed': user_points.actions_completed,
            'feedback': feedback,
            'message': 'Action completed successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/points', methods=['GET'])
def get_points():
    """
    Get user points for today.
    
    PRIVACY CONTROLS (Property 33):
    - Returns only aggregated point totals
    - No user identity information is included
    - No personally identifiable information
    
    Returns:
        JSON object with points breakdown
        
    Requirements: 8.1, 8.2, 11.2
    """
    try:
        # Reload points to check for daily reset
        global user_points
        user_points = storage_service.load_user_points()
        
        # PRIVACY: Only return aggregated point data
        # No user identity, no personal information
        return jsonify(user_points.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/points/reset', methods=['POST'])
def reset_points():
    """
    Reset daily points (for testing/demo purposes).
    
    Returns:
        JSON object with success message
        
    Requirements: 8.3
    """
    try:
        global user_points
        
        from datetime import date
        user_points = UserPoints(date=date.today().isoformat())
        storage_service.save_user_points(user_points)
        
        return jsonify({
            'message': 'Points reset successfully',
            'points': user_points.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events', methods=['GET'])
def get_events():
    """
    Get all community events.
    
    PRIVACY CONTROLS (Property 34):
    - Location is general area description, not specific venue
    - No venue-specific details that could identify private spaces
    - No user identity information
    
    Returns:
        JSON array of event objects sorted by date
        
    Requirements: 9.1, 9.3, 11.5
    """
    try:
        global events
        events = storage_service.load_events()
        
        # Sort events by date_time
        sorted_events = sorted(events, key=lambda e: e.date_time)
        
        # Convert to dictionaries
        # PRIVACY: Location is general area, not specific venue (Property 34)
        events_data = [event.to_dict() for event in sorted_events]
        
        return jsonify(events_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events', methods=['POST'])
def create_event():
    """
    Create a new community event.
    
    Request body:
        {
            "name": string,
            "location": string,
            "date_time": ISO datetime string,
            "duration": int (minutes),
            "type_focus": "vape" | "smoke" | "both",
            "context_hint": "indoor" | "outdoor" (optional),
            "description": string (optional, auto-generated if not provided)
        }
    
    Returns:
        JSON object with created event and confirmation message
        
    Requirements: 9.1, 9.2, 9.3
    """
    try:
        global events
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'location', 'date_time', 'duration', 'type_focus']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
        
        # Auto-generate description if not provided
        description = data.get('description')
        if not description:
            description = "We're meeting to help this area heal. No blame, just better air choices together."
        
        # Create event
        event = CommunityEvent(
            id=str(uuid.uuid4()),
            name=data['name'],
            location=data['location'],
            date_time=datetime.fromisoformat(data['date_time']),
            duration=data['duration'],
            type_focus=data['type_focus'],
            description=description,
            created_at=datetime.utcnow(),
            context_hint=data.get('context_hint')
        )
        
        # Add to events list
        events.append(event)
        
        # Save to storage
        storage_service.save_events(events)
        
        return jsonify({
            'event': event.to_dict(),
            'message': 'Event created successfully! Looking forward to healing together.'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset_all_data():
    """
    Reset all application data.
    
    Clears all zones, user points, and events.
    
    Returns:
        JSON object with success message
        
    Requirements: 12.2, 12.4
    """
    try:
        global user_points, events
        
        # Clear all zones
        zone_service.clear_all_zones()
        
        # Reset user points
        from datetime import date
        user_points = UserPoints(date=date.today().isoformat())
        
        # Clear events
        events = []
        
        # Clear storage
        storage_service.clear_all_data()
        
        return jsonify({
            'message': 'All data has been reset successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/seed-demo', methods=['POST'])
def seed_demo_data():
    """
    Seed demo data with zones in all three restoration states.
    
    Creates zones around the user's location (or default location) with:
    - Recovered zones (blue) - high restoration, low debt
    - Healing zones (green) - moderate restoration and debt
    - Needs Restoration zones (yellow) - high debt, low restoration
    
    Returns:
        JSON object with success message and zone count
        
    Requirements: 12.1
    """
    try:
        # Get center location from request or use default (San Francisco)
        data = request.get_json() or {}
        center_lat = data.get('latitude', 37.7749)
        center_lng = data.get('longitude', -122.4194)
        
        # Define demo zones around the center location
        # Grid offset: 0.01 degrees ≈ 1km
        demo_zones = [
            # Recovered zones (blue) - net score > 20
            # High activity recovered zone
            {'lat_offset': 0.02, 'lng_offset': 0.02, 'vape_debt': 40, 'vape_restore': 120, 'smoke_debt': 30, 'smoke_restore': 100},
            # Moderate activity recovered zone
            {'lat_offset': 0.02, 'lng_offset': 0.01, 'vape_debt': 15, 'vape_restore': 60, 'smoke_debt': 10, 'smoke_restore': 45},
            # Low activity recovered zone
            {'lat_offset': 0.01, 'lng_offset': 0.02, 'vape_debt': 5, 'vape_restore': 30, 'smoke_debt': 3, 'smoke_restore': 25},
            
            # Healing zones (green) - net score between -20 and 20
            # Close to recovered (needs 11 points)
            {'lat_offset': 0.00, 'lng_offset': 0.02, 'vape_debt': 35, 'vape_restore': 45, 'smoke_debt': 25, 'smoke_restore': 35},
            # Mid-healing (needs 30 points)
            {'lat_offset': 0.01, 'lng_offset': 0.01, 'vape_debt': 50, 'vape_restore': 40, 'smoke_debt': 45, 'smoke_restore': 35},
            # Just entered healing (needs 40 points)
            {'lat_offset': 0.00, 'lng_offset': 0.01, 'vape_debt': 60, 'vape_restore': 45, 'smoke_debt': 55, 'smoke_restore': 40},
            
            # Needs Restoration zones (yellow) - net score < -20
            # Very high activity, needs lots of help
            {'lat_offset': -0.01, 'lng_offset': 0.01, 'vape_debt': 150, 'vape_restore': 20, 'smoke_debt': 120, 'smoke_restore': 15},
            # High activity, moderate debt
            {'lat_offset': -0.01, 'lng_offset': 0.02, 'vape_debt': 80, 'vape_restore': 10, 'smoke_debt': 70, 'smoke_restore': 8},
            # Moderate activity, high debt
            {'lat_offset': -0.02, 'lng_offset': 0.01, 'vape_debt': 65, 'vape_restore': 5, 'smoke_debt': 55, 'smoke_restore': 3},
            # Low activity, just needs restoration
            {'lat_offset': -0.02, 'lng_offset': 0.02, 'vape_debt': 30, 'vape_restore': 2, 'smoke_debt': 25, 'smoke_restore': 1},
        ]
        
        created_zones = []
        
        for demo_zone in demo_zones:
            # Calculate zone location
            lat = center_lat + demo_zone['lat_offset']
            lng = center_lng + demo_zone['lng_offset']
            
            # Create or get zone
            zone = zone_service.create_zone(lat, lng)
            
            # Set demo values
            zone.vape_debt = demo_zone['vape_debt']
            zone.vape_restore = demo_zone['vape_restore']
            zone.smoke_debt = demo_zone['smoke_debt']
            zone.smoke_restore = demo_zone['smoke_restore']
            zone.last_updated = datetime.utcnow()
            
            created_zones.append(zone)
        
        # Save zones to storage
        storage_service.save_zones(zone_service.get_all_zones())
        
        return jsonify({
            'message': f'Demo data seeded successfully with {len(created_zones)} zones',
            'zones_created': len(created_zones),
            'center': {'latitude': center_lat, 'longitude': center_lng}
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/zones/<zone_id>/actions', methods=['GET'])
def get_zone_actions(zone_id):
    """
    Get restoration actions for a specific zone.
    
    Allows users to proactively help any zone without needing to submit a report first.
    
    Query parameters:
        context: 'indoor' or 'outdoor' (optional)
        type: 'vape' or 'smoke' (optional, defaults to 'vape')
    
    Returns:
        JSON object with zone info and suggested actions
    """
    try:
        # Get zone
        zone = zone_service.get_zone(zone_id)
        if not zone:
            return jsonify({'error': 'Zone not found'}), 404
        
        # Get query parameters
        context = request.args.get('context')
        action_type = request.args.get('type', 'vape')
        
        # Validate type
        if action_type not in ['vape', 'smoke']:
            return jsonify({'error': 'Invalid type. Must be "vape" or "smoke"'}), 400
        
        # Get restoration action suggestions
        suggestions = action_service.get_suggestions(
            context=context,
            type=action_type
        )
        
        # Convert suggestions to dictionaries
        suggestions_data = [
            {
                'id': action.id,
                'title': action.title,
                'description': action.description,
                'points': action.points,
                'context': action.context
            }
            for action in suggestions
        ]
        
        # Calculate current state
        vape_state = state_service.calculate_state(zone, 'vape')
        smoke_state = state_service.calculate_state(zone, 'smoke')
        
        return jsonify({
            'zone_id': zone_id,
            'zone': zone.to_dict(),
            'vape_state': vape_state,
            'smoke_state': smoke_state,
            'suggestions': suggestions_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
