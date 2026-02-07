"""
Test script for main.js integration
Tests that all components are properly wired together
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_main_integration():
    """Test main.js integration with all components"""
    
    print("=" * 60)
    print("Testing Main.js Integration")
    print("=" * 60)
    
    # Check if backend is running
    print("\n1. Checking backend connection...")
    try:
        response = requests.get('http://localhost:5000/api/zones', timeout=5)
        if response.status_code == 200:
            print("   ✓ Backend is running")
        else:
            print(f"   ✗ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Backend connection failed: {e}")
        print("   Please ensure Flask server is running: python app.py")
        return False
    
    # Set up Chrome driver
    print("\n2. Setting up browser...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("   ✓ Browser initialized")
    except Exception as e:
        print(f"   ✗ Failed to initialize browser: {e}")
        return False
    
    try:
        # Load the application
        print("\n3. Loading application...")
        driver.get('http://localhost:5000/')
        time.sleep(2)  # Wait for initialization
        print("   ✓ Application loaded")
        
        # Test 1: Check if all components are loaded
        print("\n4. Testing component loading...")
        components = [
            'NavigationBar',
            'ReportForm',
            'RestorationActionCard',
            'HeatmapView',
            'ZoneInspector',
            'PointsSummary',
            'EventList',
            'EventForm',
            'BreatheBackApp',
            'BreatheBackMain'
        ]
        
        all_loaded = True
        for component in components:
            result = driver.execute_script(f"return typeof window.{component} !== 'undefined';")
            if result:
                print(f"   ✓ {component} loaded")
            else:
                print(f"   ✗ {component} not loaded")
                all_loaded = False
        
        if not all_loaded:
            print("\n   ✗ Not all components loaded")
            return False
        
        # Test 2: Check if app is initialized
        print("\n5. Testing application initialization...")
        app_initialized = driver.execute_script("""
            return window.BreatheBackApp && 
                   typeof window.BreatheBackApp.getState === 'function';
        """)
        
        if app_initialized:
            print("   ✓ BreatheBackApp initialized")
        else:
            print("   ✗ BreatheBackApp not initialized")
            return False
        
        # Test 3: Check application state
        print("\n6. Testing application state...")
        state = driver.execute_script("return window.BreatheBackApp.getState();")
        
        if state:
            print("   ✓ Application state exists")
            
            # Check default view
            if state.get('currentView') == 'report':
                print("   ✓ Default view is 'report'")
            else:
                print(f"   ✗ Default view is '{state.get('currentView')}', expected 'report'")
                return False
            
            # Check state structure
            if 'zones' in state:
                print("   ✓ Zones initialized")
            else:
                print("   ✗ Zones not initialized")
                return False
            
            if state.get('userPoints'):
                print("   ✓ User points initialized")
            else:
                print("   ✗ User points not initialized")
                return False
            
            if isinstance(state.get('events'), list):
                print("   ✓ Events array initialized")
            else:
                print("   ✗ Events not initialized")
                return False
        else:
            print("   ✗ Application state not found")
            return False
        
        # Test 4: Check view routing
        print("\n7. Testing view routing...")
        views = ['report', 'heatmap', 'community', 'mypoints']
        
        for view in views:
            # Navigate to view
            driver.execute_script(f"window.BreatheBackApp.updateView('{view}');")
            time.sleep(0.5)
            
            # Check current view
            current_view = driver.execute_script("return window.BreatheBackApp.getState().currentView;")
            
            if current_view == view:
                print(f"   ✓ Navigate to '{view}' successful")
            else:
                print(f"   ✗ Navigate to '{view}' failed (current: {current_view})")
                return False
        
        # Return to report view
        driver.execute_script("window.BreatheBackApp.updateView('report');")
        
        # Test 5: Check navigation bar
        print("\n8. Testing navigation bar...")
        nav_items = driver.find_elements(By.CLASS_NAME, 'nav-item')
        
        if len(nav_items) == 4:
            print(f"   ✓ Navigation bar has 4 items")
        else:
            print(f"   ✗ Navigation bar has {len(nav_items)} items, expected 4")
            return False
        
        # Test 6: Check view containers
        print("\n9. Testing view containers...")
        view_containers = ['report-view', 'heatmap-view', 'community-view', 'mypoints-view']
        
        for container_id in view_containers:
            element = driver.find_element(By.ID, container_id)
            if element:
                print(f"   ✓ {container_id} exists")
            else:
                print(f"   ✗ {container_id} not found")
                return False
        
        # Test 7: Check component containers
        print("\n10. Testing component containers...")
        component_containers = [
            'report-form-container',
            'restoration-card-container',
            'map-container',
            'zone-inspector-container',
            'points-summary-container',
            'event-list-container',
            'event-form-container'
        ]
        
        for container_id in component_containers:
            element = driver.find_element(By.ID, container_id)
            if element:
                print(f"   ✓ {container_id} exists")
            else:
                print(f"   ✗ {container_id} not found")
                return False
        
        print("\n" + "=" * 60)
        print("✓ All integration tests passed!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        driver.quit()

if __name__ == '__main__':
    success = test_main_integration()
    exit(0 if success else 1)

