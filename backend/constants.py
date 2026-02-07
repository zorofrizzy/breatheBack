"""Constants for BreatheBack application.

Defines thresholds for zone state calculations and scoring.
Requirements: 13.3, 13.4, 13.5
"""

# Debt increment per report
DEBT_INCREMENT = 10

# State calculation thresholds
RECOVERED_THRESHOLD = 20  # Net score > 20 means zone is recovered
HEALING_THRESHOLD = -20   # Net score between -20 and 20 means zone is healing
                          # Net score < -20 means zone needs restoration

# Grid size for zone calculation (degrees)
ZONE_GRID_SIZE = 0.01  # Approximately 1km at equator
