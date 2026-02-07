/**
 * ActionsView Component
 * Allows users to proactively take restoration actions for their current zone
 * without needing to submit a report first
 */

class ActionsView {
  /**
   * Create an ActionsView instance
   * @param {Object} options - Configuration options
   * @param {string} options.containerId - ID of the container element
   */
  constructor(options = {}) {
    this.containerId = options.containerId || 'actions-container';
    this.container = null;
    this.currentLocation = null;
    this.currentZoneId = null;
    this.suggestions = [];
  }
  
  /**
   * Initialize the actions view
   */
  init() {
    this.container = document.getElementById(this.containerId);
    
    if (!this.container) {
      console.error(`ActionsView: Container with id "${this.containerId}" not found`);
      return;
    }
    
    this.render();
  }
  
  /**
   * Render the actions view
   */
  render() {
    if (!this.container) {
      console.error('ActionsView: Container not initialized');
      return;
    }
    
    this.container.innerHTML = `
      <div class="actions-view">
        <div class="actions-intro">
          <p>Take proactive steps to improve air quality in your area. Choose an action type below to see suggestions.</p>
        </div>
        
        <div class="action-type-selector">
          <h3>What would you like to help with?</h3>
          <div class="type-buttons">
            <button class="type-btn" data-type="vape">
              <span class="type-icon">💨</span>
              <span class="type-label">Vape Restoration</span>
            </button>
            <button class="type-btn" data-type="smoke">
              <span class="type-icon">🚭</span>
              <span class="type-label">Smoke Restoration</span>
            </button>
            <button class="type-btn" data-type="both">
              <span class="type-icon">🌬️</span>
              <span class="type-label">Both</span>
            </button>
          </div>
        </div>
        
        <div class="context-selector" style="display: none;">
          <h3>Where are you?</h3>
          <div class="context-buttons">
            <button class="context-btn" data-context="indoor">
              <span class="context-icon">🏠</span>
              <span class="context-label">Indoor</span>
            </button>
            <button class="context-btn" data-context="outdoor">
              <span class="context-icon">🌳</span>
              <span class="context-label">Outdoor</span>
            </button>
            <button class="context-btn" data-context="any">
              <span class="context-icon">📍</span>
              <span class="context-label">Any</span>
            </button>
          </div>
        </div>
        
        <div id="actions-list-container"></div>
      </div>
    `;
    
    this.attachEventListeners();
  }
  
  /**
   * Attach event listeners
   */
  attachEventListeners() {
    // Type selection buttons
    const typeButtons = this.container.querySelectorAll('.type-btn');
    typeButtons.forEach(button => {
      button.addEventListener('click', () => {
        const type = button.getAttribute('data-type');
        this.handleTypeSelection(type);
      });
    });
    
    // Context selection buttons
    const contextButtons = this.container.querySelectorAll('.context-btn');
    contextButtons.forEach(button => {
      button.addEventListener('click', () => {
        const context = button.getAttribute('data-context');
        this.handleContextSelection(context);
      });
    });
  }
  
  /**
   * Handle type selection
   * @param {string} type - Selected type ('vape', 'smoke', or 'both')
   */
  handleTypeSelection(type) {
    console.log('Type selected:', type);
    
    // Highlight selected button
    const typeButtons = this.container.querySelectorAll('.type-btn');
    typeButtons.forEach(btn => {
      if (btn.getAttribute('data-type') === type) {
        btn.classList.add('selected');
      } else {
        btn.classList.remove('selected');
      }
    });
    
    // Show context selector
    const contextSelector = this.container.querySelector('.context-selector');
    if (contextSelector) {
      contextSelector.style.display = 'block';
    }
    
    // Store selected type
    this.selectedType = type;
  }
  
  /**
   * Handle context selection
   * @param {string} context - Selected context ('indoor', 'outdoor', or 'any')
   */
  async handleContextSelection(context) {
    console.log('Context selected:', context);
    
    // Highlight selected button
    const contextButtons = this.container.querySelectorAll('.context-btn');
    contextButtons.forEach(btn => {
      if (btn.getAttribute('data-context') === context) {
        btn.classList.add('selected');
      } else {
        btn.classList.remove('selected');
      }
    });
    
    // Get user location
    await this.getUserLocation();
    
    // Load actions
    await this.loadActions(context === 'any' ? null : context);
  }
  
  /**
   * Get user's current location
   */
  async getUserLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        console.error('Geolocation not supported');
        reject(new Error('Geolocation not supported'));
        return;
      }
      
      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.currentLocation = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          
          // Calculate zone ID
          const ZONE_GRID_SIZE = 0.01;
          const latGrid = Math.floor(this.currentLocation.latitude / ZONE_GRID_SIZE);
          const lngGrid = Math.floor(this.currentLocation.longitude / ZONE_GRID_SIZE);
          this.currentZoneId = `zone_${latGrid}_${lngGrid}`;
          
          console.log('User location:', this.currentLocation);
          console.log('Current zone:', this.currentZoneId);
          
          resolve(this.currentLocation);
        },
        (error) => {
          console.error('Error getting location:', error);
          reject(error);
        }
      );
    });
  }
  
  /**
   * Load restoration actions
   * @param {string|null} context - Context ('indoor', 'outdoor', or null for any)
   */
  async loadActions(context) {
    try {
      // Store the selected context for later use
      this.selectedContext = context;
      
      // Determine which type(s) to fetch
      const types = this.selectedType === 'both' ? ['vape', 'smoke'] : [this.selectedType];
      
      // Fetch actions for each type
      const allSuggestions = [];
      
      for (const type of types) {
        const url = `http://localhost:5000/api/zones/${this.currentZoneId}/actions?type=${type}${context ? `&context=${context}` : ''}`;
        const response = await fetch(url);
        
        if (response.ok) {
          const data = await response.json();
          // When "both" is selected, mark actions as "both" type instead of individual types
          const actionType = this.selectedType === 'both' ? 'both' : type;
          allSuggestions.push(...data.suggestions.map(s => ({ ...s, actionType: actionType })));
        }
      }
      
      this.suggestions = allSuggestions;
      this.renderActions();
      
    } catch (error) {
      console.error('Error loading actions:', error);
      this.showError('Failed to load actions. Please try again.');
    }
  }
  
  /**
   * Render the actions list
   */
  renderActions() {
    const listContainer = this.container.querySelector('#actions-list-container');
    
    if (!listContainer) {
      return;
    }
    
    if (this.suggestions.length === 0) {
      listContainer.innerHTML = '<p class="no-actions">No actions available at this time.</p>';
      return;
    }
    
    listContainer.innerHTML = `
      <div class="actions-list">
        <h3>Available Actions</h3>
        <p class="zone-info">Helping zone: <strong>${this.currentZoneId}</strong></p>
        ${this.suggestions.map(action => {
          const typeLabel = action.actionType === 'both' ? 'BOTH (Vape + Smoke)' : action.actionType.toUpperCase();
          const buttonLabel = action.actionType === 'both' ? 'Complete Both Action' : `Complete ${action.actionType.charAt(0).toUpperCase() + action.actionType.slice(1)} Action`;
          
          return `
            <div class="action-card">
              <div class="action-header">
                <h4>${action.title}</h4>
                <span class="action-points">+${action.points} pts</span>
              </div>
              <p class="action-description">${action.description}</p>
              <div class="action-footer">
                <span class="action-type-badge ${action.actionType}">${typeLabel}</span>
                <button class="btn-primary complete-action-btn" data-action-id="${action.id}" data-points="${action.points}" data-type="${action.actionType}">
                  ${buttonLabel}
                </button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
    
    // Attach event listeners to complete buttons
    const completeButtons = listContainer.querySelectorAll('.complete-action-btn');
    completeButtons.forEach(button => {
      button.addEventListener('click', () => {
        const actionId = button.getAttribute('data-action-id');
        const points = parseInt(button.getAttribute('data-points'));
        const type = button.getAttribute('data-type');
        this.completeAction(actionId, points, type);
      });
    });
  }
  
  /**
   * Complete a restoration action
   * @param {string} actionId - Action ID
   * @param {number} points - Points to award
   * @param {string} type - Action type ('vape' or 'smoke')
   */
  async completeAction(actionId, points, type) {
    try {
      console.log(`Completing action: actionId=${actionId}, points=${points}, type=${type}, zone=${this.currentZoneId}`);
      
      const response = await fetch('http://localhost:5000/api/actions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_id: actionId,
          points: points,
          type: type,
          zone_id: this.currentZoneId
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Action completion failed:', errorData);
        throw new Error(errorData.error || 'Failed to complete action');
      }
      
      const result = await response.json();
      console.log('Action completed successfully:', result);
      
      // Show success message
      this.showSuccess(result.feedback || 'Great work! Action completed.');
      
      // Update app state
      if (window.BreatheBackApp) {
        // Refresh points from API
        const pointsResponse = await fetch('http://localhost:5000/api/points');
        if (pointsResponse.ok) {
          const pointsData = await pointsResponse.json();
          console.log('Points data from API:', pointsData);
          window.BreatheBackApp.updatePoints(pointsData);
        }
        
        // Refresh heatmap if it exists
        if (window.heatmapView) {
          console.log('Updating heatmap view...');
          window.heatmapView.update();
        }
        
        // Refresh points summary if it exists
        if (window.pointsSummary) {
          window.pointsSummary.update();
        }
      }
      
      // Reload actions to show updated state
      setTimeout(() => {
        this.loadActions(this.selectedContext);
      }, 1500);
      
    } catch (error) {
      console.error('Error completing action:', error);
      this.showError('Failed to complete action. Please try again.');
    }
  }
  
  /**
   * Show success message
   * @param {string} message - Success message
   */
  showSuccess(message) {
    const successEl = document.createElement('div');
    successEl.className = 'action-success-message';
    successEl.textContent = message;
    this.container.prepend(successEl);
    
    setTimeout(() => {
      successEl.remove();
    }, 3000);
  }
  
  /**
   * Show error message
   * @param {string} message - Error message
   */
  showError(message) {
    const errorEl = document.createElement('div');
    errorEl.className = 'action-error-message';
    errorEl.textContent = message;
    this.container.prepend(errorEl);
    
    setTimeout(() => {
      errorEl.remove();
    }, 3000);
  }
  
  /**
   * Update the actions view
   */
  update() {
    // Reload current actions if any are loaded
    if (this.suggestions.length > 0 && this.selectedContext) {
      this.loadActions(this.selectedContext);
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ActionsView;
}

// Make available globally
if (typeof window !== 'undefined') {
  window.ActionsView = ActionsView;
}
