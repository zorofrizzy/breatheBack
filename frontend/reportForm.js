/**
 * ReportForm Component
 * Allows users to report air impacts with minimal taps
 * Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1
 */

class ReportForm {
  /**
   * Create a ReportForm instance
   * @param {Object} options - Configuration options
   * @param {string} options.containerId - ID of the container element
   * @param {Function} options.onSubmit - Callback when report is submitted
   * @param {Function} options.onLocationError - Callback when location error occurs
   */
  constructor(options = {}) {
    this.containerId = options.containerId || 'report-form-container';
    this.onSubmit = options.onSubmit || (() => {});
    this.onLocationError = options.onLocationError || (() => {});
    
    // Form state
    this.selectedType = null;      // 'smoke' or 'vape'
    this.selectedContext = null;   // 'indoor' or 'outdoor' (optional)
    this.currentLocation = null;   // User's current location
    this.isSubmitting = false;     // Prevent double submission
    this.locationPermissionGranted = false;
    
    this.container = null;
  }
  
  /**
   * Initialize the report form
   */
  init() {
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      console.error(`ReportForm: Container with id "${this.containerId}" not found`);
      return;
    }
    
    this.render();
    this.attachEventListeners();
    this.requestLocationPermission();
  }
  
  /**
   * Request geolocation permission and get current location
   */
  async requestLocationPermission() {
    if (!navigator.geolocation) {
      this.handleLocationError('Geolocation is not supported by your browser');
      return;
    }
    
    try {
      // Request current position
      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.currentLocation = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          this.locationPermissionGranted = true;
          this.updateSubmitButtonState();
          this.hideLocationError();
        },
        (error) => {
          this.handleLocationError(this.getLocationErrorMessage(error));
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000 // Cache location for 1 minute
        }
      );
    } catch (error) {
      this.handleLocationError('Unable to access your location');
    }
  }
  
  /**
   * Get user-friendly error message for geolocation errors
   * @param {GeolocationPositionError} error - Geolocation error
   * @returns {string} User-friendly error message
   */
  getLocationErrorMessage(error) {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        return 'We need your location to help restore air quality in your area.';
      case error.POSITION_UNAVAILABLE:
        return 'Location information is unavailable. Please try again.';
      case error.TIMEOUT:
        return 'Location request timed out. Please try again.';
      default:
        return 'Unable to determine your location. Please try again.';
    }
  }
  
  /**
   * Handle location errors
   * @param {string} message - Error message to display
   */
  handleLocationError(message) {
    this.locationPermissionGranted = false;
    this.currentLocation = null;
    this.updateSubmitButtonState();
    this.showLocationError(message);
    this.onLocationError(message);
  }
  
  /**
   * Show location error message
   * @param {string} message - Error message
   */
  showLocationError(message) {
    const errorContainer = this.container.querySelector('.location-error');
    if (errorContainer) {
      errorContainer.textContent = message;
      errorContainer.style.display = 'block';
    }
  }
  
  /**
   * Hide location error message
   */
  hideLocationError() {
    const errorContainer = this.container.querySelector('.location-error');
    if (errorContainer) {
      errorContainer.style.display = 'none';
    }
  }
  
  /**
   * Render the report form
   */
  render() {
    if (!this.container) {
      console.error('ReportForm: Container not initialized');
      return;
    }
    
    this.container.innerHTML = `
      <div class="report-form">
        <div class="form-section">
          <h2 class="form-section-title">What did you notice?</h2>
          <p class="form-section-description">Select the type of air impact</p>
          
          <div class="button-group type-buttons">
            <button 
              class="selection-button type-button" 
              data-type="smoke"
              aria-label="Report smoke"
            >
              <span class="button-icon">🚬</span>
              <span class="button-label">Smoke</span>
            </button>
            <button 
              class="selection-button type-button" 
              data-type="vape"
              aria-label="Report vape"
            >
              <span class="button-icon">💨</span>
              <span class="button-label">Vape</span>
            </button>
          </div>
        </div>
        
        <div class="form-section">
          <h2 class="form-section-title">Where are you? (Optional)</h2>
          <p class="form-section-description">This helps us suggest better actions</p>
          
          <div class="button-group context-buttons">
            <button 
              class="selection-button context-button" 
              data-context="indoor"
              aria-label="Indoor context"
            >
              <span class="button-icon">🏠</span>
              <span class="button-label">Indoor</span>
            </button>
            <button 
              class="selection-button context-button" 
              data-context="outdoor"
              aria-label="Outdoor context"
            >
              <span class="button-icon">🌳</span>
              <span class="button-label">Outdoor</span>
            </button>
          </div>
        </div>
        
        <div class="location-error" style="display: none;" role="alert"></div>
        
        <div class="form-actions">
          <button 
            class="submit-button" 
            id="submit-report-button"
            disabled
            aria-label="Submit report"
          >
            <span class="button-text">Submit Report</span>
          </button>
          
          <button 
            class="enable-location-button" 
            id="enable-location-button"
            style="display: none;"
            aria-label="Enable location"
          >
            <span class="button-text">Enable Location</span>
          </button>
        </div>
      </div>
    `;
  }
  
  /**
   * Attach event listeners to form elements
   */
  attachEventListeners() {
    if (!this.container) {
      console.error('ReportForm: Container not initialized');
      return;
    }
    
    // Type button listeners
    const typeButtons = this.container.querySelectorAll('.type-button');
    typeButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const type = button.getAttribute('data-type');
        this.handleTypeSelection(type);
      });
    });
    
    // Context button listeners
    const contextButtons = this.container.querySelectorAll('.context-button');
    contextButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const context = button.getAttribute('data-context');
        this.handleContextSelection(context);
      });
    });
    
    // Submit button listener
    const submitButton = this.container.querySelector('#submit-report-button');
    if (submitButton) {
      submitButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleSubmit();
      });
    }
    
    // Enable location button listener
    const enableLocationButton = this.container.querySelector('#enable-location-button');
    if (enableLocationButton) {
      enableLocationButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.requestLocationPermission();
      });
    }
  }
  
  /**
   * Handle type selection
   * @param {string} type - Selected type ('smoke' or 'vape')
   */
  handleTypeSelection(type) {
    if (type !== 'smoke' && type !== 'vape') {
      console.error(`Invalid type: ${type}`);
      return;
    }
    
    this.selectedType = type;
    
    // Update button states
    const typeButtons = this.container.querySelectorAll('.type-button');
    typeButtons.forEach(button => {
      const buttonType = button.getAttribute('data-type');
      if (buttonType === type) {
        button.classList.add('selected');
        button.setAttribute('aria-pressed', 'true');
      } else {
        button.classList.remove('selected');
        button.setAttribute('aria-pressed', 'false');
      }
    });
    
    // Update submit button state
    this.updateSubmitButtonState();
  }
  
  /**
   * Handle context selection
   * @param {string} context - Selected context ('indoor' or 'outdoor')
   */
  handleContextSelection(context) {
    if (context !== 'indoor' && context !== 'outdoor') {
      console.error(`Invalid context: ${context}`);
      return;
    }
    
    // Toggle context selection (can deselect)
    if (this.selectedContext === context) {
      this.selectedContext = null;
    } else {
      this.selectedContext = context;
    }
    
    // Update button states
    const contextButtons = this.container.querySelectorAll('.context-button');
    contextButtons.forEach(button => {
      const buttonContext = button.getAttribute('data-context');
      if (buttonContext === this.selectedContext) {
        button.classList.add('selected');
        button.setAttribute('aria-pressed', 'true');
      } else {
        button.classList.remove('selected');
        button.setAttribute('aria-pressed', 'false');
      }
    });
  }
  
  /**
   * Update submit button state based on form validity
   */
  updateSubmitButtonState() {
    const submitButton = this.container.querySelector('#submit-report-button');
    const enableLocationButton = this.container.querySelector('#enable-location-button');
    
    if (!submitButton) return;
    
    // Enable submit button only if type is selected AND location is available
    const isValid = this.selectedType !== null && this.locationPermissionGranted && this.currentLocation !== null;
    
    submitButton.disabled = !isValid;
    
    // Show/hide enable location button
    if (enableLocationButton) {
      if (!this.locationPermissionGranted) {
        enableLocationButton.style.display = 'block';
      } else {
        enableLocationButton.style.display = 'none';
      }
    }
  }
  
  /**
   * Handle form submission
   */
  async handleSubmit() {
    // Validate form
    if (!this.selectedType) {
      console.error('Type selection is required');
      return;
    }
    
    if (!this.currentLocation) {
      console.error('Location is required');
      this.handleLocationError('Location is required to submit a report');
      return;
    }
    
    if (this.isSubmitting) {
      console.log('Already submitting...');
      return;
    }
    
    this.isSubmitting = true;
    
    // Update submit button to show loading state
    const submitButton = this.container.querySelector('#submit-report-button');
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.querySelector('.button-text').textContent = 'Submitting...';
    }
    
    try {
      // Create report object
      const report = {
        type: this.selectedType,
        context: this.selectedContext,
        location: this.currentLocation,
        timestamp: new Date().toISOString()
      };
      
      // Call API to submit report
      const response = await fetch('http://localhost:5000/api/reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(report)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to submit report');
      }
      
      const data = await response.json();
      
      // Call onSubmit callback with report and suggestions
      this.onSubmit({
        report,
        zoneId: data.zone_id,
        suggestions: data.suggestions
      });
      
      // Reset form
      this.resetForm();
      
    } catch (error) {
      console.error('Error submitting report:', error);
      alert(`Error submitting report: ${error.message}`);
      
      // Re-enable submit button
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.querySelector('.button-text').textContent = 'Submit Report';
      }
    } finally {
      this.isSubmitting = false;
    }
  }
  
  /**
   * Reset form to initial state
   */
  resetForm() {
    // Clear selections
    this.selectedType = null;
    this.selectedContext = null;
    
    // Update button states
    const typeButtons = this.container.querySelectorAll('.type-button');
    typeButtons.forEach(button => {
      button.classList.remove('selected');
      button.setAttribute('aria-pressed', 'false');
    });
    
    const contextButtons = this.container.querySelectorAll('.context-button');
    contextButtons.forEach(button => {
      button.classList.remove('selected');
      button.setAttribute('aria-pressed', 'false');
    });
    
    // Reset submit button
    const submitButton = this.container.querySelector('#submit-report-button');
    if (submitButton) {
      submitButton.querySelector('.button-text').textContent = 'Submit Report';
      this.updateSubmitButtonState();
    }
  }
  
  /**
   * Get current form state
   * @returns {Object} Current form state
   */
  getState() {
    return {
      selectedType: this.selectedType,
      selectedContext: this.selectedContext,
      currentLocation: this.currentLocation,
      locationPermissionGranted: this.locationPermissionGranted
    };
  }
  
  /**
   * Destroy the report form (cleanup)
   */
  destroy() {
    if (this.container) {
      this.container.innerHTML = '';
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ReportForm;
}

// Make available globally
if (typeof window !== 'undefined') {
  window.ReportForm = ReportForm;
}
