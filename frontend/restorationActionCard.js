/**
 * RestorationActionCard Component
 * Displays context-aware restoration actions after a report
 * Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.6
 */

class RestorationActionCard {
  /**
   * Create a RestorationActionCard instance
   * @param {Object} options - Configuration options
   * @param {string} options.containerId - ID of the container element
   * @param {string} options.context - Context of the report ('indoor' or 'outdoor')
   * @param {string} options.reportType - Type of report ('smoke' or 'vape')
   * @param {string} options.zoneId - Zone ID where the report was submitted
   * @param {Array} options.suggestions - Array of action suggestions from API
   * @param {Function} options.onActionComplete - Callback when action is completed
   * @param {Function} options.onClose - Callback when card is closed
   */
  constructor(options = {}) {
    this.containerId = options.containerId || 'restoration-card-container';
    this.context = options.context || null;
    this.reportType = options.reportType || 'vape';
    this.zoneId = options.zoneId || null;
    this.suggestions = options.suggestions || [];
    this.onActionComplete = options.onActionComplete || (() => {});
    this.onClose = options.onClose || (() => {});
    
    this.container = null;
    this.isProcessing = false;
  }
  
  /**
   * Initialize the restoration action card
   */
  init() {
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      console.error(`RestorationActionCard: Container with id "${this.containerId}" not found`);
      return;
    }
    
    this.render();
    this.attachEventListeners();
  }
  
  /**
   * Render the restoration action card
   * Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
   */
  render() {
    if (!this.container) {
      console.error('RestorationActionCard: Container not initialized');
      return;
    }
    
    // Validate that we have 3-5 actions (Property 9: Action count range)
    if (this.suggestions.length < 3 || this.suggestions.length > 5) {
      console.warn(`RestorationActionCard: Expected 3-5 actions, got ${this.suggestions.length}`);
    }
    
    this.container.innerHTML = `
      <div class="restoration-card">
        <div class="restoration-card-header">
          <h2 class="restoration-card-title">Help Restore the Air</h2>
          <p class="restoration-card-subtitle">Choose an action to complete</p>
          <button class="card-close-button" aria-label="Close card">×</button>
        </div>
        
        <div class="action-list">
          ${this.suggestions.map(action => `
            <button 
              class="action-item" 
              data-action-id="${action.id}"
              data-action-points="${action.points}"
              aria-label="Complete action: ${action.title}"
            >
              <div class="action-content">
                <div class="action-title">${this.escapeHtml(action.title)}</div>
                <div class="action-description">${this.escapeHtml(action.description)}</div>
              </div>
              <div class="action-points">+${action.points}</div>
            </button>
          `).join('')}
        </div>
        
        <div class="card-footer">
          <p class="card-footer-text">Every action helps the community heal</p>
        </div>
      </div>
    `;
  }
  
  /**
   * Attach event listeners to card elements
   */
  attachEventListeners() {
    if (!this.container) {
      console.error('RestorationActionCard: Container not initialized');
      return;
    }
    
    // Action item click listeners
    const actionItems = this.container.querySelectorAll('.action-item');
    actionItems.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const actionId = button.getAttribute('data-action-id');
        const actionPoints = parseInt(button.getAttribute('data-action-points'), 10);
        const action = this.suggestions.find(a => a.id === actionId);
        
        if (action) {
          this.handleActionComplete(action);
        }
      });
    });
    
    // Close button listener
    const closeButton = this.container.querySelector('.card-close-button');
    if (closeButton) {
      closeButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.close();
      });
    }
  }
  
  /**
   * Handle action completion
   * @param {Object} action - The action to complete
   * Requirements: 5.1, 5.6
   */
  async handleActionComplete(action) {
    if (this.isProcessing) {
      console.log('Already processing an action...');
      return;
    }
    
    if (!this.zoneId) {
      console.error('RestorationActionCard: No zone ID provided');
      return;
    }
    
    this.isProcessing = true;
    
    try {
      // Call API to complete action
      const response = await fetch('http://localhost:5000/api/actions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action_id: action.id,
          points: action.points,
          type: this.reportType,
          zone_id: this.zoneId
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to complete action');
      }
      
      const data = await response.json();
      
      // Display positive feedback (Requirement 5.6)
      this.showFeedback(action, data);
      
      // Call onActionComplete callback
      this.onActionComplete({
        action,
        totalPoints: data.total_points,
        actionsCompleted: data.actions_completed,
        feedback: data.feedback
      });
      
    } catch (error) {
      console.error('Error completing action:', error);
      this.showError(`Error completing action: ${error.message}`);
      this.isProcessing = false;
    }
  }
  
  /**
   * Show positive feedback after action completion
   * @param {Object} action - The completed action
   * @param {Object} data - Response data from API
   * Requirements: 5.6
   */
  showFeedback(action, data) {
    if (!this.container) return;
    
    this.container.innerHTML = `
      <div class="restoration-card feedback-card">
        <div class="feedback-content">
          <div class="feedback-icon">✓</div>
          <div class="feedback-message">${this.escapeHtml(data.feedback)}</div>
          
          <div class="feedback-points">
            <div class="points-earned">+${action.points} points earned!</div>
            <div class="points-total">Total today: ${data.total_points} points</div>
          </div>
          
          <div class="feedback-actions-count">
            ${data.actions_completed} ${data.actions_completed === 1 ? 'action' : 'actions'} completed today
          </div>
        </div>
      </div>
    `;
    
    // Auto-close after 3 seconds
    setTimeout(() => {
      this.close();
    }, 3000);
  }
  
  /**
   * Show error message
   * @param {string} message - Error message to display
   */
  showError(message) {
    if (!this.container) return;
    
    const errorContainer = document.createElement('div');
    errorContainer.className = 'card-error-message';
    errorContainer.textContent = message;
    errorContainer.setAttribute('role', 'alert');
    
    const cardHeader = this.container.querySelector('.restoration-card-header');
    if (cardHeader) {
      cardHeader.after(errorContainer);
      
      // Remove error after 5 seconds
      setTimeout(() => {
        errorContainer.remove();
      }, 5000);
    }
  }
  
  /**
   * Close the restoration action card
   */
  close() {
    if (this.container) {
      this.container.innerHTML = '';
    }
    
    this.onClose();
  }
  
  /**
   * Update the card with new suggestions
   * @param {Object} options - New options
   */
  update(options = {}) {
    if (options.context !== undefined) {
      this.context = options.context;
    }
    if (options.reportType !== undefined) {
      this.reportType = options.reportType;
    }
    if (options.zoneId !== undefined) {
      this.zoneId = options.zoneId;
    }
    if (options.suggestions !== undefined) {
      this.suggestions = options.suggestions;
    }
    
    this.render();
    this.attachEventListeners();
  }
  
  /**
   * Escape HTML to prevent XSS
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  /**
   * Destroy the restoration action card (cleanup)
   */
  destroy() {
    if (this.container) {
      this.container.innerHTML = '';
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = RestorationActionCard;
}

// Make available globally
if (typeof window !== 'undefined') {
  window.RestorationActionCard = RestorationActionCard;
}
