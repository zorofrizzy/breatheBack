/**
 * ThemeManager
 * Handles switching between light and dark themes
 */

class ThemeManager {
  constructor() {
    this.currentTheme = 'dark'; // default
    this.lightStylesheet = 'styles-new.css';
    this.darkStylesheet = 'styles.css';
  }
  
  init() {
    // Load saved theme preference
    const savedTheme = localStorage.getItem('breatheback_theme') || 'dark';
    this.setTheme(savedTheme, false);
    
    // Set up toggle button
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => this.toggle());
    }
  }
  
  toggle() {
    const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    this.setTheme(newTheme, true);
  }
  
  setTheme(theme, save = true) {
    this.currentTheme = theme;
    
    // Update stylesheet
    const linkElement = document.querySelector('link[rel="stylesheet"][href*="styles"]');
    if (linkElement) {
      linkElement.href = theme === 'light' ? this.lightStylesheet : this.darkStylesheet;
    }
    
    // Update toggle button icon
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
      const icon = toggleBtn.querySelector('.theme-icon');
      if (icon) {
        icon.textContent = theme === 'light' ? '🌙' : '☀️';
      }
    }
    
    // Save preference
    if (save) {
      localStorage.setItem('breatheback_theme', theme);
    }
    
    // Refresh map view if it exists and is active
    // This ensures the user location marker is preserved during theme switches
    setTimeout(() => {
      if (window.heatmapView && window.heatmapView.map) {
        console.log('Refreshing map after theme change...');
        
        // Force map to invalidate size (handles CSS changes)
        window.heatmapView.map.invalidateSize();
        
        // Restore user location marker using stored coordinates
        window.heatmapView.restoreUserLocationMarker();
      }
    }, 150); // Increased timeout to ensure CSS is fully loaded
    
    console.log('Theme set to:', theme);
  }
  
  getCurrentTheme() {
    return this.currentTheme;
  }
}

// Make available globally
if (typeof window !== 'undefined') {
  window.ThemeManager = ThemeManager;
}
