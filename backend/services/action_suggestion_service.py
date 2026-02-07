"""Action suggestion service for context-aware restoration actions.

Provides restoration action suggestions based on context (indoor/outdoor).
Requirements: 4.2, 4.3, 4.4, 4.5
"""

import random
from typing import List, Literal, Optional
from dataclasses import dataclass


@dataclass
class RestorationAction:
    """
    Represents a restoration action that users can complete.
    
    Attributes:
        id: Unique identifier for the action
        title: Short title for the action
        description: Detailed description of the action
        points: Clean_Air_Points value for completing this action
        context: Context where this action is applicable ('indoor', 'outdoor', or 'both')
    """
    id: str
    title: str
    description: str
    points: int
    context: Literal['indoor', 'outdoor', 'both']


# Indoor-specific restoration actions (ventilation-focused)
INDOOR_ACTIONS: List[RestorationAction] = [
    RestorationAction(
        id='indoor_1',
        title='Open a window',
        description='Let fresh air in for 5 minutes',
        points=10,
        context='indoor'
    ),
    RestorationAction(
        id='indoor_2',
        title='Move near ventilation',
        description='Find a spot with better air flow',
        points=5,
        context='indoor'
    ),
    RestorationAction(
        id='indoor_3',
        title='Relocate to open area',
        description='Step into a more spacious zone',
        points=8,
        context='indoor'
    ),
    RestorationAction(
        id='indoor_4',
        title='Use a fan',
        description='Improve air circulation',
        points=7,
        context='indoor'
    ),
]

# Outdoor-specific restoration actions (spacing-focused)
OUTDOOR_ACTIONS: List[RestorationAction] = [
    RestorationAction(
        id='outdoor_1',
        title='Step away',
        description='Move from dense areas',
        points=5,
        context='outdoor'
    ),
    RestorationAction(
        id='outdoor_2',
        title='Choose open air',
        description='Find a well-ventilated spot',
        points=8,
        context='outdoor'
    ),
    RestorationAction(
        id='outdoor_3',
        title='Move upwind',
        description='Position yourself upwind',
        points=10,
        context='outdoor'
    ),
    RestorationAction(
        id='outdoor_4',
        title='Find fresh air',
        description='Locate a clearer space',
        points=7,
        context='outdoor'
    ),
]

# Universal actions applicable in any context
UNIVERSAL_ACTIONS: List[RestorationAction] = [
    RestorationAction(
        id='universal_1',
        title='Wear a face mask',
        description='Breathe cleaner air',
        points=5,
        context='both'
    ),
    RestorationAction(
        id='universal_2',
        title='Encourage others',
        description='Share air restoration tips',
        points=10,
        context='both'
    ),
]


class ActionSuggestionService:
    """
    Service for providing context-aware restoration action suggestions.
    
    Returns 3-5 actions based on the provided context, prioritizing
    context-specific actions while including universal actions as fallback.
    """
    
    @staticmethod
    def get_suggestions(
        context: Optional[Literal['indoor', 'outdoor']] = None,
        type: Literal['vape', 'smoke'] = 'vape'
    ) -> List[RestorationAction]:
        """
        Get restoration action suggestions based on context.
        
        Returns 3-5 actions, prioritizing context-specific actions when
        context is provided. Actions are randomized for variety.
        
        Args:
            context: Optional context ('indoor' or 'outdoor')
            type: Type of air impact ('vape' or 'smoke') - currently not used
                  for differentiation but included for future extensibility
        
        Returns:
            List of 3-5 RestorationAction objects
        
        Requirements: 4.2, 4.3, 4.4, 4.5
        """
        # Start with an empty list of candidate actions
        candidate_actions: List[RestorationAction] = []
        
        # Add context-specific actions if context is provided
        if context == 'indoor':
            candidate_actions.extend(INDOOR_ACTIONS)
        elif context == 'outdoor':
            candidate_actions.extend(OUTDOOR_ACTIONS)
        
        # Always include universal actions
        candidate_actions.extend(UNIVERSAL_ACTIONS)
        
        # If no context provided, include all actions
        if context is None:
            candidate_actions.extend(INDOOR_ACTIONS)
            candidate_actions.extend(OUTDOOR_ACTIONS)
        
        # Randomize the order for variety
        shuffled_actions = candidate_actions.copy()
        random.shuffle(shuffled_actions)
        
        # Return 3-5 actions (Property 9: Action count range)
        # We'll return between 3 and 5 actions, preferring 5 if available
        num_actions = min(5, max(3, len(shuffled_actions)))
        
        return shuffled_actions[:num_actions]
