/**
 * EventList Component
 * Displays upcoming community restoration events
 * Requirements: 9.4, 9.5
 */

class EventList {
  /**
   * Initialize the EventList component
   * @param {Object} config - Configuration object
   * @param {string} config.containerId - ID of the container element
   * @param {Function} config.onEventTap - Callback when an event is tapped
   */
  constructor(config) {
    this.containerId = config.containerId;
    this.onEventTap = config.onEventTap || (() => {});
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
   * Get events from app state, sorted by date/time
   * Requirement: 9.4 - Sort events by date/time
   * @returns {Array} Sorted array of events
   */
  getSortedEvents() {
    const app = window.BreatheBackApp;
    const state = app ? app.getState() : null;
    const events = state ? state.events : [];

    // Sort events by date_time (ascending - earliest first)
    return [...events].sort((a, b) => {
      const dateA = new Date(a.date_time);
      const dateB = new Date(b.date_time);
      return dateA - dateB;
    });
  }

  /**
   * Format date and time for display
   * @param {string} dateTimeString - ISO datetime string
   * @returns {string} Formatted date and time
   */
  formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    
    // Format: "Mon, Jan 15, 2026 at 2:30 PM"
    const options = {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    };
    
    return date.toLocaleString('en-US', options);
  }

  /**
   * Format duration for display
   * @param {number} minutes - Duration in minutes
   * @returns {string} Formatted duration
   */
  formatDuration(minutes) {
    if (minutes < 60) {
      return `${minutes} min`;
    } else {
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      if (remainingMinutes === 0) {
        return `${hours} ${hours === 1 ? 'hour' : 'hours'}`;
      } else {
        return `${hours}h ${remainingMinutes}m`;
      }
    }
  }

  /**
   * Get display label for type focus
   * @param {string} typeFocus - 'vape', 'smoke', or 'both'
   * @returns {string} Display label
   */
  getTypeFocusLabel(typeFocus) {
    const labels = {
      'vape': 'Vape Focus',
      'smoke': 'Smoke Focus',
      'both': 'Vape & Smoke'
    };
    return labels[typeFocus] || typeFocus;
  }

  /**
   * Get icon for type focus
   * @param {string} typeFocus - 'vape', 'smoke', or 'both'
   * @returns {string} Icon emoji or symbol
   */
  getTypeFocusIcon(typeFocus) {
    const icons = {
      'vape': '💨',
      'smoke': '🚭',
      'both': '🌬️'
    };
    return icons[typeFocus] || '🌬️';
  }

  /**
   * Render a single event item
   * Requirement: 9.5 - Display title, date/time, location, type focus
   * @param {Object} event - Event object
   * @returns {string} HTML for event item
   */
  renderEventItem(event) {
    const formattedDateTime = this.formatDateTime(event.date_time);
    const formattedDuration = this.formatDuration(event.duration);
    const typeFocusLabel = this.getTypeFocusLabel(event.type_focus);
    const typeFocusIcon = this.getTypeFocusIcon(event.type_focus);

    return `
      <div class="event-item" data-event-id="${event.id}">
        <div class="event-header">
          <h3 class="event-title">${this.escapeHtml(event.name)}</h3>
          <span class="event-type-badge">
            <span class="event-type-icon">${typeFocusIcon}</span>
            ${typeFocusLabel}
          </span>
        </div>
        
        <div class="event-details">
          <div class="event-detail-item">
            <span class="event-detail-icon">📅</span>
            <span class="event-detail-text">${formattedDateTime}</span>
          </div>
          
          <div class="event-detail-item">
            <span class="event-detail-icon">⏱️</span>
            <span class="event-detail-text">${formattedDuration}</span>
          </div>
          
          <div class="event-detail-item">
            <span class="event-detail-icon">📍</span>
            <span class="event-detail-text">${this.escapeHtml(event.location)}</span>
          </div>
        </div>

        ${event.context_hint ? `
          <div class="event-context-hint">
            <span class="context-hint-label">${event.context_hint === 'indoor' ? '🏠 Indoor' : '🌳 Outdoor'}</span>
          </div>
        ` : ''}

        <div class="event-description">
          <p>${this.escapeHtml(event.description)}</p>
        </div>
      </div>
    `;
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
   * Render the EventList component
   * Requirements: 9.4, 9.5
   */
  render() {
    if (!this.container) return;

    const events = this.getSortedEvents();

    // Build HTML
    let html = `
      <div class="event-list">
        <div class="event-list-header">
          <h2>Community Events</h2>
          <p class="event-list-subtitle">Join us in healing the air together</p>
        </div>
    `;

    if (events.length === 0) {
      html += `
        <div class="event-list-empty">
          <p>No upcoming events yet.</p>
          <p class="event-list-empty-hint">Create an event to bring the community together!</p>
        </div>
      `;
    } else {
      html += `<div class="event-list-items">`;
      events.forEach(event => {
        html += this.renderEventItem(event);
      });
      html += `</div>`;
    }

    html += `</div>`;

    this.container.innerHTML = html;

    // Attach event listeners
    this.attachEventListeners();
  }

  /**
   * Attach event listeners to event items
   * Requirement: 9.5 - Implement handleEventTap
   */
  attachEventListeners() {
    if (!this.container) return;

    const eventItems = this.container.querySelectorAll('.event-item');
    eventItems.forEach(item => {
      item.addEventListener('click', () => {
        const eventId = item.getAttribute('data-event-id');
        this.handleEventTap(eventId);
      });
    });
  }

  /**
   * Handle event tap
   * Requirement: 9.5 - Show event details
   * @param {string} eventId - Event ID
   */
  handleEventTap(eventId) {
    console.log('Event tapped:', eventId);

    // Get event data
    const app = window.BreatheBackApp;
    const state = app ? app.getState() : null;
    const events = state ? state.events : [];
    const event = events.find(e => e.id === eventId);

    if (event) {
      // Call the callback with event data
      this.onEventTap(event);
    }
  }

  /**
   * Update the display with current events data
   * Call this method when events change
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

// Make EventList available globally
window.EventList = EventList;
