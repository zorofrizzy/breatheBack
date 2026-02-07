/**
 * EventForm Component
 * Allows users to create community restoration events
 * Requirements: 9.1, 9.2, 9.3, 9.6
 */

class EventForm {
  /**
   * Initialize the EventForm component
   * @param {Object} config - Configuration object
   * @param {string} config.containerId - ID of the container element
   * @param {Function} config.onSubmit - Callback when form is submitted successfully
   * @param {Function} config.onCancel - Callback when form is cancelled
   */
  constructor(config) {
    this.containerId = config.containerId;
    this.onSubmit = config.onSubmit || (() => {});
    this.onCancel = config.onCancel || (() => {});
    this.container = null;
    this.isSubmitting = false;
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
   * Get default description template
   * Requirement: 9.2, 9.6 - Auto-populate description with supportive template
   * @returns {string} Default description
   */
  getDefaultDescription() {
    return "We're meeting to help this area heal. No blame, just better air choices together.";
  }

  /**
   * Get minimum datetime for event (current time)
   * @returns {string} ISO datetime string for min attribute
   */
  getMinDateTime() {
    const now = new Date();
    // Format: YYYY-MM-DDTHH:MM
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  /**
   * Render the EventForm component
   * Requirement: 9.1 - Form fields (name, location, date/time, duration, type focus, context hint)
   */
  render() {
    if (!this.container) return;

    const minDateTime = this.getMinDateTime();
    const defaultDescription = this.getDefaultDescription();

    const html = `
      <div class="event-form">
        <div class="event-form-header">
          <h2>Create Community Event</h2>
          <p class="event-form-subtitle">Bring the community together for air restoration</p>
        </div>

        <form id="event-form-element" class="event-form-fields">
          <!-- Event Name -->
          <div class="form-group">
            <label for="event-name" class="form-label">Event Name *</label>
            <input 
              type="text" 
              id="event-name" 
              name="name" 
              class="form-input" 
              placeholder="e.g., Community Air Healing Meetup"
              required
              maxlength="100"
            />
          </div>

          <!-- Location -->
          <div class="form-group">
            <label for="event-location" class="form-label">Location *</label>
            <input 
              type="text" 
              id="event-location" 
              name="location" 
              class="form-input" 
              placeholder="e.g., Central Park, Downtown Area"
              required
              maxlength="200"
            />
          </div>

          <!-- Date and Time -->
          <div class="form-group">
            <label for="event-datetime" class="form-label">Date & Time *</label>
            <input 
              type="datetime-local" 
              id="event-datetime" 
              name="date_time" 
              class="form-input" 
              min="${minDateTime}"
              required
            />
          </div>

          <!-- Duration -->
          <div class="form-group">
            <label for="event-duration" class="form-label">Duration (minutes) *</label>
            <input 
              type="number" 
              id="event-duration" 
              name="duration" 
              class="form-input" 
              placeholder="e.g., 60"
              min="15"
              max="480"
              step="15"
              value="60"
              required
            />
            <p class="form-hint">Suggested: 30-120 minutes</p>
          </div>

          <!-- Type Focus -->
          <div class="form-group">
            <label class="form-label">Type Focus *</label>
            <div class="button-group">
              <button 
                type="button" 
                class="button-option" 
                data-type="vape"
                aria-pressed="false"
              >
                💨 Vape
              </button>
              <button 
                type="button" 
                class="button-option" 
                data-type="smoke"
                aria-pressed="false"
              >
                🚭 Smoke
              </button>
              <button 
                type="button" 
                class="button-option" 
                data-type="both"
                aria-pressed="false"
              >
                🌬️ Both
              </button>
            </div>
            <input type="hidden" id="event-type-focus" name="type_focus" required />
          </div>

          <!-- Context Hint (Optional) -->
          <div class="form-group">
            <label class="form-label">Context Hint (Optional)</label>
            <div class="button-group">
              <button 
                type="button" 
                class="button-option" 
                data-context="indoor"
                aria-pressed="false"
              >
                🏠 Indoor
              </button>
              <button 
                type="button" 
                class="button-option" 
                data-context="outdoor"
                aria-pressed="false"
              >
                🌳 Outdoor
              </button>
            </div>
            <input type="hidden" id="event-context-hint" name="context_hint" />
          </div>

          <!-- Description -->
          <div class="form-group">
            <label for="event-description" class="form-label">Description</label>
            <textarea 
              id="event-description" 
              name="description" 
              class="form-textarea" 
              rows="3"
              maxlength="500"
            >${defaultDescription}</textarea>
            <p class="form-hint">This supportive message will be shown to attendees</p>
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button type="button" class="button button-secondary" id="cancel-button">
              Cancel
            </button>
            <button type="submit" class="button button-primary" id="submit-button">
              Create Event
            </button>
          </div>

          <!-- Confirmation Message (hidden by default) -->
          <div id="confirmation-message" class="confirmation-message" style="display: none;">
            <div class="confirmation-content">
              <span class="confirmation-icon">✓</span>
              <p class="confirmation-text">Event created successfully! Looking forward to healing together.</p>
            </div>
          </div>

          <!-- Error Message (hidden by default) -->
          <div id="error-message" class="error-message" style="display: none;">
            <p class="error-text"></p>
          </div>
        </form>
      </div>
    `;

    this.container.innerHTML = html;

    // Attach event listeners
    this.attachEventListeners();
  }

  /**
   * Attach event listeners to form elements
   */
  attachEventListeners() {
    if (!this.container) return;

    const form = this.container.querySelector('#event-form-element');
    const cancelButton = this.container.querySelector('#cancel-button');
    const typeButtons = this.container.querySelectorAll('[data-type]');
    const contextButtons = this.container.querySelectorAll('[data-context]');

    // Form submission
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleSubmit(e);
      });
    }

    // Cancel button
    if (cancelButton) {
      cancelButton.addEventListener('click', () => {
        this.handleCancel();
      });
    }

    // Type focus buttons
    typeButtons.forEach(button => {
      button.addEventListener('click', () => {
        this.handleTypeSelection(button);
      });
    });

    // Context hint buttons
    contextButtons.forEach(button => {
      button.addEventListener('click', () => {
        this.handleContextSelection(button);
      });
    });
  }

  /**
   * Handle type focus button selection
   * @param {HTMLElement} selectedButton - The clicked button
   */
  handleTypeSelection(selectedButton) {
    const typeButtons = this.container.querySelectorAll('[data-type]');
    const hiddenInput = this.container.querySelector('#event-type-focus');
    const selectedType = selectedButton.getAttribute('data-type');

    // Update button states
    typeButtons.forEach(button => {
      if (button === selectedButton) {
        button.classList.add('selected');
        button.setAttribute('aria-pressed', 'true');
      } else {
        button.classList.remove('selected');
        button.setAttribute('aria-pressed', 'false');
      }
    });

    // Update hidden input
    if (hiddenInput) {
      hiddenInput.value = selectedType;
    }
  }

  /**
   * Handle context hint button selection
   * @param {HTMLElement} selectedButton - The clicked button
   */
  handleContextSelection(selectedButton) {
    const contextButtons = this.container.querySelectorAll('[data-context]');
    const hiddenInput = this.container.querySelector('#event-context-hint');
    const selectedContext = selectedButton.getAttribute('data-context');

    // Toggle selection (context is optional)
    if (selectedButton.classList.contains('selected')) {
      // Deselect
      selectedButton.classList.remove('selected');
      selectedButton.setAttribute('aria-pressed', 'false');
      if (hiddenInput) {
        hiddenInput.value = '';
      }
    } else {
      // Select this, deselect others
      contextButtons.forEach(button => {
        if (button === selectedButton) {
          button.classList.add('selected');
          button.setAttribute('aria-pressed', 'true');
        } else {
          button.classList.remove('selected');
          button.setAttribute('aria-pressed', 'false');
        }
      });
      if (hiddenInput) {
        hiddenInput.value = selectedContext;
      }
    }
  }

  /**
   * Handle form submission
   * Requirement: 9.1, 9.3 - Submit event and display confirmation
   * @param {Event} event - Form submit event
   */
  async handleSubmit(event) {
    event.preventDefault();

    if (this.isSubmitting) return;

    // Hide previous messages
    this.hideConfirmation();
    this.hideError();

    // Get form data
    const formData = new FormData(event.target);
    const data = {
      name: formData.get('name'),
      location: formData.get('location'),
      date_time: formData.get('date_time'),
      duration: parseInt(formData.get('duration'), 10),
      type_focus: formData.get('type_focus'),
      context_hint: formData.get('context_hint') || undefined,
      description: formData.get('description')
    };

    // Validate required fields
    if (!data.name || !data.location || !data.date_time || !data.duration || !data.type_focus) {
      this.showError('Please fill in all required fields');
      return;
    }

    // Validate type focus is selected
    if (!data.type_focus) {
      this.showError('Please select a type focus (Vape, Smoke, or Both)');
      return;
    }

    // Convert datetime-local to ISO format
    const dateTime = new Date(data.date_time);
    data.date_time = dateTime.toISOString();

    // Disable submit button
    this.isSubmitting = true;
    const submitButton = this.container.querySelector('#submit-button');
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = 'Creating...';
    }

    try {
      // Call API to create event
      const response = await fetch('/api/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create event');
      }

      const result = await response.json();

      // Update app state with new event
      const app = window.BreatheBackApp;
      if (app) {
        const state = app.getState();
        const updatedEvents = [...state.events, result.event];
        app.updateEvents(updatedEvents);
      }

      // Show confirmation message
      // Requirement: 9.3 - Display confirmation message after submission
      this.showConfirmation(result.message);

      // Reset form after short delay
      setTimeout(() => {
        this.resetForm();
        
        // Call onSubmit callback
        this.onSubmit(result.event);
      }, 2000);

    } catch (error) {
      console.error('Error creating event:', error);
      this.showError(error.message || 'Failed to create event. Please try again.');
    } finally {
      // Re-enable submit button
      this.isSubmitting = false;
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = 'Create Event';
      }
    }
  }

  /**
   * Handle form cancellation
   */
  handleCancel() {
    this.resetForm();
    this.onCancel();
  }

  /**
   * Reset the form to initial state
   */
  resetForm() {
    const form = this.container.querySelector('#event-form-element');
    if (form) {
      form.reset();
    }

    // Reset button selections
    const typeButtons = this.container.querySelectorAll('[data-type]');
    typeButtons.forEach(button => {
      button.classList.remove('selected');
      button.setAttribute('aria-pressed', 'false');
    });

    const contextButtons = this.container.querySelectorAll('[data-context]');
    contextButtons.forEach(button => {
      button.classList.remove('selected');
      button.setAttribute('aria-pressed', 'false');
    });

    // Reset hidden inputs
    const typeFocusInput = this.container.querySelector('#event-type-focus');
    if (typeFocusInput) {
      typeFocusInput.value = '';
    }

    const contextHintInput = this.container.querySelector('#event-context-hint');
    if (contextHintInput) {
      contextHintInput.value = '';
    }

    // Reset description to default
    const descriptionTextarea = this.container.querySelector('#event-description');
    if (descriptionTextarea) {
      descriptionTextarea.value = this.getDefaultDescription();
    }

    // Hide messages
    this.hideConfirmation();
    this.hideError();
  }

  /**
   * Show confirmation message
   * Requirement: 9.3 - Display confirmation message
   * @param {string} message - Confirmation message
   */
  showConfirmation(message) {
    const confirmationDiv = this.container.querySelector('#confirmation-message');
    const confirmationText = this.container.querySelector('.confirmation-text');
    
    if (confirmationDiv && confirmationText) {
      confirmationText.textContent = message;
      confirmationDiv.style.display = 'block';
    }
  }

  /**
   * Hide confirmation message
   */
  hideConfirmation() {
    const confirmationDiv = this.container.querySelector('#confirmation-message');
    if (confirmationDiv) {
      confirmationDiv.style.display = 'none';
    }
  }

  /**
   * Show error message
   * @param {string} message - Error message
   */
  showError(message) {
    const errorDiv = this.container.querySelector('#error-message');
    const errorText = this.container.querySelector('.error-text');
    
    if (errorDiv && errorText) {
      errorText.textContent = message;
      errorDiv.style.display = 'block';
    }
  }

  /**
   * Hide error message
   */
  hideError() {
    const errorDiv = this.container.querySelector('#error-message');
    if (errorDiv) {
      errorDiv.style.display = 'none';
    }
  }

  /**
   * Update the component
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

// Make EventForm available globally
window.EventForm = EventForm;
