"""
LLM Service for Cancer Impact Explanations
Uses OpenRouter to generate personalized, compelling explanations
of how air quality impacts cancer risk.

Requirements: Hack4Hope - Make cancer policy understandable and actionable
"""

import os
import requests
from typing import Dict, Optional


class LLMService:
    """Service for generating cancer impact explanations using LLM"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENROUTER_API_KEY', '')
        self.api_url = 'https://openrouter.ai/api/v1/chat/completions'
        # Use free model - Google Gemini Flash is fast and free
        # Alternative free models:
        # - 'google/gemini-flash-1.5-8b' (faster, smaller)
        # - 'meta-llama/llama-3.2-3b-instruct:free' (good quality)
        # - 'microsoft/phi-3-mini-128k-instruct:free' (compact)
        self.model = 'google/gemini-flash-1.5'
        
    def explain_zone_impact(self, zone_data: Dict, map_type: str = 'vape') -> str:
        """
        Explain how a zone's air quality affects cancer risk.
        
        Args:
            zone_data: Zone information (debt, restore scores)
            map_type: 'vape' or 'smoke'
            
        Returns:
            Compelling explanation of cancer risk and impact
        """
        # Calculate zone metrics
        if map_type == 'vape':
            debt = zone_data.get('vape_debt', 0)
            restore = zone_data.get('vape_restore', 0)
            exposure_type = 'vaping aerosols'
        else:
            debt = zone_data.get('smoke_debt', 0)
            restore = zone_data.get('smoke_restore', 0)
            exposure_type = 'secondhand smoke'
        
        net_score = restore - debt
        state = self._calculate_state(net_score)
        
        # Build prompt
        prompt = f"""You are a cancer prevention educator speaking to young adults (ages 16-25). 

Zone Status: {state}
Exposure Debt: {debt} points (harmful exposure accumulated)
Restoration: {restore} points (protective actions taken)
Net Score: {net_score}
Exposure Type: {exposure_type}

Write a compelling 2-3 sentence explanation that:
1. Explains what this zone's status means for cancer risk (be specific about lung cancer, throat cancer)
2. Makes it personal and relatable to youth
3. Ends with hope/empowerment about restoration actions

Tone: Direct, honest, empowering (not preachy or scary)
Length: 2-3 sentences max
Focus: Cancer prevention, not just general health"""

        try:
            response = self._call_llm(prompt)
            return response
        except Exception as e:
            # Fallback to static message if LLM fails
            return self._get_fallback_explanation(state, debt, restore, exposure_type)
    
    def explain_action_impact(self, action_title: str, points: int, 
                             zone_state: str, map_type: str = 'vape') -> str:
        """
        Explain how completing an action reduces cancer risk.
        
        Args:
            action_title: The action completed
            points: Points earned
            zone_state: Current zone state
            map_type: 'vape' or 'smoke'
            
        Returns:
            Explanation of cancer prevention impact
        """
        exposure_type = 'vaping aerosols' if map_type == 'vape' else 'secondhand smoke'
        
        prompt = f"""You are a cancer prevention educator celebrating a youth's action.

Action Completed: {action_title}
Points Earned: {points}
Zone Status: {zone_state}
Exposure Type: {exposure_type}

Write a celebratory 2 sentence explanation that:
1. Explains how THIS specific action reduces cancer risk
2. Quantifies the impact if possible (e.g., "reduces carcinogen exposure by X hours")
3. Empowers them to keep going

Tone: Celebratory, specific, empowering
Length: 2 sentences max
Focus: Direct cancer prevention impact"""

        try:
            response = self._call_llm(prompt)
            return response
        except Exception as e:
            return f"Amazing! Your {points} points help reduce {exposure_type} exposure in this area, directly lowering cancer risk for everyone here. Keep restoring!"
    
    def explain_total_impact(self, total_points: int, actions_completed: int,
                            zones_improved: int) -> str:
        """
        Explain the cumulative cancer prevention impact of all user actions.
        
        Args:
            total_points: Total restoration points earned
            actions_completed: Number of actions completed
            zones_improved: Number of zones moved to better state
            
        Returns:
            Compelling summary of cancer prevention impact
        """
        prompt = f"""You are a cancer prevention educator summarizing a youth's impact.

Total Points: {total_points}
Actions Completed: {actions_completed}
Zones Improved: {zones_improved}

Write an inspiring 2-3 sentence summary that:
1. Translates their points into real cancer prevention impact
2. Makes them feel like a cancer prevention hero
3. Connects to broader community health

Tone: Inspiring, quantitative, community-focused
Length: 2-3 sentences max
Focus: Cancer prevention at scale"""

        try:
            response = self._call_llm(prompt)
            return response
        except Exception as e:
            return f"Your {total_points} points have helped reduce carcinogen exposure across {zones_improved} zones. You're actively preventing cancer in your community—that's real impact!"
    
    def _call_llm(self, prompt: str) -> str:
        """Call OpenRouter API"""
        if not self.api_key:
            raise Exception("OPENROUTER_API_KEY not set")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://breatheback.app',  # Optional
            'X-Title': 'BreatheBack Cancer Prevention'  # Optional
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 150,
            'temperature': 0.7
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        
        return data['choices'][0]['message']['content'].strip()
    
    def _calculate_state(self, net_score: int) -> str:
        """Calculate zone state from net score"""
        if net_score > 20:
            return 'recovered'
        elif net_score > -20:
            return 'healing'
        else:
            return 'needs_restoration'
    
    def _get_fallback_explanation(self, state: str, debt: int, 
                                  restore: int, exposure_type: str) -> str:
        """Fallback explanations if LLM fails"""
        if state == 'needs_restoration':
            return f"This zone has high exposure to {exposure_type}, which contains carcinogens linked to lung and throat cancer. Your restoration actions can help reduce cancer risk for everyone here."
        elif state == 'healing':
            return f"This zone is improving! Reduced {exposure_type} exposure means lower cancer risk. Keep taking action to fully protect this community."
        else:
            return f"This zone is thriving with minimal {exposure_type} exposure. Low carcinogen levels mean reduced cancer risk—great work protecting community health!"


# Singleton instance
llm_service = LLMService()
