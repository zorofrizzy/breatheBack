/**
 * PointsSummary Component
 * Displays user's daily contribution and points
 * Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
 */

class PointsSummary {
  /**
   * Initialize the PointsSummary component
   * @param {Object} config - Configuration object
   * @param {string} config.containerId - ID of the container element
   */
  constructor(config) {
    this.containerId = config.containerId;
    this.container = null;
  }

  /**
   * Initialize the component
   */
  init() {
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      console.error(`Container element with ID "${this.containerId}" not found`);
      return;
    }

    // Render the component
    this.render();
  }

  /**
   * Check if we need to reset daily points (midnight passed)
   * Requirement: 8.3 - Daily points reset at midnight
   */
  checkDailyReset() {
    const app = window.BreatheBackApp;
    if (!app) return;

    const state = app.getState();
    if (!state.userPoints) return;

    const today = new Date().toISOString().split('T')[0];
    const storedDate = state.userPoints.date;

    if (storedDate !== today) {
      // New day - reset points
      console.log('New day detected in PointsSummary, resetting daily points');
      
      const resetPoints = {
        date: today,
        totalPoints: 0,
        actionsCompleted: 0,
        vapePoints: 0,
        smokePoints: 0,
        actions: []
      };

      app.updatePoints(resetPoints);
    }
  }

  /**
   * Generate feel-good summary message based on points
   * Requirement: 8.5 - Display positive summary message
   * @param {number} totalPoints - Total points earned today
   * @param {number} actionsCompleted - Number of actions completed
   * @returns {string} Summary message
   */
  getSummaryMessage(totalPoints, actionsCompleted) {
    if (totalPoints === 0) {
      return "Ready to help the air heal today?";
    } else if (totalPoints >= 1 && totalPoints <= 20) {
      return "Small actions add up—nice work.";
    } else if (totalPoints >= 21 && totalPoints <= 50) {
      // Calculate approximate number of spaces helped (rough estimate)
      const spacesHelped = Math.max(1, Math.floor(actionsCompleted / 2));
      return `You helped ${spacesHelped} ${spacesHelped === 1 ? 'space' : 'spaces'} start healing today.`;
    } else {
      // 51+ points
      return "Amazing effort! The community feels your impact.";
    }
  }

  /**
   * Render the PointsSummary component
   * Requirements: 8.1, 8.2, 8.4, 8.5
   */
  render() {
    if (!this.container) return;

    // Get current user points from app state
    const app = window.BreatheBackApp;
    const state = app ? app.getState() : null;
    const userPoints = state ? state.userPoints : null;

    console.log('PointsSummary render - userPoints:', userPoints);

    // Default values if no points data
    // Handle both camelCase and snake_case from API
    const totalPoints = userPoints ? (userPoints.totalPoints || userPoints.total_points || 0) : 0;
    const actionsCompleted = userPoints ? (userPoints.actionsCompleted || userPoints.actions_completed || 0) : 0;
    const vapePoints = userPoints ? (userPoints.vapePoints || userPoints.vape_points || 0) : 0;
    const smokePoints = userPoints ? (userPoints.smokePoints || userPoints.smoke_points || 0) : 0;

    console.log('PointsSummary render - parsed values:', { totalPoints, actionsCompleted, vapePoints, smokePoints });
    console.log('PointsSummary render - raw userPoints object:', JSON.stringify(userPoints, null, 2));

    // Generate summary message
    const summaryMessage = this.getSummaryMessage(totalPoints, actionsCompleted);

    // Build HTML
    const html = `
      <div class="points-summary">
        <div class="points-header">
          <h2>My Points</h2>
          <p class="points-date">Today</p>
        </div>

        <div class="points-main">
          <div class="points-total">
            <div class="points-number">${totalPoints}</div>
            <div class="points-label">Clean Air Points</div>
          </div>

          <div class="actions-count">
            <div class="actions-number">${actionsCompleted}</div>
            <div class="actions-label">${actionsCompleted === 1 ? 'Action' : 'Actions'} Completed</div>
          </div>
        </div>

        ${this.renderBreakdown(vapePoints, smokePoints, totalPoints)}

        <div class="points-summary-message">
          <p>${summaryMessage}</p>
        </div>
      </div>
    `;

    this.container.innerHTML = html;
  }

  /**
   * Render optional breakdown of vape vs smoke points
   * Requirement: 8.4 - Optional breakdown display
   * @param {number} vapePoints - Points from vape restoration
   * @param {number} smokePoints - Points from smoke restoration
   * @param {number} totalPoints - Total points
   * @returns {string} HTML for breakdown section
   */
  renderBreakdown(vapePoints, smokePoints, totalPoints) {
    // Only show breakdown if user has earned points
    if (totalPoints === 0) {
      return '';
    }

    return `
      <div class="points-breakdown">
        <h3>Breakdown</h3>
        <div class="breakdown-items">
          <div class="breakdown-item">
            <span class="breakdown-label">Vape Restoration</span>
            <span class="breakdown-value">${vapePoints} pts</span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">Smoke Restoration</span>
            <span class="breakdown-value">${smokePoints} pts</span>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Update the display with current points data
   * Call this method when points change
   */
  update() {
    this.render();
  }

  /**
   * Destroy the component and clean up
   */
  destroy() {
    if (this.container) {
      this.container.innerHTML = '';
    }
  }
}

// Make PointsSummary available globally
window.PointsSummary = PointsSummary;
