/**
 * BottomSheetManager
 * Manages bottom sheet overlays (Points, Zone Inspector, Actions)
 * Only one sheet visible at a time
 */

class BottomSheetManager {
  constructor() {
    this.overlay = null;
    this.currentSheet = null;
    this.sheets = new Map();
  }
  
  init() {
    this.overlay = document.getElementById('bottom-sheet-overlay');
    if (!this.overlay) {
      console.error('BottomSheetManager: overlay not found');
      return;
    }
    
    // Register all sheets
    this.registerSheet('points', document.getElementById('points-panel'));
    this.registerSheet('zone', document.getElementById('zone-inspector-panel'));
    this.registerSheet('actions', document.getElementById('actions-panel'));
    
    // Close on overlay click
    this.overlay.addEventListener('click', (e) => {
      if (e.target === this.overlay) {
        this.closeAll();
      }
    });
    
    // Close buttons
    document.querySelectorAll('.sheet-close').forEach(btn => {
      btn.addEventListener('click', () => this.closeAll());
    });
    
    // Points chip opens points panel
    const pointsChip = document.getElementById('points-chip');
    if (pointsChip) {
      pointsChip.addEventListener('click', () => this.open('points'));
    }
  }
  
  registerSheet(id, element) {
    if (element) {
      this.sheets.set(id, element);
    }
  }
  
  open(sheetId) {
    const sheet = this.sheets.get(sheetId);
    if (!sheet) {
      console.error(`Sheet "${sheetId}" not found`);
      return;
    }
    
    // Close current sheet if any
    if (this.currentSheet) {
      this.currentSheet.classList.add('hidden');
    }
    
    // Show overlay
    this.overlay.classList.remove('hidden');
    
    // Show new sheet
    sheet.classList.remove('hidden');
    this.currentSheet = sheet;
    
    // Trigger any update callbacks
    this.triggerUpdate(sheetId);
  }
  
  closeAll() {
    if (this.currentSheet) {
      this.currentSheet.classList.add('hidden');
      this.currentSheet = null;
    }
    
    this.overlay.classList.add('hidden');
  }
  
  triggerUpdate(sheetId) {
    // Update content when sheet opens
    if (sheetId === 'points' && window.pointsSummary) {
      window.pointsSummary.update();
    }
  }
  
  isOpen() {
    return this.currentSheet !== null;
  }
}

// Make available globally
if (typeof window !== 'undefined') {
  window.BottomSheetManager = BottomSheetManager;
}
