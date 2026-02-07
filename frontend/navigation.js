/**
 * NavigationBar Component
 * Provides persistent navigation between the four main views
 * Requirements: 1.2, 1.3, 1.5
 */

class NavigationBar {
  /**
   * Create a NavigationBar instance
   * @param {Object} options - Configuration options
   * @param {string} options.containerId - ID of the container element
   * @param {string} options.currentView - Initial active view
   * @param {Function} options.onViewChange - Callback when view changes
   */
  constructor(options = {}) {
    this.containerId = options.containerId || 'navigation-bar';
    this.currentView = options.currentView || 'report';
    this.onViewChange = options.onViewChange || (() => {});
    
    // Navigation items configuration
    this.navItems = [
      { id: 'report', icon: '📝', label: 'Report' },
      { id: 'actions', icon: '✨', label: 'Actions' },
      { id: 'heatmap', icon: '🗺️', label: 'Heatmap' },
      { id: 'community', icon: '👥', label: 'Community' },
      { id: 'mypoints', icon: '⭐', label: 'My Points' }
    ];
    
    this.container = null;
  }
  
  /**
   * Initialize the navigation bar
   */
  init() {
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      console.error(`NavigationBar: Container with id "${this.containerId}" not found`);
      return;
    }
    
    this.render();
    this.attachEventListeners();
  }
  
  /**
   * Render the navigation bar
   */
  render() {
    if (!this.container) {
      console.error('NavigationBar: Container not initialized');
      return;
    }
    
    // Clear existing content
    this.container.innerHTML = '';
    
    // Create navigation items
    this.navItems.forEach(item => {
      const navButton = this.createNavItem(item);
      this.container.appendChild(navButton);
    });
    
    // Highlight the current active view
    this.highlightActiveView(this.currentView);
  }
  
  /**
   * Create a navigation item element
   * @param {Object} item - Navigation item configuration
   * @returns {HTMLElement} Navigation button element
   */
  createNavItem(item) {
    const button = document.createElement('button');
    button.className = 'nav-item';
    button.setAttribute('data-view', item.id);
    button.setAttribute('aria-label', `Navigate to ${item.label}`);
    
    // Create icon span
    const iconSpan = document.createElement('span');
    iconSpan.className = 'nav-icon';
    iconSpan.textContent = item.icon;
    iconSpan.setAttribute('aria-hidden', 'true');
    
    // Create label span
    const labelSpan = document.createElement('span');
    labelSpan.className = 'nav-label';
    labelSpan.textContent = item.label;
    
    // Append icon and label to button
    button.appendChild(iconSpan);
    button.appendChild(labelSpan);
    
    return button;
  }
  
  /**
   * Attach event listeners to navigation items
   */
  attachEventListeners() {
    if (!this.container) {
      console.error('NavigationBar: Container not initialized');
      return;
    }
    
    const navButtons = this.container.querySelectorAll('.nav-item');
    
    navButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const view = button.getAttribute('data-view');
        if (view) {
          this.handleViewChange(view);
        }
      });
      
      // Add keyboard support (Enter and Space)
      button.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          const view = button.getAttribute('data-view');
          if (view) {
            this.handleViewChange(view);
          }
        }
      });
    });
  }
  
  /**
   * Handle view change
   * @param {string} view - View identifier ('report', 'actions', 'heatmap', 'community', 'mypoints')
   */
  handleViewChange(view) {
    const validViews = ['report', 'actions', 'heatmap', 'community', 'mypoints'];
    
    if (!validViews.includes(view)) {
      console.error(`NavigationBar: Invalid view "${view}"`);
      return;
    }
    
    // Don't do anything if already on this view
    if (view === this.currentView) {
      return;
    }
    
    // Update current view
    this.currentView = view;
    
    // Highlight the active view
    this.highlightActiveView(view);
    
    // Call the callback
    this.onViewChange(view);
  }
  
  /**
   * Highlight the active view in the navigation
   * @param {string} view - View identifier to highlight
   */
  highlightActiveView(view) {
    if (!this.container) {
      console.error('NavigationBar: Container not initialized');
      return;
    }
    
    const navButtons = this.container.querySelectorAll('.nav-item');
    
    navButtons.forEach(button => {
      const buttonView = button.getAttribute('data-view');
      
      if (buttonView === view) {
        button.classList.add('active');
        button.setAttribute('aria-current', 'page');
      } else {
        button.classList.remove('active');
        button.removeAttribute('aria-current');
      }
    });
  }
  
  /**
   * Update the current view (called externally when view changes)
   * @param {string} view - New current view
   */
  setCurrentView(view) {
    const validViews = ['report', 'actions', 'heatmap', 'community', 'mypoints'];
    
    if (!validViews.includes(view)) {
      console.error(`NavigationBar: Invalid view "${view}"`);
      return;
    }
    
    this.currentView = view;
    this.highlightActiveView(view);
  }
  
  /**
   * Get the current active view
   * @returns {string} Current view identifier
   */
  getCurrentView() {
    return this.currentView;
  }
  
  /**
   * Destroy the navigation bar (cleanup)
   */
  destroy() {
    if (this.container) {
      this.container.innerHTML = '';
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = NavigationBar;
}

// Make available globally
if (typeof window !== 'undefined') {
  window.NavigationBar = NavigationBar;
}
