"""
Quick test script for LLM cancer impact feature
Run this to verify your OpenRouter setup works
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file in root directory
load_dotenv()

from backend.services.llm_service import llm_service

def test_llm():
    """Test LLM service with sample zone data"""
    
    # Check API key
    if not os.environ.get('OPENROUTER_API_KEY'):
        print("❌ OPENROUTER_API_KEY not set!")
        print("\nCreate a file: backend/.env")
        print("Add this line: OPENROUTER_API_KEY=your-key-here")
        print("\nGet your key from: https://openrouter.ai/")
        return
    
    print("✅ API key found")
    print("\n" + "="*60)
    print("Testing LLM Cancer Impact Explanations")
    print("="*60)
    
    # Test 1: Needs Restoration Zone
    print("\n1. NEEDS RESTORATION ZONE (High vape debt)")
    print("-" * 60)
    zone_data = {
        'vape_debt': 150,
        'vape_restore': 20,
        'smoke_debt': 120,
        'smoke_restore': 15
    }
    
    try:
        explanation = llm_service.explain_zone_impact(zone_data, 'vape')
        print(f"✅ {explanation}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Healing Zone
    print("\n2. HEALING ZONE (Moderate debt and restore)")
    print("-" * 60)
    zone_data = {
        'vape_debt': 50,
        'vape_restore': 40,
        'smoke_debt': 45,
        'smoke_restore': 35
    }
    
    try:
        explanation = llm_service.explain_zone_impact(zone_data, 'vape')
        print(f"✅ {explanation}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Recovered Zone
    print("\n3. RECOVERED ZONE (High restore, low debt)")
    print("-" * 60)
    zone_data = {
        'vape_debt': 15,
        'vape_restore': 60,
        'smoke_debt': 10,
        'smoke_restore': 45
    }
    
    try:
        explanation = llm_service.explain_zone_impact(zone_data, 'vape')
        print(f"✅ {explanation}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Action Completion
    print("\n4. ACTION COMPLETION")
    print("-" * 60)
    
    try:
        explanation = llm_service.explain_action_impact(
            "Pick up vape waste",
            15,
            "needs_restoration",
            "vape"
        )
        print(f"✅ {explanation}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ All tests complete!")
    print("="*60)
    print("\nYour LLM feature is ready for the demo!")
    print("Start the server with: python app.py")

if __name__ == '__main__':
    test_llm()
