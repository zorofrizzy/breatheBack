/**
 * BreatheBack Community Air Restoration App
 * Main application state management and initialization
 */

// ============================================================================
// Application State Structure
// ============================================================================

/**
 * Global application state
 * @type {AppState}
 */
let appState = {
  currentView: 'report',           // Current active view
  currentMapType: 'vape',          // Current heatmap type (vape or smoke)
  zones: new Map(),                // Map<string, Zone> - all zones by ID
  userPoints: null,                // UserPoints object for current day
  events: [],                      // Array of CommunityEvent objects
  currentLocation: null,           // Current user location {latitude, longitude}
  selectedZone: null,              // Currently selected zone ID (for inspector)
  showRestorationCard: false,      // Whether to show restoration action card
  lastReport: null,                // Last submitted report (for action context)
  currentSuggestions: []           // Current action suggestions
};

// ============================================================================
// State Update Functions
// ============================================================================

/**
 * Update the current view
 * @param {string} view - View name: 'report', 'map', 'community'
 */
function updateView(view) {
  const validViews = ['report', 'map', 'community'];
  if (!validViews.includes(view)) {
    console.error(`Invalid view: ${view}`);
    return;
  }
  
  appState.currentView = view;
  saveStateToStorage();
  renderCurrentView();
}

/**
 * Update zones data
 * @param {Map<string, Zone>} zones - Updated zones map
 */
function updateZones(zones) {
  appState.zones = zones;
  saveStateToStorage();
}

/**
 * Update a single zone
 * @param {string} zoneId - Zone identifier
 * @param {Zone} zoneData - Updated zone data
 */
function updateZone(zoneId, zoneData) {
  appState.zones.set(zoneId, zoneData);
  saveStateToStorage();
}

/**
 * Update user points
 * @param {UserPoints} points - Updated user points object
 */
function updatePoints(points) {
  // Convert snake_case from API to camelCase for frontend
  if (points) {
    appState.userPoints = {
      date: points.date,
      totalPoints: points.total_points !== undefined ? points.total_points : points.totalPoints || 0,
      actionsCompleted: points.actions_completed !== undefined ? points.actions_completed : points.actionsCompleted || 0,
      vapePoints: points.vape_points !== undefined ? points.vape_points : points.vapePoints || 0,
      smokePoints: points.smoke_points !== undefined ? points.smoke_points : points.smokePoints || 0,
      actions: points.actions || []
    };
  } else {
    appState.userPoints = points;
  }
  saveStateToStorage();
}

/**
 * Update events list
 * @param {Array<CommunityEvent>} events - Updated events array
 */
function updateEvents(events) {
  appState.events = events;
  saveStateToStorage();
}

/**
 * Update current location
 * @param {Coordinates} location - User's current location
 */
function updateLocation(location) {
  appState.currentLocation = location;
  // Location is transient, don't persist to storage
}

/**
 * Update map type (vape or smoke)
 * @param {string} mapType - 'vape' or 'smoke'
 */
function updateMapType(mapType) {
  if (mapType !== 'vape' && mapType !== 'smoke') {
    console.error(`Invalid map type: ${mapType}`);
    return;
  }
  
  appState.currentMapType = mapType;
  saveStateToStorage();
}

/**
 * Update selected zone
 * @param {string|null} zoneId - Zone ID or null to clear selection
 */
function updateSelectedZone(zoneId) {
  appState.selectedZone = zoneId;
  // Selection is transient, don't persist to storage
}

/**
 * Show restoration action card
 * @param {AirImpactReport} report - The report that triggered the card
 */
function showRestorationActionCard(report) {
  appState.showRestorationCard = true;
  appState.lastReport = report;
  // Card state is transient, don't persist to storage
}

/**
 * Hide restoration action card
 */
function hideRestorationActionCard() {
  appState.showRestorationCard = false;
  appState.lastReport = null;
  // Card state is transient, don't persist to storage
}

/**
 * Get current application state
 * @returns {AppState} Current state object
 */
function getState() {
  return appState;
}

// ============================================================================
// State Persistence (LocalStorage)
// ============================================================================

const STORAGE_KEYS = {
  ZONES: 'breatheback_zones',
  USER_POINTS: 'breatheback_user_points',
  EVENTS: 'breatheback_events',
  LAST_RESET: 'breatheback_last_reset',
  CURRENT_VIEW: 'breatheback_current_view',
  MAP_TYPE: 'breatheback_map_type'
};

/**
 * Save current state to localStorage
 */
function saveStateToStorage() {
  try {
    // Save zones (convert Map to array for JSON serialization)
    const zonesArray = Array.from(appState.zones.entries()).map(([id, zone]) => ({
      id,
      ...zone
    }));
    localStorage.setItem(STORAGE_KEYS.ZONES, JSON.stringify(zonesArray));
    
    // Save user points
    if (appState.userPoints) {
      localStorage.setItem(STORAGE_KEYS.USER_POINTS, JSON.stringify(appState.userPoints));
    }
    
    // Save events
    localStorage.setItem(STORAGE_KEYS.EVENTS, JSON.stringify(appState.events));
    
    // Save UI state
    localStorage.setItem(STORAGE_KEYS.CURRENT_VIEW, appState.currentView);
    localStorage.setItem(STORAGE_KEYS.MAP_TYPE, appState.currentMapType);
    
  } catch (error) {
    console.error('Error saving state to localStorage:', error);
    handleStorageError(error);
  }
}

/**
 * Load state from localStorage
 */
function loadStateFromStorage() {
  try {
    // Load zones
    const zonesData = localStorage.getItem(STORAGE_KEYS.ZONES);
    if (zonesData) {
      const zonesArray = JSON.parse(zonesData);
      appState.zones = new Map(zonesArray.map(zone => [zone.id, zone]));
    }
    
    // Load user points
    const pointsData = localStorage.getItem(STORAGE_KEYS.USER_POINTS);
    if (pointsData) {
      appState.userPoints = JSON.parse(pointsData);
      
      // Check if we need to reset daily points (new day)
      checkDailyReset();
    } else {
      // Initialize user points for today
      initializeUserPoints();
    }
    
    // Load events
    const eventsData = localStorage.getItem(STORAGE_KEYS.EVENTS);
    if (eventsData) {
      appState.events = JSON.parse(eventsData);
    }
    
    // Load UI state
    const currentView = localStorage.getItem(STORAGE_KEYS.CURRENT_VIEW);
    if (currentView) {
      appState.currentView = currentView;
    }
    
    const mapType = localStorage.getItem(STORAGE_KEYS.MAP_TYPE);
    if (mapType) {
      appState.currentMapType = mapType;
    }
    
  } catch (error) {
    console.error('Error loading state from localStorage:', error);
    handleStorageError(error);
  }
}

/**
 * Initialize user points for a new day
 */
function initializeUserPoints() {
  const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
  appState.userPoints = {
    date: today,
    totalPoints: 0,
    actionsCompleted: 0,
    vapePoints: 0,
    smokePoints: 0,
    actions: []
  };
  saveStateToStorage();
}

/**
 * Check if we need to reset daily points (midnight passed)
 */
function checkDailyReset() {
  if (!appState.userPoints) {
    initializeUserPoints();
    return;
  }
  
  const today = new Date().toISOString().split('T')[0];
  const storedDate = appState.userPoints.date;
  
  if (storedDate !== today) {
    // New day - reset points
    console.log('New day detected, resetting daily points');
    initializeUserPoints();
  }
}

/**
 * Clear all data (reset functionality)
 */
function clearAllData() {
  try {
    // Clear zones
    appState.zones.clear();
    
    // Reset user points
    initializeUserPoints();
    
    // Clear events
    appState.events = [];
    
    // Reset UI state
    appState.currentView = 'report';
    appState.currentMapType = 'vape';
    appState.selectedZone = null;
    appState.showRestorationCard = false;
    appState.lastReport = null;
    
    // Save reset timestamp
    localStorage.setItem(STORAGE_KEYS.LAST_RESET, new Date().toISOString());
    
    // Save cleared state
    saveStateToStorage();
    
    console.log('All data cleared successfully');
    
  } catch (error) {
    console.error('Error clearing data:', error);
  }
}

/**
 * Handle storage errors (quota exceeded, etc.)
 * @param {Error} error - Storage error
 */
function handleStorageError(error) {
  if (error.name === 'QuotaExceededError') {
    console.warn('LocalStorage quota exceeded. Consider clearing old data.');
    // Could show UI prompt to user here
  } else {
    console.error('Storage error:', error);
  }
}

// ============================================================================
// View Rendering (Placeholder - will be implemented by components)
// ============================================================================

/**
 * Render the current view
 * This function will be implemented to coordinate component rendering
 */
function renderCurrentView() {
  console.log(`Rendering view: ${appState.currentView}`);
  
  // Hide all views
  const views = ['report', 'map', 'community'];
  views.forEach(view => {
    const element = document.getElementById(`${view}-view`);
    if (element) {
      element.classList.remove('active');
    }
  });
  
  // Show current view
  const currentElement = document.getElementById(`${appState.currentView}-view`);
  if (currentElement) {
    currentElement.classList.add('active');
  }
  
  // Update view-specific components
  if (appState.currentView === 'report' && reportFlow) {
    reportFlow.update();
  }
  
  if (appState.currentView === 'map' && heatmapView) {
    // Update heatmap with current zones
    setTimeout(() => {
      heatmapView.update();
    }, 100);
  }
  
  if (appState.currentView === 'community') {
    if (eventList) {
      eventList.update();
    }
    if (eventForm) {
      eventForm.update();
    }
  }
  
  // Update navigation highlighting
  updateNavigationHighlight();
}

/**
 * Update navigation bar to highlight current view
 */
function updateNavigationHighlight() {
  // Update NavigationBar component if initialized
  if (navigationBar) {
    navigationBar.setCurrentView(appState.currentView);
  } else {
    // Fallback to manual update if component not initialized
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      const view = item.getAttribute('data-view');
      if (view === appState.currentView) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  }
}

// ============================================================================
// Application Initialization
// ============================================================================

// NavigationBar instance
let navigationBar = null;

// ThemeManager instance
let themeManager = null;

// ReportFlow instance (merged Report + Actions)
let reportFlow = null;

// BottomSheetManager instance
let bottomSheetManager = null;

// ActionsView instance
let actionsView = null;

// HeatmapView instance
let heatmapView = null;

// ZoneInspector instance
let zoneInspector = null;

// PointsSummary instance
let pointsSummary = null;

// EventList instance
let eventList = null;

// EventForm instance
let eventForm = null;

/**
 * Initialize the application
 */
function initializeApp() {
  console.log('Initializing BreatheBack application...');
  
  // Load state from localStorage
  loadStateFromStorage();
  
  // Initialize ThemeManager first
  initializeThemeManager();
  
  // Initialize NavigationBar component
  initializeNavigationBar();
  
  // Initialize BottomSheetManager
  initializeBottomSheetManager();
  
  // Initialize ReportFlow component (merged Report + Actions)
  initializeReportFlow();
  
  // Initialize HeatmapView component
  initializeHeatmapView();
  
  // Initialize ZoneInspector component
  initializeZoneInspector();
  
  // Initialize PointsSummary component
  initializePointsSummary();
  
  // Initialize EventList component
  initializeEventList();
  
  // Initialize EventForm component
  initializeEventForm();
  
  // Initialize reset and demo functionality
  initializeResetAndDemo();
  
  // Initialize points chip
  initializePointsChip();
  
  // Render initial view
  renderCurrentView();
  
  // Set up periodic daily reset check (every minute)
  setInterval(checkDailyReset, 60000);
  
  console.log('BreatheBack application initialized');
}

/**
 * Initialize the ThemeManager
 */
function initializeThemeManager() {
  themeManager = new ThemeManager();
  themeManager.init();
  
  // Make globally accessible
  window.themeManager = themeManager;
}

/**
 * Initialize the NavigationBar component
 */
function initializeNavigationBar() {
  navigationBar = new NavigationBar({
    containerId: 'navigation-bar',
    currentView: appState.currentView,
    onViewChange: (view) => {
      updateView(view);
    }
  });
  
  navigationBar.init();
}

/**
 * Initialize points chip
 */
async function initializePointsChip() {
  try {
    const response = await fetch('http://localhost:5000/api/points');
    if (response.ok) {
      const data = await response.json();
      const chipValue = document.getElementById('points-chip-value');
      if (chipValue) {
        chipValue.textContent = data.total_points || 0;
      }
      updatePoints(data);
    }
  } catch (error) {
    console.error('Error loading initial points:', error);
  }
}

/**
 * Initialize the BottomSheetManager
 */
function initializeBottomSheetManager() {
  bottomSheetManager = new BottomSheetManager();
  bottomSheetManager.init();
  
  // Make globally accessible
  window.bottomSheetManager = bottomSheetManager;
}

/**
 * Initialize the ReportFlow component (merged Report + Actions)
 */
function initializeReportFlow() {
  reportFlow = new ReportFlow({
    containerId: 'report-flow-container',
    onActionComplete: (result) => {
      console.log('Action completed:', result);
      
      // Update user points in state
      if (result.totalPoints !== undefined) {
        const pointsData = {
          date: new Date().toISOString().split('T')[0],
          total_points: result.totalPoints,
          actions_completed: result.actionsCompleted || 0,
          vape_points: 0,
          smoke_points: 0
        };
        updatePoints(pointsData);
      }
      
      // Update heatmap if it's initialized
      if (heatmapView) {
        heatmapView.update();
      }
    }
  });
  
  reportFlow.init();
  
  // Make globally accessible
  window.reportFlow = reportFlow;
}

/**
 * Initialize the HeatmapView component
 */
function initializeHeatmapView() {
  heatmapView = new HeatmapView({
    mapContainerId: 'map-container',
    toggleContainerId: 'map-toggle-container',
    legendContainerId: 'map-legend-container',
    mapType: appState.currentMapType,
    onMapTypeToggle: (type) => {
      console.log('Map type toggled:', type);
      updateMapType(type);
    },
    onZoneTap: (zoneInfo) => {
      console.log('Zone tapped:', zoneInfo);
      updateSelectedZone(zoneInfo.zoneId);
      
      // Show zone inspector in bottom sheet
      if (zoneInspector && bottomSheetManager) {
        zoneInspector.show(zoneInfo);
        bottomSheetManager.open('zone');
      }
    }
  });
  
  heatmapView.init();
  
  // Expose globally for other components to access
  window.heatmapView = heatmapView;
}

/**
 * Initialize the ZoneInspector component
 */
function initializeZoneInspector() {
  zoneInspector = new ZoneInspector({
    containerId: 'zone-inspector-container',
    onClose: (zoneInfo) => {
      console.log('Zone inspector closed:', zoneInfo);
      updateSelectedZone(null);
      if (bottomSheetManager) {
        bottomSheetManager.closeAll();
      }
    }
  });
  
  zoneInspector.init();
}

/**
 * Initialize the PointsSummary component
 */
function initializePointsSummary() {
  pointsSummary = new PointsSummary({
    containerId: 'points-summary-container'
  });
  
  pointsSummary.init();
  
  // Expose globally for other components to access
  window.pointsSummary = pointsSummary;
}

/**
 * Initialize the EventList component
 */
function initializeEventList() {
  eventList = new EventList({
    containerId: 'event-list-container',
    onEventTap: (event) => {
      console.log('Event details requested:', event);
      // For now, just log the event details
      // In the future, could show a modal with full event details
    }
  });
  
  eventList.init();
}

/**
 * Initialize the EventForm component
 */
function initializeEventForm() {
  eventForm = new EventForm({
    containerId: 'event-form-container',
    onSubmit: (event) => {
      console.log('Event created:', event);
      
      // Update event list to show new event
      if (eventList) {
        eventList.update();
      }
    },
    onCancel: () => {
      console.log('Event form cancelled');
    }
  });
  
  eventForm.init();
}

/**
 * Set up navigation event listeners
 */
function setupNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const view = item.getAttribute('data-view');
      if (view) {
        updateView(view);
      }
    });
  });
}

// ============================================================================
// Export functions for use by other modules
// ============================================================================

// Make functions available globally for other components
window.BreatheBackApp = {
  // State getters
  getState,
  
  // State updaters
  updateView,
  updateZones,
  updateZone,
  updatePoints,
  updateEvents,
  updateLocation,
  updateMapType,
  updateSelectedZone,
  showRestorationActionCard,
  hideRestorationActionCard,
  
  // Storage functions
  saveStateToStorage,
  loadStateFromStorage,
  clearAllData,
  
  // Initialization
  initializeApp
};

// ============================================================================
// Note: Auto-initialization is handled by main.js
// This prevents double initialization
// ============================================================================

// ============================================================================
// Reset and Demo Functionality
// ============================================================================

/**
 * Show confirmation modal
 * @param {string} title - Modal title
 * @param {string} message - Confirmation message
 * @param {Function} onConfirm - Callback when confirmed
 */
function showConfirmationModal(title, message, onConfirm) {
  // Create modal HTML
  const modalHTML = `
    <div class="confirmation-modal" id="confirmation-modal">
      <div class="confirmation-content">
        <h3>${title}</h3>
        <p>${message}</p>
        <div class="confirmation-actions">
          <button class="btn-cancel" id="cancel-btn">Cancel</button>
          <button class="btn-confirm" id="confirm-btn">Confirm</button>
        </div>
      </div>
    </div>
  `;
  
  // Add modal to body
  document.body.insertAdjacentHTML('beforeend', modalHTML);
  
  const modal = document.getElementById('confirmation-modal');
  const cancelBtn = document.getElementById('cancel-btn');
  const confirmBtn = document.getElementById('confirm-btn');
  
  // Handle cancel
  const handleCancel = () => {
    modal.remove();
  };
  
  // Handle confirm
  const handleConfirm = async () => {
    modal.remove();
    if (onConfirm) {
      await onConfirm();
    }
  };
  
  // Add event listeners
  cancelBtn.addEventListener('click', handleCancel);
  confirmBtn.addEventListener('click', handleConfirm);
  
  // Close on background click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      handleCancel();
    }
  });
}

/**
 * Show success message
 * @param {string} message - Success message to display
 */
function showSuccessMessage(message) {
  const messageHTML = `
    <div class="success-message" id="success-message">
      ${message}
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', messageHTML);
  
  const messageEl = document.getElementById('success-message');
  
  // Remove after 3 seconds
  setTimeout(() => {
    messageEl.style.opacity = '0';
    setTimeout(() => {
      messageEl.remove();
    }, 300);
  }, 3000);
}

/**
 * Reset all application data
 * Requirements: 12.2, 12.3, 12.4
 */
async function resetAllData() {
  try {
    // Call API reset endpoint
    const response = await fetch('http://localhost:5000/api/reset', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to reset data');
    }
    
    // Clear local state
    clearAllData();
    
    // Refresh all views
    await refreshAllViews();
    
    // Return to Report view
    updateView('report');
    
    // Show success message
    showSuccessMessage('Data reset complete. Ready for a fresh start!');
    
    console.log('All data reset successfully');
    
  } catch (error) {
    console.error('Error resetting data:', error);
    alert('Failed to reset data. Please try again.');
  }
}

/**
 * Refresh all views after data change
 */
async function refreshAllViews() {
  try {
    // Reload zones from API
    const zonesResponse = await fetch('http://localhost:5000/api/zones');
    if (zonesResponse.ok) {
      const zonesData = await zonesResponse.json();
      const zonesMap = new Map(zonesData.map(zone => [zone.id, zone]));
      updateZones(zonesMap);
    }
    
    // Reload user points from API
    const pointsResponse = await fetch('http://localhost:5000/api/points');
    if (pointsResponse.ok) {
      const pointsData = await pointsResponse.json();
      updatePoints(pointsData);
    }
    
    // Reload events from API
    const eventsResponse = await fetch('http://localhost:5000/api/events');
    if (eventsResponse.ok) {
      const eventsData = await eventsResponse.json();
      updateEvents(eventsData);
    }
    
    // Update all component views
    if (heatmapView) {
      heatmapView.update();
    }
    
    if (pointsSummary) {
      pointsSummary.update();
    }
    
    if (eventList) {
      eventList.update();
    }
    
    console.log('All views refreshed');
    
  } catch (error) {
    console.error('Error refreshing views:', error);
  }
}

/**
 * Seed demo data with zones in all three states
 * Requirements: 12.1
 */
async function seedDemoData() {
  try {
    // Get user's current location or use default
    let latitude = 37.7749;
    let longitude = -122.4194;
    
    if (navigator.geolocation) {
      try {
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject);
        });
        latitude = position.coords.latitude;
        longitude = position.coords.longitude;
      } catch (error) {
        console.log('Could not get user location, using default');
      }
    }
    
    // Call API to seed demo data
    const response = await fetch('http://localhost:5000/api/seed-demo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude, longitude })
    });
    
    if (!response.ok) {
      throw new Error('Failed to seed demo data');
    }
    
    const result = await response.json();
    
    // Refresh all views
    await refreshAllViews();
    
    // Show success message
    showSuccessMessage(`Demo data loaded! ${result.zones_created} zones created around your location.`);
    
    // Switch to heatmap view to see the zones
    updateView('heatmap');
    
    console.log('Demo data seeded successfully:', result);
    
  } catch (error) {
    console.error('Error seeding demo data:', error);
    alert('Failed to load demo data. Please try again.');
  }
}

/**
 * Initialize reset and demo functionality
 */
function initializeResetAndDemo() {
  const resetBtn = document.getElementById('reset-data-btn');
  const demoBtn = document.getElementById('demo-mode-btn');
  const seedDemoBtn = document.getElementById('seed-demo-btn');
  const forceClearBtn = document.getElementById('force-clear-btn');
  
  console.log('Initializing reset and demo buttons:', {
    resetBtn: !!resetBtn,
    demoBtn: !!demoBtn,
    seedDemoBtn: !!seedDemoBtn,
    forceClearBtn: !!forceClearBtn
  });
  
  // Force clear button - clears everything and reloads
  if (forceClearBtn) {
    forceClearBtn.addEventListener('click', () => {
      console.log('Force clear button clicked');
      showConfirmationModal(
        'Force Clear All Data?',
        'This will clear all local storage and reload the page. Use this if reset is not working.',
        async () => {
          console.log('Force clear confirmed');
          try {
            // Clear all localStorage
            localStorage.clear();
            
            // Call API reset
            await fetch('http://localhost:5000/api/reset', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' }
            });
            
            // Reload page
            window.location.reload();
          } catch (error) {
            console.error('Error during force clear:', error);
            // Reload anyway
            window.location.reload();
          }
        }
      );
    });
  }
  
  // Seed demo data button
  if (seedDemoBtn) {
    seedDemoBtn.addEventListener('click', async () => {
      console.log('Seed demo button clicked');
      showConfirmationModal(
        'Seed Demo Data?',
        'This will create sample zones in all three restoration states around your location.',
        async () => {
          await seedDemoData();
        }
      );
    });
  }
  
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      console.log('Reset button clicked');
      showConfirmationModal(
        'Reset All Data?',
        'This will clear all zones, points, and events. This action cannot be undone.',
        async () => {
          console.log('Reset confirmed, calling resetAllData...');
          await resetAllData();
        }
      );
    });
  }
  
  if (demoBtn) {
    let demoModeActive = false;
    
    demoBtn.addEventListener('click', async () => {
      console.log('Demo mode button clicked');
      if (!demoModeActive) {
        // Enable demo mode
        showConfirmationModal(
          'Enable Demo Mode?',
          'This will populate the app with sample data to demonstrate all features.',
          async () => {
            await seedDemoData();
            demoModeActive = true;
            demoBtn.textContent = 'Disable Demo Mode';
            demoBtn.classList.add('demo-mode-active');
          }
        );
      } else {
        // Disable demo mode (reset data)
        showConfirmationModal(
          'Disable Demo Mode?',
          'This will clear all demo data and reset the app.',
          async () => {
            await resetAllData();
            demoModeActive = false;
            demoBtn.textContent = 'Enable Demo Mode';
            demoBtn.classList.remove('demo-mode-active');
          }
        );
      }
    });
  }
}

// Export reset and demo functions
window.BreatheBackApp.resetAllData = resetAllData;
window.BreatheBackApp.seedDemoData = seedDemoData;
window.BreatheBackApp.refreshAllViews = refreshAllViews;
