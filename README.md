# BreatheBack Community Air Restoration App

**🎗️ Hack4Hope 2025 - Cancer Prevention Through AI-Powered Education**

BreatheBack is a single-page mobile web application that empowers communities to take positive action around air quality restoration. Users can report air impacts (smoke or vape), complete context-aware restoration actions, and visualize community progress through separate restoration maps—all while maintaining a supportive, non-accusatory, and privacy-focused experience.

## 🆕 AI Cancer Impact Feature (Hack4Hope)

**Making Cancer Policy Understandable and Actionable**

BreatheBack now uses AI (via OpenRouter) to translate air quality data into personalized cancer prevention explanations. When users tap a zone on the heatmap, they see:

- **Real-time cancer risk analysis**: AI explains how vaping aerosols and secondhand smoke affect lung and throat cancer risk
- **Personalized to each zone**: Explanations adapt based on actual exposure levels (debt/restore scores)
- **Youth-focused language**: Direct, honest, empowering tone for ages 16-25
- **Immediate impact**: Users understand WHY their actions matter for cancer prevention

**Example**: A zone with high vape debt shows: *"This zone has high exposure to vaping aerosols, which contain carcinogens linked to lung and throat cancer. Your restoration actions can help reduce cancer risk for everyone here."*

### Quick Setup
1. Get an OpenRouter API key: https://openrouter.ai/ (FREE - no credit card!)
2. Create `.env` file in root directory with: `OPENROUTER_API_KEY=your-key`
3. Run: `python test_llm.py` to verify setup
4. Start server: `python app.py`

**Model Used**: Google Gemini Flash 1.5 (100% free, fast, high-quality)

See [LLM_SETUP.md](LLM_SETUP.md) for detailed instructions and [DEMO_GUIDE.md](DEMO_GUIDE.md) for judging presentation tips.

## Philosophy

**"We're helping air heal together."**

BreatheBack prioritizes positive community engagement over blame, uses aggregate zone-level data instead of individual tracking, and presents information through soft language and calming visual design.

## Features

- **🎗️ AI Cancer Impact Explanations**: Real-time LLM-powered cancer risk analysis for each zone
- **Quick Reporting**: Report air impacts (smoke or vape) with minimal taps
- **Context-Aware Actions**: Get tailored restoration suggestions based on indoor/outdoor context
- **Dual Heatmaps**: Separate visualization for vape and smoke restoration states
- **Privacy-First**: All data aggregated at zone level—no individual tracking
- **Points & Progress**: Track your daily contribution to air restoration
- **Community Events**: Schedule and join collective restoration efforts
- **Supportive Design**: Soft colors, encouraging language, and calming aesthetics

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask**: Web framework and API server
- **JSON**: File-based data persistence

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **HTML5**: Semantic markup and Geolocation API
- **CSS3**: Responsive design with soft color palette
- **Leaflet.js**: Interactive map visualization

## Project Structure

```
breatheback-community-app/
├── backend/
│   ├── models/              # Data models
│   │   ├── zone.py
│   │   ├── user_points.py
│   │   ├── community_event.py
│   │   └── air_impact_report.py
│   ├── services/            # Business logic services
│   │   ├── zone_calculation_service.py
│   │   ├── state_calculation_service.py
│   │   ├── action_suggestion_service.py
│   │   └── local_storage_service.py
│   └── constants.py         # Configuration constants
├── frontend/
│   ├── index.html           # Main HTML structure
│   ├── styles.css           # Soft design styling
│   ├── main.js              # Application initialization
│   ├── app.js               # State management
│   ├── navigation.js        # Navigation component
│   ├── reportForm.js        # Report submission
│   ├── restorationActionCard.js  # Action suggestions
│   ├── heatmapView.js       # Map visualization
│   ├── zoneInspector.js     # Zone details modal
│   ├── pointsSummary.js     # User points display
│   ├── eventList.js         # Event listing
│   └── eventForm.js         # Event creation
├── data/                    # JSON data storage
├── app.py                   # Flask application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, or Edge)

### Setup Steps

1. **Clone or download the repository**
   ```bash
   cd breatheback-community-app
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create data directory** (if not exists)
   ```bash
   mkdir data
   ```

## Running the Application

### Start the Flask Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

The application will load with the Report view as the default homepage.

### Enable Location Services

When you first submit a report, your browser will request permission to access your location. Click "Allow" to enable the full functionality of the app.

## API Endpoints

### Zones

- **GET /api/zones**
  - Retrieve all zones with their debt and restoration scores
  - Response: `{ "zones": [...] }`

### Reports

- **POST /api/reports**
  - Submit an air impact report
  - Body: `{ "type": "smoke|vape", "context": "indoor|outdoor", "location": { "latitude": float, "longitude": float } }`
  - Response: `{ "success": true, "zone_id": "...", "zone": {...} }`

### Actions

- **POST /api/actions**
  - Complete a restoration action
  - Body: `{ "action_id": "...", "points": int, "type": "smoke|vape", "zone_id": "..." }`
  - Response: `{ "success": true, "zone": {...}, "user_points": {...} }`

### Points

- **GET /api/points**
  - Retrieve user's daily points
  - Response: `{ "points": {...} }`

- **POST /api/points/reset**
  - Reset daily points (called automatically at midnight)
  - Response: `{ "success": true, "points": {...} }`

### Events

- **GET /api/events**
  - Retrieve all community events
  - Response: `{ "events": [...] }`

- **POST /api/events**
  - Create a new community event
  - Body: `{ "name": "...", "location": "...", "date_time": "...", "duration": int, "type_focus": "smoke|vape|both", "context_hint": "indoor|outdoor" }`
  - Response: `{ "success": true, "event": {...} }`

### Reset

- **POST /api/reset**
  - Reset all application data (zones, points, events)
  - Response: `{ "success": true }`

## Testing

### Backend Tests

Run all Python tests:
```bash
python -m pytest tests/
```

Run specific test files:
```bash
python -m pytest tests/test_zone_calculation_service.py
python -m pytest tests/test_state_calculation_service.py
python -m pytest tests/test_action_suggestion_service.py
python -m pytest tests/test_local_storage_service.py
```

Run API integration tests:
```bash
python -m pytest tests/test_api.py
python -m pytest tests/test_e2e_flow.py
```

### Frontend Tests

Frontend tests are HTML files that can be opened directly in a browser:

1. **State Management Tests**
   - Open `tests/frontend/test_state_management.html` in browser
   - Check console for test results

2. **Component Tests**
   - `tests/frontend/test_navigation.html` - Navigation component
   - `tests/frontend/test_report_form.html` - Report form
   - `tests/frontend/test_restoration_action_card.html` - Action card
   - `tests/frontend/test_heatmap_view.html` - Heatmap visualization
   - `tests/frontend/test_zone_inspector.html` - Zone inspector modal
   - `tests/frontend/test_points_summary.html` - Points summary
   - `tests/frontend/test_event_unit.html` - Event components

3. **Integration Tests**
   - `tests/frontend/test_e2e_flow.html` - End-to-end flow
   - `tests/frontend/test_main_integration.html` - Full application integration
   - `tests/frontend/test_checkpoint_21_integration.html` - Comprehensive checkpoint

### Test Coverage

The test suite includes:
- Unit tests for all services and models
- Integration tests for API endpoints
- Component tests for all UI elements
- End-to-end tests for complete user flows
- Property-based tests for correctness properties (optional)

## Demo Mode

### Using Demo Mode

1. Open the application in your browser
2. Navigate to the Heatmap view
3. The application includes seeded demo data showing zones in all three restoration states

### Seeded Demo Data

Demo mode includes:
- Zones in "Needs Restoration" state (yellow)
- Zones in "Healing" state (green)
- Zones in "Recovered" state (blue)
- Both vape and smoke data for comprehensive visualization

### Reset Functionality

To reset all data and start fresh:

1. Open browser console (F12)
2. Run: `fetch('/api/reset', { method: 'POST' })`
3. Refresh the page

Or use the test file:
- Open `frontend/test_reset_demo.html` in browser
- Click "Reset All Data" button

## Usage Guide

### Reporting an Air Impact

1. Navigate to the **Report** view (default on load)
2. Select the type: **Smoke** or **Vape**
3. Optionally select context: **Indoor** or **Outdoor**
4. Tap **Submit Report**
5. Allow location access when prompted
6. View suggested restoration actions

### Completing Restoration Actions

1. After submitting a report, view the action card
2. Choose from 3-5 context-aware actions
3. Tap an action to complete it
4. Earn Clean Air Points
5. See positive feedback

### Viewing the Heatmap

1. Navigate to the **Heatmap** view
2. Toggle between **Vape Map** and **Smoke Map**
3. View color-coded zones:
   - 🟡 **Yellow**: Needs Restoration
   - 🟢 **Green**: Healing
   - 🔵 **Blue**: Recovered
4. Tap any zone to see its restoration state message

### Checking Your Points

1. Navigate to the **My Points** view
2. See your total points earned today
3. View number of actions completed
4. Read your feel-good summary message
5. Points reset automatically at midnight

### Creating Community Events

1. Navigate to the **Community** view
2. Tap **Create Event** (or scroll to form)
3. Fill in event details:
   - Name
   - Location
   - Date and Time
   - Duration
   - Type Focus (Vape, Smoke, or Both)
   - Context Hint (optional)
4. Submit to create the event
5. View upcoming events in the list

## Configuration

### Zone Grid Size

Edit `backend/constants.py` to adjust zone grid size:

```python
ZONE_GRID_SIZE = 0.01  # degrees (approximately 1km at equator)
```

### Restoration Thresholds

Edit `backend/constants.py` to adjust state thresholds:

```python
DEBT_INCREMENT = 10           # Points added per report
RECOVERED_THRESHOLD = 20      # Net score for "Recovered" state
HEALING_THRESHOLD = -20       # Net score for "Healing" state
```

### Action Points

Edit `backend/services/action_suggestion_service.py` to modify action point values and descriptions.

## Privacy & Data

### What Data is Stored

- **Zone-level aggregated data**: Debt and restoration scores per zone
- **User daily points**: Total points and action count (resets daily)
- **Community events**: Public event information

### What Data is NOT Stored

- Individual user identities
- Exact report locations (only zone IDs)
- Individual report timestamps
- Context information (used only for action suggestions)
- Venue-specific details

### Data Persistence

All data is stored locally in JSON files in the `data/` directory:
- `zones.json` - Zone data
- `user_points.json` - Daily points
- `events.json` - Community events

## Troubleshooting

### Location Permission Denied

If you deny location permission:
- The app will show an error message
- You can enable location in browser settings
- Or manually allow when prompted again

### Server Won't Start

Check that:
- Python 3.8+ is installed: `python --version`
- Virtual environment is activated
- Dependencies are installed: `pip install -r requirements.txt`
- Port 5000 is not in use by another application

### Map Not Loading

Ensure:
- Internet connection is active (for Leaflet.js CDN)
- Browser supports JavaScript and has it enabled
- No browser extensions blocking map resources

### Data Not Persisting

Check that:
- `data/` directory exists and is writable
- Flask server has write permissions
- JSON files are not corrupted

## Browser Compatibility

Tested and supported on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Mobile browsers:
- Chrome Mobile (Android)
- Safari Mobile (iOS)

## Contributing

This is a proof-of-concept application. For improvements:
1. Test thoroughly before making changes
2. Follow the existing code style
3. Update tests for new features
4. Document API changes in this README

## License

This project is a demonstration application for community air restoration efforts.

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the test files for usage examples
3. Inspect browser console for error messages
4. Check Flask server logs for backend errors

## Acknowledgments

Built with a focus on:
- Privacy-preserving design
- Supportive, non-accusatory language
- Community empowerment
- Positive behavioral change

---

**Remember: We're helping air heal together. 🌬️💙**
