/**
 * BreatheBack Community Air Restoration App
 * Main application entry point - wires all components together
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
 */

// ============================================================================
// Application Initialization and Component Wiring
// ============================================================================

/**
 * Main application initialization function
 * This is the entry point that wires all components together
 */
function initializeBreatheBackApp() {
  console.log('Starting BreatheBack application initialization...');
  
  // Check if all required components are loaded
  if (!validateComponentsLoaded()) {
    console.error('Not all required components are loaded. Cannot initialize app.');
    return;
  }
  
  // Initialize the application through the BreatheBackApp module
  // This will:
  // 1. Load state from localStorage
  // 2. Initialize all components (NavigationBar, ReportForm, HeatmapView, etc.)
  // 3. Set up event listeners for view changes
  // 4. Implement view routing logic
  // 5. Set Report view as default on load
  // 6. Start periodic daily reset check
  
  if (window.BreatheBackApp && typeof window.BreatheBackApp.initializeApp === 'function') {
    window.BreatheBackApp.initializeApp();
    console.log('BreatheBack application initialized successfully');
  } else {
    console.error('BreatheBackApp module not found or initializeApp function missing');
  }
}

/**
 * Validate that all required components are loaded
 * @returns {boolean} True if all components are loaded
 */
function validateComponentsLoaded() {
  const requiredComponents = [
    'NavigationBar',
    'ReportFlow',
    'BottomSheetManager',
    'HeatmapView',
    'ZoneInspector',
    'PointsSummary',
    'EventList',
    'EventForm',
    'BreatheBackApp'
  ];
  
  const missingComponents = [];
  
  for (const component of requiredComponents) {
    if (!window[component]) {
      missingComponents.push(component);
    }
  }
  
  if (missingComponents.length > 0) {
    console.error('Missing required components:', missingComponents);
    console.log('Available components:', Object.keys(window).filter(k => k.includes('Back') || k.includes('View') || k.includes('Flow')));
    return false;
  }
  
  return true;
}

/**
 * Check if Flask backend is running
 * @returns {Promise<boolean>} True if backend is accessible
 */
async function checkBackendStatus() {
  try {
    const response = await fetch('http://localhost:5000/api/zones', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    return response.ok;
  } catch (error) {
    console.error('Backend not accessible:', error);
    return false;
  }
}

/**
 * Display backend connection error
 */
function displayBackendError() {
  const app = document.getElementById('app');
  if (app) {
    const errorHTML = `
      <div class="backend-error">
        <div class="error-content">
          <h2>⚠️ Backend Connection Error</h2>
          <p>Unable to connect to the BreatheBack backend server.</p>
          <p>Please ensure the Flask server is running:</p>
          <pre>python app.py</pre>
          <button onclick="location.reload()" class="btn-primary">Retry Connection</button>
        </div>
      </div>
    `;
    app.innerHTML = errorHTML;
  }
}

/**
 * Initialize the application when DOM is ready
 */
async function onDOMReady() {
  console.log('DOM ready, checking backend status...');
  
  // Check if backend is running
  const backendAvailable = await checkBackendStatus();
  
  if (!backendAvailable) {
    console.warn('Backend server not available. Some features may not work.');
    // Still initialize the app - it can work with localStorage
  }
  
  // Initialize the application
  try {
    initializeBreatheBackApp();
  } catch (error) {
    console.error('Error initializing app:', error);
    // Show error to user
    const app = document.getElementById('app');
    if (app) {
      app.innerHTML = `
        <div style="padding: 40px; text-align: center;">
          <h1>⚠️ Initialization Error</h1>
          <p>Failed to initialize the application.</p>
          <p style="color: #666; font-size: 14px;">${error.message}</p>
          <button onclick="location.reload()" style="margin-top: 20px; padding: 10px 20px; background: #0366D6; color: white; border: none; border-radius: 6px; cursor: pointer;">
            Reload Page
          </button>
        </div>
      `;
    }
  }
}

// ============================================================================
// Auto-initialize when DOM is ready
// ============================================================================

if (document.readyState === 'loading') {
  // DOM is still loading, wait for DOMContentLoaded event
  document.addEventListener('DOMContentLoaded', onDOMReady);
} else {
  // DOM already loaded, initialize immediately
  onDOMReady();
}

// ============================================================================
// Export for testing and debugging
// ============================================================================

window.BreatheBackMain = {
  initializeBreatheBackApp,
  validateComponentsLoaded,
  checkBackendStatus
};

