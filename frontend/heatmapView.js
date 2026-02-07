/**
 * HeatmapView Component
 * Visualizes zone restoration states with separate vape/smoke maps
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 7.1
 */

class HeatmapView {
  /**
   * Create a HeatmapView instance
   * @param {Object} options - Configuration options
   * @param {string} options.mapContainerId - ID of the map container element
   * @param {string} options.toggleContainerId - ID of the toggle control container
   * @param {string} options.legendContainerId - ID of the legend container
   * @param {string} options.mapType - Initial map type ('vape' or 'smoke')
   * @param {Function} options.onMapTypeToggle - Callback when map type changes
   * @param {Function} options.onZoneTap - Callback when zone is tapped
   */
  constructor(options = {}) {
    this.mapContainerId = options.mapContainerId || 'map-container';
    this.toggleContainerId = options.toggleContainerId || 'map-toggle-container';
    this.legendContainerId = options.legendContainerId || 'map-legend-container';
    this.mapType = options.mapType || 'vape';
    this.onMapTypeToggle = options.onMapTypeToggle || (() => {});
    this.onZoneTap = options.onZoneTap || (() => {});
    
    // Map instance
    this.map = null;
    this.zoneOverlays = new Map(); // Map of zone ID to Leaflet layer
    this.userLocationMarker = null; // User location marker
    this.userZoneHighlight = null; // Highlight for user's current zone
    
    // Containers
    this.mapContainer = null;
    this.toggleContainer = null;
    this.legendContainer = null;
    
    // State calculation thresholds (matching backend constants)
    this.RECOVERED_THRESHOLD = 20;
    this.HEALING_THRESHOLD = -20;
    
    // State colors (matching backend)
    this.stateColors = {
      'needs_restoration': '#F4D03F',  // Soft yellow
      'healing': '#52BE80',             // Soft green
      'recovered': '#5DADE2'            // Soft blue
    };
    
    // State messages (matching backend)
    this.stateMessages = {
      'needs_restoration': 'This space needs care',
      'healing': 'This space is healing',
      'recovered': 'This space has recovered'
    };
  }
  
  /**
   * Initialize the heatmap view
   */
  init() {
    this.mapContainer = document.getElementById(this.mapContainerId);
    this.toggleContainer = document.getElementById(this.toggleContainerId);
    this.legendContainer = document.getElementById(this.legendContainerId);
    
    if (!this.mapContainer) {
      console.error(`HeatmapView: Map container with id "${this.mapContainerId}" not found`);
      return;
    }
    
    // Initialize map
    this.initializeMap();
    
    // Render toggle control
    if (this.toggleContainer) {
      this.renderToggleControl();
    }
    
    // Render legend
    if (this.legendContainer) {
      this.renderLegend();
    }
  }
  
  /**
   * Initialize Leaflet map
   */
  initializeMap() {
    if (!this.mapContainer) {
      console.error('HeatmapView: Map container not initialized');
      return;
    }
    
    // Show loading indicator
    this.showLoadingIndicator();
    
    try {
      // Create Leaflet map centered on a default location
      // Using San Francisco as default center
      this.map = L.map(this.mapContainerId, {
        center: [37.7749, -122.4194],
        zoom: 13,
        zoomControl: true,
        attributionControl: true,
        preferCanvas: true // Better performance for many overlays
      });
      
      // Add tile layer with multiple fallback servers
      const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
        minZoom: 10,
        subdomains: ['a', 'b', 'c'],
        errorTileUrl: '', // Don't show broken tile images
        crossOrigin: true
      });
      
      // Add event listeners for tile loading
      tileLayer.on('loading', () => {
        console.log('Map tiles loading...');
      });
      
      tileLayer.on('load', () => {
        console.log('Map tiles loaded successfully');
        this.hideLoadingIndicator();
      });
      
      tileLayer.on('tileerror', (error) => {
        console.warn('Tile loading error:', error);
        // Try alternative tile server if primary fails
        this.tryAlternativeTileServer();
      });
      
      // Add tile layer to map
      tileLayer.addTo(this.map);
      this.tileLayer = tileLayer;
      
      // Add custom location control
      this.addLocationControl();
      
      // Force map to invalidate size after a short delay
      // This fixes issues with map not rendering properly
      setTimeout(() => {
        if (this.map) {
          this.map.invalidateSize();
          this.hideLoadingIndicator();
        }
      }, 500);
      
      // Try to center on user's location if available
      this.centerOnUserLocation();
      
    } catch (error) {
      console.error('Error initializing map:', error);
      this.showMapError('Failed to initialize map. Please refresh the page.');
      this.hideLoadingIndicator();
    }
  }
  
  /**
   * Try alternative tile server if primary fails
   */
  tryAlternativeTileServer() {
    if (this.alternativeTileServerTried) {
      return; // Already tried alternative
    }
    
    this.alternativeTileServerTried = true;
    console.log('Trying alternative tile server...');
    
    // Remove existing tile layer
    if (this.tileLayer && this.map) {
      this.map.removeLayer(this.tileLayer);
    }
    
    // Try CartoDB tile server as alternative
    this.tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      maxZoom: 19,
      minZoom: 10,
      subdomains: 'abcd'
    });
    
    this.tileLayer.on('load', () => {
      console.log('Alternative tile server loaded successfully');
      this.hideLoadingIndicator();
    });
    
    this.tileLayer.addTo(this.map);
  }
  
  /**
   * Show loading indicator
   */
  showLoadingIndicator() {
    if (!this.mapContainer) return;
    
    // Check if loading indicator already exists
    let loadingEl = this.mapContainer.querySelector('.map-loading');
    if (loadingEl) return;
    
    // Create loading indicator
    loadingEl = document.createElement('div');
    loadingEl.className = 'map-loading';
    loadingEl.innerHTML = `
      <div class="loading-spinner"></div>
      <p>Loading map...</p>
    `;
    this.mapContainer.appendChild(loadingEl);
  }
  
  /**
   * Hide loading indicator
   */
  hideLoadingIndicator() {
    if (!this.mapContainer) return;
    
    const loadingEl = this.mapContainer.querySelector('.map-loading');
    if (loadingEl) {
      loadingEl.remove();
    }
  }
  
  /**
   * Show map error message
   * @param {string} message - Error message to display
   */
  showMapError(message) {
    if (!this.mapContainer) return;
    
    const errorEl = document.createElement('div');
    errorEl.className = 'map-error';
    errorEl.innerHTML = `
      <p>${message}</p>
      <button class="btn-primary" onclick="location.reload()">Refresh Page</button>
    `;
    this.mapContainer.appendChild(errorEl);
  }
  
  /**
   * Center map on user's current location
   */
  centerOnUserLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          this.map.setView([lat, lng], 13);
          
          // Add user location marker
          this.addUserLocationMarker(lat, lng);
        },
        (error) => {
          console.log('Could not get user location, using default center');
        }
      );
    }
  }
  
  /**
   * Add or update user location marker on the map
   * @param {number} lat - Latitude
   * @param {number} lng - Longitude
   */
  addUserLocationMarker(lat, lng) {
    // Remove existing marker if any
    if (this.userLocationMarker) {
      this.map.removeLayer(this.userLocationMarker);
    }
    
    // Create custom icon for user location
    const userIcon = L.divIcon({
      className: 'user-location-marker',
      html: `
        <div class="user-marker-outer">
          <div class="user-marker-inner"></div>
        </div>
      `,
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    });
    
    // Add marker to map
    this.userLocationMarker = L.marker([lat, lng], {
      icon: userIcon,
      zIndexOffset: 1000 // Ensure it's above zone overlays
    }).addTo(this.map);
    
    // Calculate which zone the user is in
    const zoneId = this.calculateZoneId(lat, lng);
    
    // Add popup with zone info
    this.userLocationMarker.bindPopup(`📍 You are here<br><small>Zone: ${zoneId}</small>`);
    
    // Highlight the user's current zone
    this.highlightUserZone(lat, lng);
  }
  
  /**
   * Calculate zone ID from coordinates (matching backend logic)
   * @param {number} lat - Latitude
   * @param {number} lng - Longitude
   * @returns {string} Zone ID
   */
  calculateZoneId(lat, lng) {
    const ZONE_GRID_SIZE = 0.01;
    const latGrid = Math.floor(lat / ZONE_GRID_SIZE);
    const lngGrid = Math.floor(lng / ZONE_GRID_SIZE);
    return `zone_${latGrid}_${lngGrid}`;
  }
  
  /**
   * Highlight the zone the user is currently in
   * @param {number} lat - Latitude
   * @param {number} lng - Longitude
   */
  highlightUserZone(lat, lng) {
    // Remove existing highlight if any
    if (this.userZoneHighlight) {
      this.map.removeLayer(this.userZoneHighlight);
    }
    
    // Calculate zone boundaries
    const ZONE_GRID_SIZE = 0.01;
    const latGrid = Math.floor(lat / ZONE_GRID_SIZE);
    const lngGrid = Math.floor(lng / ZONE_GRID_SIZE);
    
    const south = latGrid * ZONE_GRID_SIZE;
    const north = (latGrid + 1) * ZONE_GRID_SIZE;
    const west = lngGrid * ZONE_GRID_SIZE;
    const east = (lngGrid + 1) * ZONE_GRID_SIZE;
    
    // Calculate zone ID for this location
    const userZoneId = this.calculateZoneId(lat, lng);
    
    // Create highlighted rectangle for user's zone
    this.userZoneHighlight = L.rectangle(
      [[south, west], [north, east]],
      {
        color: '#4A90E2',
        fillColor: '#4A90E2',
        fillOpacity: 0.1,
        weight: 3,
        opacity: 0.8,
        dashArray: '5, 5',
        interactive: true  // Make sure it's interactive
      }
    ).addTo(this.map);
    
    // Add click handler to user zone highlight
    // This ensures clicks on the user's zone work properly
    this.userZoneHighlight.on('click', () => {
      console.log('User zone highlight clicked:', userZoneId);
      // Get the state for this zone
      const zones = this.getCurrentZones();
      const zone = zones.find(z => z.id === userZoneId);
      
      if (zone) {
        const state = this.calculateState(zone, this.mapType);
        this.handleZoneTap(userZoneId, state);
      } else {
        // Zone doesn't exist yet, show default state
        this.handleZoneTap(userZoneId, 'needs_restoration');
      }
    });
    
    // Add to map with lower z-index than user marker
    this.userZoneHighlight.setStyle({ zIndex: 500 });
  }
  
  /**
   * Update user location marker
   */
  updateUserLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          this.addUserLocationMarker(lat, lng);
        },
        (error) => {
          console.log('Could not update user location');
        }
      );
    }
  }
  
  /**
   * Render toggle control for Vape | Smoke | All map types
   */
  renderToggleControl() {
    if (!this.toggleContainer) {
      console.error('HeatmapView: Toggle container not initialized');
      return;
    }
    
    this.toggleContainer.innerHTML = `
      <div class="map-toggle">
        <button 
          class="toggle-button ${this.mapType === 'vape' ? 'active' : ''}" 
          data-type="vape"
          aria-label="Show vape map"
          aria-pressed="${this.mapType === 'vape'}"
        >
          Vape
        </button>
        <button 
          class="toggle-button ${this.mapType === 'smoke' ? 'active' : ''}" 
          data-type="smoke"
          aria-label="Show smoke map"
          aria-pressed="${this.mapType === 'smoke'}"
        >
          Smoke
        </button>
        <button 
          class="toggle-button ${this.mapType === 'all' ? 'active' : ''}" 
          data-type="all"
          aria-label="Show combined map"
          aria-pressed="${this.mapType === 'all'}"
        >
          All
        </button>
      </div>
    `;
    
    // Attach event listeners
    const toggleButtons = this.toggleContainer.querySelectorAll('.toggle-button');
    toggleButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const type = button.getAttribute('data-type');
        this.handleMapTypeToggle(type);
      });
    });
  }
  
  /**
   * Add custom location control to the map
   */
  addLocationControl() {
    if (!this.map) {
      return;
    }
    
    // Create custom Leaflet control for centering on user location
    const LocationControl = L.Control.extend({
      options: {
        position: 'bottomright'
      },
      
      onAdd: (map) => {
        const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
        
        container.innerHTML = `
          <a href="#" class="leaflet-control-location" title="Center on my location" role="button" aria-label="Center on my location">
            <span class="location-icon">📍</span>
          </a>
        `;
        
        container.style.backgroundColor = 'white';
        container.style.width = '34px';
        container.style.height = '34px';
        container.style.cursor = 'pointer';
        
        container.onclick = (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.centerOnUserLocationOnly();
        };
        
        return container;
      }
    });
    
    // Add the control to the map
    this.map.addControl(new LocationControl());
  }
  
  /**
   * Center map on user location without changing zoom
   */
  centerOnUserLocationOnly() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          
          // Pan to location without changing zoom
          this.map.panTo([lat, lng]);
          
          // Update user location marker
          this.addUserLocationMarker(lat, lng);
        },
        (error) => {
          console.log('Could not get user location:', error);
          alert('Unable to get your location. Please enable location services.');
        }
      );
    } else {
      alert('Geolocation is not supported by your browser.');
    }
  }
  
  /**
   * Handle map type toggle
   * @param {string} type - Map type ('vape', 'smoke', or 'all')
   */
  async handleMapTypeToggle(type) {
    if (type !== 'vape' && type !== 'smoke' && type !== 'all') {
      console.error(`Invalid map type: ${type}`);
      return;
    }
    
    if (type === this.mapType) {
      // Already on this map type
      return;
    }
    
    // Update map type
    this.mapType = type;
    
    // Update toggle button states
    if (this.toggleContainer) {
      const toggleButtons = this.toggleContainer.querySelectorAll('.toggle-button');
      toggleButtons.forEach(button => {
        const buttonType = button.getAttribute('data-type');
        if (buttonType === type) {
          button.classList.add('active');
          button.setAttribute('aria-pressed', 'true');
        } else {
          button.classList.remove('active');
          button.setAttribute('aria-pressed', 'false');
        }
      });
    }
    
    // Update legend
    this.renderLegend();
    
    // Fetch fresh zones from API and re-render
    try {
      const response = await fetch('http://localhost:5000/api/zones');
      if (response.ok) {
        const zones = await response.json();
        console.log(`Rendering ${zones.length} zones for map type: ${type}`);
        this.renderZones(zones, type);
      } else {
        console.error('Failed to fetch zones:', response.statusText);
        // Fallback to current zones if API fails
        const zones = this.getCurrentZones();
        this.renderZones(zones, type);
      }
    } catch (error) {
      console.error('Error fetching zones:', error);
      // Fallback to current zones if API fails
      const zones = this.getCurrentZones();
      this.renderZones(zones, type);
    }
    
    // Call callback
    this.onMapTypeToggle(type);
  }
  
  /**
   * Render legend based on current map type
   */
  renderLegend() {
    if (!this.legendContainer) {
      console.error('HeatmapView: Legend container not initialized');
      return;
    }
    
    let mapTypeLabel;
    if (this.mapType === 'vape') {
      mapTypeLabel = 'Vape';
    } else if (this.mapType === 'smoke') {
      mapTypeLabel = 'Smoke';
    } else {
      mapTypeLabel = 'Combined (Vape + Smoke)';
    }
    
    this.legendContainer.innerHTML = `
      <div class="map-legend">
        <h3 class="legend-title">${mapTypeLabel} Restoration States</h3>
        <div class="legend-items">
          <div class="legend-item">
            <span class="legend-color" style="background-color: ${this.stateColors.recovered}"></span>
            <span class="legend-label">Recovered</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background-color: ${this.stateColors.healing}"></span>
            <span class="legend-label">Healing</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background-color: ${this.stateColors.needs_restoration}"></span>
            <span class="legend-label">Needs Restoration</span>
          </div>
        </div>
      </div>
    `;
  }
  
  /**
   * Calculate restoration state for a zone
   * @param {Object} zone - Zone object
   * @param {string} mapType - Map type ('vape', 'smoke', or 'all')
   * @returns {string} Restoration state ('needs_restoration', 'healing', or 'recovered')
   */
  calculateState(zone, mapType) {
    // Get the appropriate debt and restoration scores based on type
    let debt, restore;
    
    if (mapType === 'vape') {
      debt = zone.vape_debt || zone.vapeDebt || 0;
      restore = zone.vape_restore || zone.vapeRestore || 0;
    } else if (mapType === 'smoke') {
      debt = zone.smoke_debt || zone.smokeDebt || 0;
      restore = zone.smoke_restore || zone.smokeRestore || 0;
    } else if (mapType === 'all') {
      // Combine both vape and smoke data
      const vapeDebt = zone.vape_debt || zone.vapeDebt || 0;
      const vapeRestore = zone.vape_restore || zone.vapeRestore || 0;
      const smokeDebt = zone.smoke_debt || zone.smokeDebt || 0;
      const smokeRestore = zone.smoke_restore || zone.smokeRestore || 0;
      
      debt = vapeDebt + smokeDebt;
      restore = vapeRestore + smokeRestore;
    } else {
      // Default to vape if invalid type
      debt = zone.vape_debt || zone.vapeDebt || 0;
      restore = zone.vape_restore || zone.vapeRestore || 0;
    }
    
    // Calculate net score
    const netScore = restore - debt;
    
    // Apply thresholds to determine state
    if (netScore > this.RECOVERED_THRESHOLD) {
      return 'recovered';
    } else if (netScore > this.HEALING_THRESHOLD) {
      return 'healing';
    } else {
      return 'needs_restoration';
    }
  }
  
  /**
   * Render zones as colored overlays on the map
   * @param {Array} zones - Array of zone objects
   * @param {string} mapType - Map type ('vape' or 'smoke')
   */
  renderZones(zones, mapType) {
    if (!this.map) {
      console.error('HeatmapView: Map not initialized');
      return;
    }
    
    // Clear existing zone overlays
    this.clearZoneOverlays();
    
    // Render each zone
    zones.forEach(zone => {
      this.renderZone(zone, mapType);
    });
  }
  
  /**
   * Render a single zone as a colored overlay
   * @param {Object} zone - Zone object
   * @param {string} mapType - Map type ('vape', 'smoke', or 'all')
   */
  renderZone(zone, mapType) {
    if (!this.map) {
      console.error('HeatmapView: Map not initialized');
      return;
    }
    
    // Calculate state for this zone
    const state = this.calculateState(zone, mapType);
    
    // Get color for this state
    const color = this.stateColors[state];
    
    console.log(`Rendering zone ${zone.id}: state=${state}, color=${color}, mapType=${mapType}`);
    
    // Get zone bounds
    const bounds = zone.bounds;
    if (!bounds) {
      console.error('Zone missing bounds:', zone);
      return;
    }
    
    // Create rectangle overlay
    const rectangle = L.rectangle(
      [
        [bounds.south, bounds.west],
        [bounds.north, bounds.east]
      ],
      {
        color: color,
        fillColor: color,
        fillOpacity: 0.5,  // Increased from 0.4 for better visibility
        weight: 2,         // Increased from 1 for clearer boundaries
        opacity: 0.8       // Increased from 0.6 for clearer boundaries
      }
    );
    
    // Add click handler for zone tap
    rectangle.on('click', () => {
      this.handleZoneTap(zone.id, state);
    });
    
    // Add to map
    rectangle.addTo(this.map);
    
    // Store overlay for later removal
    this.zoneOverlays.set(zone.id, rectangle);
  }
  
  /**
   * Clear all zone overlays from the map
   */
  clearZoneOverlays() {
    this.zoneOverlays.forEach((overlay, zoneId) => {
      if (this.map) {
        this.map.removeLayer(overlay);
      }
    });
    this.zoneOverlays.clear();
  }
  
  /**
   * Handle zone tap
   * @param {string} zoneId - Zone ID
   * @param {string} state - Zone restoration state
   */
  handleZoneTap(zoneId, state) {
    console.log(`Zone tapped: ${zoneId}, state: ${state}`);
    
    // Get state message
    const message = this.stateMessages[state];
    
    // Call callback with zone info
    this.onZoneTap({
      zoneId,
      state,
      message,
      mapType: this.mapType // Include current map type
    });
  }
  
  /**
   * Get current zones from app state
   * @returns {Array} Array of zone objects
   */
  getCurrentZones() {
    // Get zones from global app state
    if (window.BreatheBackApp) {
      const state = window.BreatheBackApp.getState();
      if (state && state.zones) {
        // Convert Map to Array
        return Array.from(state.zones.values());
      }
    }
    
    return [];
  }
  
  /**
   * Update the heatmap with current zones
   */
  async update() {
    console.log('HeatmapView.update() called');
    
    // Ensure map is properly sized when view becomes visible
    if (this.map) {
      // Small delay to ensure container is visible
      setTimeout(() => {
        this.map.invalidateSize();
      }, 100);
    }
    
    // Update user location marker
    this.updateUserLocation();
    
    // Fetch zones from API with cache busting
    try {
      console.log('Fetching zones from API...');
      const response = await fetch('http://localhost:5000/api/zones', {
        cache: 'no-cache',
        headers: {
          'Cache-Control': 'no-cache'
        }
      });
      
      if (response.ok) {
        const zones = await response.json();
        console.log(`Fetched ${zones.length} zones, rendering for map type: ${this.mapType}`);
        
        // Log a sample zone to see the data
        if (zones.length > 0) {
          console.log('Sample zone data:', zones[0]);
        }
        
        this.renderZones(zones, this.mapType);
      } else {
        console.error('Failed to fetch zones:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching zones:', error);
    }
  }
  
  /**
   * Set map type and update display
   * @param {string} type - Map type ('vape' or 'smoke')
   */
  setMapType(type) {
    this.handleMapTypeToggle(type);
  }
  
  /**
   * Get current map type
   * @returns {string} Current map type
   */
  getMapType() {
    return this.mapType;
  }
  
  /**
   * Destroy the heatmap view (cleanup)
   */
  destroy() {
    // Clear zone overlays
    this.clearZoneOverlays();
    
    // Remove map
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
    
    // Clear containers
    if (this.toggleContainer) {
      this.toggleContainer.innerHTML = '';
    }
    
    if (this.legendContainer) {
      this.legendContainer.innerHTML = '';
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = HeatmapView;
}

// Make available globally
if (typeof window !== 'undefined') {
  window.HeatmapView = HeatmapView;
}
