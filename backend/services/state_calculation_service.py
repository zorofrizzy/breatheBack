"""State calculation service for zone restoration states.

Calculates restoration states based on zone debt and restoration scores.
Requirements: 13.3, 13.4, 13.5, 7.1
"""

from typing import Literal
from backend.models.zone import Zone
from backend.constants import RECOVERED_THRESHOLD, HEALING_THRESHOLD


RestorationState = Literal['needs_restoration', 'healing', 'recovered']


class StateCalculationService:
    """
    Service for calculating zone restoration states.
    
    Determines the restoration state of a zone based on the net score
    (restoration score - debt) for either vape or smoke data.
    """
    
    @staticmethod
    def calculate_state(zone: Zone, type: Literal['vape', 'smoke']) -> RestorationState:
        """
        Calculate the restoration state for a zone based on type.
        
        State calculation logic (Property 39):
        - If (Restoration_Score - Air_Debt) > RECOVERED_THRESHOLD, state = Recovered
        - Else if (Restoration_Score - Air_Debt) > HEALING_THRESHOLD, state = Healing
        - Else state = Needs Restoration
        
        Data Isolation (Property 29):
        - Vape state calculations use ONLY vape data (vape_debt, vape_restore)
        - Smoke state calculations use ONLY smoke data (smoke_debt, smoke_restore)
        - No mixing of data types is allowed
        
        Args:
            zone: The zone to calculate state for
            type: Either 'vape' or 'smoke' to determine which data to use
            
        Returns:
            RestorationState: One of 'needs_restoration', 'healing', or 'recovered'
            
        Requirements: 10.2, 10.3, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8
        """
        # Validate type parameter to prevent data mixing
        if type not in ('vape', 'smoke'):
            raise ValueError(f"Invalid type: {type}. Must be 'vape' or 'smoke'")
        
        # Get the appropriate debt and restoration scores based on type
        # CRITICAL: Data isolation - only use type-specific data
        if type == 'vape':
            debt = zone.vape_debt
            restore = zone.vape_restore
            # Validation: Ensure we're not accidentally using smoke data
            if debt == zone.smoke_debt and restore == zone.smoke_restore and (debt != 0 or restore != 0):
                raise ValueError("Data isolation violation: vape calculation attempted to use smoke data")
        else:  # type == 'smoke'
            debt = zone.smoke_debt
            restore = zone.smoke_restore
            # Validation: Ensure we're not accidentally using vape data
            if debt == zone.vape_debt and restore == zone.vape_restore and (debt != 0 or restore != 0):
                raise ValueError("Data isolation violation: smoke calculation attempted to use vape data")
        
        # Calculate net score using only type-specific data
        net_score = restore - debt
        
        # Apply thresholds to determine state
        if net_score > RECOVERED_THRESHOLD:
            return 'recovered'
        elif net_score > HEALING_THRESHOLD:
            return 'healing'
        else:
            return 'needs_restoration'
    
    @staticmethod
    def get_state_color(state: RestorationState) -> str:
        """
        Get the color code for a restoration state.
        
        Args:
            state: The restoration state
            
        Returns:
            str: Hex color code for the state
            
        Color mapping:
        - needs_restoration: Yellow (#F4D03F)
        - healing: Green (#52BE80)
        - recovered: Blue (#5DADE2)
        """
        color_map = {
            'needs_restoration': '#F4D03F',  # Soft yellow
            'healing': '#52BE80',             # Soft green
            'recovered': '#5DADE2'            # Soft blue
        }
        
        if state not in color_map:
            raise ValueError(f"Invalid state: {state}")
        
        return color_map[state]
    
    @staticmethod
    def get_state_message(state: RestorationState) -> str:
        """
        Get a supportive message for a restoration state.
        
        Args:
            state: The restoration state
            
        Returns:
            str: Supportive, non-accusatory message for the state
            
        Requirements: 7.1, 7.2, 7.3, 7.4
        """
        message_map = {
            'needs_restoration': 'This space needs care',
            'healing': 'This space is healing',
            'recovered': 'This space has recovered'
        }
        
        if state not in message_map:
            raise ValueError(f"Invalid state: {state}")
        
        return message_map[state]

