/**
 * ReportFlow Component
 * Merged Report + Actions into one smooth flow
 * Step 1: Select type + context (chips)
 * Step 2: Log air impact
 * Step 3: Immediately reveal "Restore now" actions
 */

class ReportFlow {
  constructor(options = {}) {
    this.containerId = options.containerId || 'report-flow-container';
    this.onActionComplete = options.onActionComplete || (() => {});
    
    // Flow state
    this.selectedType = null;      // 'vape' or 'smoke'
    this.selectedContext = null;   // 'indoor' or 'outdoor'
    this.currentLocation = null;
    this.currentZoneId = null;
    this.suggestions = [];
    this.step = 1; // 1: select, 2: logged, 3: actions shown
    
    this.container = null;
  }
  
  init() {
    console.log('ReportFlow.init() called');
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      console.error(`ReportFlow: Container "${this.containerId}" not found`);
      return;
    }
    
    console.log('ReportFlow: Container found, rendering...');
    this.render();
    this.requestLocation();
    console.log('ReportFlow: Initialized successfully');
  }
  
  async requestLocation() {
    if (!navigator.geolocation) {
      this.showError('Location not supported');
      return;
    }
    
    try {
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000
        });
      });
      
      this.currentLocation = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      };
      
      // Calculate zone ID
      const ZONE_GRID_SIZE = 0.01;
      const latGrid = Math.floor(this.currentLocation.latitude / ZONE_GRID_SIZE);
      const lngGrid = Math.floor(this.currentLocation.longitude / ZONE_GRID_SIZE);
      this.currentZoneId = `zone_${latGrid}_${lngGrid}`;
      
      this.updateSubmitButton();
    } catch (error) {
      this.showError('Enable location to log air impacts');
    }
  }
  
  render() {
    console.log('ReportFlow.render() called, step:', this.step);
    if (!this.container) return;
    
    if (this.step === 1) {
      this.renderSelectionStep();
    } else if (this.step === 2) {
      this.renderActionsStep();
    }
    console.log('ReportFlow.render() completed');
  }
  
  renderSelectionStep() {
    console.log('ReportFlow.renderSelectionStep() called');
    this.container.innerHTML = `
      <div class="report-flow-card">
        <div class="flow-intro">
          <h1>Help air heal</h1>
          <p>Select what you noticed, then take action</p>
        </div>
        
        <div class="chip-section">
          <label class="chip-label">Type</label>
          <div class="chip-group">
            <button class="chip ${this.selectedType === 'vape' ? 'selected' : ''}" data-type="vape">
              💨 Vape
            </button>
            <button class="chip ${this.selectedType === 'smoke' ? 'selected' : ''}" data-type="smoke">
              🚬 Smoke
            </button>
          </div>
        </div>
        
        <div class="chip-section">
          <label class="chip-label">Where</label>
          <div class="chip-group">
            <button class="chip ${this.selectedContext === 'indoor' ? 'selected' : ''}" data-context="indoor">
              🏠 Indoor
            </button>
            <button class="chip ${this.selectedContext === 'outdoor' ? 'selected' : ''}" data-context="outdoor">
              🌳 Outdoor
            </button>
          </div>
        </div>
        
        <button class="btn-primary btn-log" id="log-impact-btn" disabled>
          Log air impact
        </button>
      </div>
    `;
    
    this.attachSelectionListeners();
  }
  
  renderActionsStep() {
    const actionsHTML = this.suggestions.map(action => `
      <button class="action-card" data-action-id="${action.id}" data-points="${action.points}">
        <div class="action-info">
          <div class="action-title">${this.escapeHtml(action.title)}</div>
          <div class="action-desc">${this.escapeHtml(action.description)}</div>
        </div>
        <div class="action-points">+${action.points}</div>
      </button>
    `).join('');
    
    this.container.innerHTML = `
      <div class="report-flow-card">
        <div class="flow-success">
          <div class="success-icon">✓</div>
          <h2>Logged</h2>
          <p>This space is healing</p>
        </div>
        
        <div class="restore-section">
          <h3>Restore now</h3>
          <div class="actions-list">
            ${actionsHTML}
          </div>
        </div>
        
        <button class="btn-secondary btn-new-report" id="new-report-btn">
          Log another
        </button>
      </div>
    `;
    
    this.attachActionsListeners();
  }
  
  attachSelectionListeners() {
    // Type chips
    this.container.querySelectorAll('[data-type]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.selectedType = btn.getAttribute('data-type');
        this.render();
      });
    });
    
    // Context chips
    this.container.querySelectorAll('[data-context]').forEach(btn => {
      btn.addEventListener('click', () => {
        const context = btn.getAttribute('data-context');
        this.selectedContext = this.selectedContext === context ? null : context;
        this.render();
      });
    });
    
    // Log button
    const logBtn = this.container.querySelector('#log-impact-btn');
    if (logBtn) {
      logBtn.addEventListener('click', () => this.handleLogImpact());
    }
    
    this.updateSubmitButton();
  }
  
  attachActionsListeners() {
    // Action cards
    this.container.querySelectorAll('.action-card').forEach(btn => {
      btn.addEventListener('click', () => {
        const actionId = btn.getAttribute('data-action-id');
        const points = parseInt(btn.getAttribute('data-points'));
        const action = this.suggestions.find(a => a.id === actionId);
        if (action) {
          this.handleActionComplete(action);
        }
      });
    });
    
    // New report button
    const newBtn = this.container.querySelector('#new-report-btn');
    if (newBtn) {
      newBtn.addEventListener('click', () => this.resetFlow());
    }
  }
  
  updateSubmitButton() {
    const logBtn = this.container.querySelector('#log-impact-btn');
    if (!logBtn) return;
    
    const canSubmit = this.selectedType && this.currentLocation;
    logBtn.disabled = !canSubmit;
    
    console.log('Submit button state:', {
      selectedType: this.selectedType,
      hasLocation: !!this.currentLocation,
      canSubmit
    });
  }
  
  async handleLogImpact() {
    if (!this.selectedType || !this.currentLocation) return;
    
    try {
      const response = await fetch('http://localhost:5000/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: this.selectedType,
          context: this.selectedContext,
          location: this.currentLocation,
          timestamp: new Date().toISOString()
        })
      });
      
      if (!response.ok) throw new Error('Failed to submit report');
      
      const data = await response.json();
      this.suggestions = data.suggestions;
      this.step = 2;
      this.render();
      
      // Update points chip
      this.updatePointsChip();
      
    } catch (error) {
      console.error('Error logging impact:', error);
      this.showError('Failed to log impact');
    }
  }
  
  async handleActionComplete(action) {
    try {
      const response = await fetch('http://localhost:5000/api/actions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_id: action.id,
          points: action.points,
          type: this.selectedType,
          zone_id: this.currentZoneId
        })
      });
      
      if (!response.ok) throw new Error('Failed to complete action');
      
      const result = await response.json();
      
      // Show brief success
      this.showSuccess(`+${action.points} points`);
      
      // Update points chip
      this.updatePointsChip();
      
      // Update map if visible
      if (window.heatmapView) {
        window.heatmapView.update();
      }
      
      // Call callback
      this.onActionComplete(result);
      
      // Reset after short delay
      setTimeout(() => this.resetFlow(), 1500);
      
    } catch (error) {
      console.error('Error completing action:', error);
      this.showError('Failed to complete action');
    }
  }
  
  resetFlow() {
    this.selectedType = null;
    this.selectedContext = null;
    this.suggestions = [];
    this.step = 1;
    this.render();
  }
  
  async updatePointsChip() {
    try {
      const response = await fetch('http://localhost:5000/api/points');
      if (response.ok) {
        const data = await response.json();
        const chipValue = document.getElementById('points-chip-value');
        if (chipValue) {
          chipValue.textContent = data.total_points || 0;
        }
        
        // Update app state
        if (window.BreatheBackApp) {
          window.BreatheBackApp.updatePoints(data);
        }
      }
    } catch (error) {
      console.error('Error updating points chip:', error);
    }
  }
  
  showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-success';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  }
  
  showError(message) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-error';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
  
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  update() {
    this.render();
  }
  
  destroy() {
    if (this.container) {
      this.container.innerHTML = '';
    }
  }
}

// Make available globally
if (typeof window !== 'undefined') {
  window.ReportFlow = ReportFlow;
}
