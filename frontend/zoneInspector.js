/**
 * ZoneInspector Component
 * Displays zone restoration state information in a modal/bottom sheet
 * Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
 */

class ZoneInspector {
  /**
   * Create a ZoneInspector instance
   * @param {Object} options - Configuration options
   * @param {string} options.containerId - ID of the container element
   * @param {Function} options.onClose - Callback when inspector is closed
   */
  constructor(options = {}) {
    this.containerId = options.containerId || 'zone-inspector-container';
    this.onClose = options.onClose || (() => {});
    
    // Current zone data
    this.currentZone = null;
    
    // State messages (matching backend and heatmap)
    this.stateMessages = {
      'needs_restoration': 'This space needs care',
      'healing': 'This space is healing',
      'recovered': 'This space has recovered'
    };
    
    // State colors for visual feedback
    this.stateColors = {
      'needs_restoration': '#F4D03F',  // Soft yellow
      'healing': '#52BE80',             // Soft green
      'recovered': '#5DADE2'            // Soft blue
    };
    
    // Container element
    this.container = null;
  }
  
  /**
   * Initialize the zone inspector
   */
  init() {
    this.container = document.getElementById(this.containerId);
    
    if (!this.container) {
      console.error(`ZoneInspector: Container with id "${this.containerId}" not found`);
      return;
    }
    
    // Initially hidden
    this.hide();
  }
  
  /**
   * Show the zone inspector with zone information
   * @param {Object} zoneInfo - Zone information object
   * @param {string} zoneInfo.zoneId - Zone ID
   * @param {string} zoneInfo.state - Zone restoration state
   * @param {string} zoneInfo.message - State message (optional, will use default if not provided)
   */
  async show(zoneInfo) {
    if (!this.container) {
      console.error('ZoneInspector: Container not initialized');
      return;
    }
    
    if (!zoneInfo || !zoneInfo.state) {
      console.error('ZoneInspector: Invalid zone info provided');
      return;
    }
    
    // Store current zone
    this.currentZone = zoneInfo;
    
    console.log('ZoneInspector.show called with:', zoneInfo);
    
    // Fetch full zone data from API to get debt/restore scores
    // IMPORTANT: Always fetch fresh data, don't use cached data
    let zoneData = null;
    try {
      console.log('Fetching fresh zone data from API...');
      const response = await fetch('http://localhost:5000/api/zones', {
        cache: 'no-cache',  // Force fresh data
        headers: {
          'Cache-Control': 'no-cache'
        }
      });
      
      if (response.ok) {
        const zones = await response.json();
        console.log(`Fetched ${zones.length} zones from API`);
        zoneData = zones.find(z => z.id === zoneInfo.zoneId);
        
        if (zoneData) {
          console.log('Found zone data:', zoneData);
        } else {
          console.warn(`Zone ${zoneInfo.zoneId} not found in zones list, using default data`);
          // Create a default zone data structure
          zoneData = {
            id: zoneInfo.zoneId,
            vape_debt: 0,
            vape_restore: 0,
            smoke_debt: 0,
            smoke_restore: 0
          };
        }
      }
    } catch (error) {
      console.error('Error fetching zone data:', error);
      // Create default zone data on error
      zoneData = {
        id: zoneInfo.zoneId,
        vape_debt: 0,
        vape_restore: 0,
        smoke_debt: 0,
        smoke_restore: 0
      };
    }
    
    // Recalculate the actual state based on fresh zone data and current map type
    const actualState = this.calculateState(zoneData, zoneInfo.mapType);
    console.log('Recalculated state:', actualState, 'for map type:', zoneInfo.mapType);
    
    // Get message for the actual state
    const message = this.stateMessages[actualState] || 'Zone information unavailable';
    
    // Get state color for the actual state
    const stateColor = this.stateColors[actualState] || '#B8C4D0';
    
    // Render the inspector with the recalculated state
    this.render(message, stateColor, actualState, zoneData);
    
    // Show the container
    this.container.classList.remove('hidden');
    this.container.style.display = 'block';
    
    // Add event listener for close button
    this.attachEventListeners();
  }
  
  /**
   * Calculate restoration state for a zone (matching heatmap logic)
   * @param {Object} zoneData - Zone data
   * @param {string} mapType - Map type (vape, smoke, or all)
   * @returns {string} State ('needs_restoration', 'healing', or 'recovered')
   */
  calculateState(zoneData, mapType) {
    const RECOVERED_THRESHOLD = 20;
    const HEALING_THRESHOLD = -20;
    
    // Get debt and restore scores based on map type
    let debt, restore;
    
    if (mapType === 'vape') {
      debt = zoneData.vape_debt || zoneData.vapeDebt || 0;
      restore = zoneData.vape_restore || zoneData.vapeRestore || 0;
    } else if (mapType === 'smoke') {
      debt = zoneData.smoke_debt || zoneData.smokeDebt || 0;
      restore = zoneData.smoke_restore || zoneData.smokeRestore || 0;
    } else if (mapType === 'all') {
      // Combined view
      const vapeDebt = zoneData.vape_debt || zoneData.vapeDebt || 0;
      const vapeRestore = zoneData.vape_restore || zoneData.vapeRestore || 0;
      const smokeDebt = zoneData.smoke_debt || zoneData.smokeDebt || 0;
      const smokeRestore = zoneData.smoke_restore || zoneData.smokeRestore || 0;
      
      debt = vapeDebt + smokeDebt;
      restore = vapeRestore + smokeRestore;
    } else {
      // Default to vape
      debt = zoneData.vape_debt || zoneData.vapeDebt || 0;
      restore = zoneData.vape_restore || zoneData.vapeRestore || 0;
    }
    
    // Calculate net score
    const netScore = restore - debt;
    
    // Apply thresholds to determine state
    if (netScore > RECOVERED_THRESHOLD) {
      return 'recovered';
    } else if (netScore > HEALING_THRESHOLD) {
      return 'healing';
    } else {
      return 'needs_restoration';
    }
  }
  
  /**
   * Hide the zone inspector
   */
  hide() {
    if (!this.container) {
      return;
    }
    
    this.container.classList.add('hidden');
    this.container.style.display = 'none';
    this.currentZone = null;
  }
  
  /**
   * Render the zone inspector content
   * @param {string} message - State message to display
   * @param {string} stateColor - Color for the state indicator
   * @param {string} state - Zone restoration state
   * @param {Object|null} zoneData - Full zone data from API
   */
  render(message, stateColor, state, zoneData) {
    if (!this.container) {
      console.error('ZoneInspector: Container not initialized');
      return;
    }
    
    // Simple, clean message for bottom sheet
    this.container.innerHTML = `
      <div class="zone-inspector">
        <div class="zone-state-message">${message}</div>
        <div class="zone-details">
          <p>Zone: ${this.currentZone.zoneId}</p>
        </div>
      </div>
    `;
  }
  
  /**
   * Calculate progress information showing points needed for next states
   * @param {Object} zoneData - Zone data from API
   * @param {string} mapType - Current map type (vape, smoke, or all)
   * @param {string} currentState - Current restoration state
   * @returns {string} HTML string with progress information
   */
  calculateProgressInfo(zoneData, mapType, currentState) {
    console.log('calculateProgressInfo called:', { zoneData, mapType, currentState });
    
    // Thresholds (matching backend constants)
    const RECOVERED_THRESHOLD = 20;
    const HEALING_THRESHOLD = -20;
    
    // Get debt and restore scores based on map type
    let debt, restore;
    
    if (mapType === 'vape') {
      debt = zoneData.vape_debt || zoneData.vapeDebt || 0;
      restore = zoneData.vape_restore || zoneData.vapeRestore || 0;
    } else if (mapType === 'smoke') {
      debt = zoneData.smoke_debt || zoneData.smokeDebt || 0;
      restore = zoneData.smoke_restore || zoneData.smokeRestore || 0;
    } else if (mapType === 'all') {
      // Combined view
      const vapeDebt = zoneData.vape_debt || zoneData.vapeDebt || 0;
      const vapeRestore = zoneData.vape_restore || zoneData.vapeRestore || 0;
      const smokeDebt = zoneData.smoke_debt || zoneData.smokeDebt || 0;
      const smokeRestore = zoneData.smoke_restore || zoneData.smokeRestore || 0;
      
      debt = vapeDebt + smokeDebt;
      restore = vapeRestore + smokeRestore;
    } else {
      // Default to vape
      debt = zoneData.vape_debt || zoneData.vapeDebt || 0;
      restore = zoneData.vape_restore || zoneData.vapeRestore || 0;
    }
    
    console.log('Zone scores:', { debt, restore, mapType });
    
    // Calculate net score
    const netScore = restore - debt;
    
    console.log('Net score:', netScore);
    
    // Calculate points needed for next states
    let progressHTML = '<div class="zone-progress-info">';
    
    if (currentState === 'needs_restoration') {
      // Show points needed to reach healing and recovered
      const pointsToHealing = Math.max(0, HEALING_THRESHOLD - netScore + 1); // +1 to exceed threshold
      const pointsToRecovered = Math.max(0, RECOVERED_THRESHOLD - netScore + 1);
      
      console.log('Points needed:', { pointsToHealing, pointsToRecovered });
      
      progressHTML += `
        <div class="progress-item">
          <span class="progress-icon">🌱</span>
          <span class="progress-text"><strong>${pointsToHealing}</strong> restoration points to reach <strong>Healing</strong></span>
        </div>
        <div class="progress-item">
          <span class="progress-icon">✨</span>
          <span class="progress-text"><strong>${pointsToRecovered}</strong> restoration points to reach <strong>Recovered</strong></span>
        </div>
      `;
    } else if (currentState === 'healing') {
      // Show points needed to reach recovered
      const pointsToRecovered = Math.max(0, RECOVERED_THRESHOLD - netScore + 1);
      
      console.log('Points to recovered:', pointsToRecovered);
      
      progressHTML += `
        <div class="progress-item">
          <span class="progress-icon">✨</span>
          <span class="progress-text"><strong>${pointsToRecovered}</strong> restoration points to reach <strong>Recovered</strong></span>
        </div>
      `;
    } else if (currentState === 'recovered') {
      // Already recovered - show congratulations
      progressHTML += `
        <div class="progress-item recovered">
          <span class="progress-icon">🎉</span>
          <span class="progress-text">This zone has fully recovered! Keep up the great work.</span>
        </div>
      `;
    }
    
    // Show current net score
    progressHTML += `
      <div class="zone-score-info">
        <small>Current net score: <strong>${netScore}</strong> (${restore} restore - ${debt} debt)</small>
      </div>
    `;
    
    progressHTML += '</div>';
    
    return progressHTML;
  }
  
  /**
   * Get human-readable state label
   * @param {string} state - Zone restoration state
   * @returns {string} State label
   */
  getStateLabel(state) {
    const labels = {
      'needs_restoration': 'Needs Restoration',
      'healing': 'Healing',
      'recovered': 'Recovered'
    };
    
    return labels[state] || 'Unknown';
  }
  
  /**
   * Attach event listeners to interactive elements
   */
  attachEventListeners() {
    if (!this.container) {
      return;
    }
    
    // Close button
    const closeButton = this.container.querySelector('[data-action="close"]');
    if (closeButton) {
      closeButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleClose();
      });
    }
    
    // Help zone button
    const helpButton = this.container.querySelector('[data-action="help-zone"]');
    if (helpButton) {
      helpButton.addEventListener('click', async (e) => {
        e.preventDefault();
        const zoneId = helpButton.getAttribute('data-zone-id');
        const mapType = helpButton.getAttribute('data-map-type');
        await this.handleHelpZone(zoneId, mapType);
      });
    }
    
    // Close on background click (optional - clicking outside the inspector)
    const inspector = this.container.querySelector('.zone-inspector');
    if (inspector) {
      this.container.addEventListener('click', (e) => {
        // Only close if clicking the container background, not the inspector itself
        if (e.target === this.container) {
          this.handleClose();
        }
      });
    }
    
    // Close on Escape key
    this.handleEscapeKey = (e) => {
      if (e.key === 'Escape' && !this.container.classList.contains('hidden')) {
        this.handleClose();
      }
    };
    
    document.addEventListener('keydown', this.handleEscapeKey);
  }
  
  /**
   * Handle help zone action
   * @param {string} zoneId - Zone ID to help
   * @param {string} mapType - Current map type (vape or smoke)
   */
  async handleHelpZone(zoneId, mapType) {
    try {
      // Fetch restoration actions for this zone
      const response = await fetch(`http://localhost:5000/api/zones/${zoneId}/actions?type=${mapType}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch zone actions');
      }
      
      const data = await response.json();
      
      // Close the inspector
      this.hide();
      
      // Show restoration action card
      if (window.BreatheBackApp) {
        window.BreatheBackApp.showRestorationActionCard({
          type: mapType,
          context: null,
          location: null,
          timestamp: new Date()
        });
        
        // Initialize restoration action card with zone data
        if (window.restorationActionCard) {
          window.restorationActionCard.destroy();
        }
        
        window.restorationActionCard = new RestorationActionCard({
          containerId: 'restoration-card-container',
          context: null,
          reportType: mapType,
          zoneId: zoneId,
          suggestions: data.suggestions,
          onActionComplete: (result) => {
            console.log('Action completed:', result);
            
            // Update user points in state
            const state = window.BreatheBackApp.getState();
            if (state.userPoints) {
              state.userPoints.totalPoints = result.totalPoints;
              state.userPoints.actionsCompleted = result.actionsCompleted;
              window.BreatheBackApp.saveStateToStorage();
            }
            
            // Update heatmap
            if (window.heatmapView) {
              window.heatmapView.update();
            }
            
            // Update points summary
            if (window.pointsSummary) {
              window.pointsSummary.update();
            }
            
            // Switch to heatmap view to see the change
            window.BreatheBackApp.updateView('heatmap');
          },
          onClose: () => {
            console.log('Restoration card closed');
            window.BreatheBackApp.hideRestorationActionCard();
            window.restorationActionCard = null;
          }
        });
        
        window.restorationActionCard.init();
        
        // Switch to report view to show the action card
        window.BreatheBackApp.updateView('report');
      }
      
    } catch (error) {
      console.error('Error fetching zone actions:', error);
      alert('Failed to load restoration actions. Please try again.');
    }
  }
  
  /**
   * Handle close action
   */
  handleClose() {
    this.hide();
    
    // Call callback
    this.onClose(this.currentZone);
    
    // Remove escape key listener
    if (this.handleEscapeKey) {
      document.removeEventListener('keydown', this.handleEscapeKey);
    }
  }
  
  /**
   * Check if inspector is currently visible
   * @returns {boolean} True if visible
   */
  isVisible() {
    if (!this.container) {
      return false;
    }
    
    return !this.container.classList.contains('hidden') && 
           this.container.style.display !== 'none';
  }
  
  /**
   * Get current zone information
   * @returns {Object|null} Current zone info or null
   */
  getCurrentZone() {
    return this.currentZone;
  }
  
  /**
   * Destroy the zone inspector (cleanup)
   */
  destroy() {
    // Remove escape key listener
    if (this.handleEscapeKey) {
      document.removeEventListener('keydown', this.handleEscapeKey);
    }
    
    // Clear container
    if (this.container) {
      this.container.innerHTML = '';
    }
    
    this.currentZone = null;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ZoneInspector;
}

// Make available globally
if (typeof window !== 'undefined') {
  window.ZoneInspector = ZoneInspector;
}
