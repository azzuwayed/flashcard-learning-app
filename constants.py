"""
constants.py

This file contains default constants used throughout the flashcards application.
"""

import os

# Default Font Configuration
DEFAULT_FONT = os.getenv("FLASHCARDS_DEFAULT_FONT", "Helvetica")
DEFAULT_FONT_SIZE = int(os.getenv("FLASHCARDS_DEFAULT_FONT_SIZE", 12))

# Default Window Resolution
DEFAULT_RESOLUTION = os.getenv("FLASHCARDS_DEFAULT_RESOLUTION", "800x600")
RESOLUTIONS = ["800x600", "1024x768", "1280x720"]

# Study Session Length (in minutes)
DEFAULT_STUDY_SESSION_LENGTH = int(os.getenv("FLASHCARDS_DEFAULT_STUDY_SESSION_LENGTH", 20))

# Default Colors
DEFAULT_COLORS = {
    "bg": "#F5F5F5",      # Background color
    "fg": "#333333",      # Foreground (text) color
    "button": "#E0E0E0",  # Button color
    "accent": "#6200EE"   # Accent color
}

# Validation
def validate_resolution(resolution):
    if resolution not in RESOLUTIONS:
        raise ValueError(f"Resolution {resolution} is not supported. Choose from {RESOLUTIONS}.")

# Validate the default resolution
validate_resolution(DEFAULT_RESOLUTION)

# If needed, you can also validate other constants here
# Example:
# def validate_font_size(size):
#     if size <= 0:
#         raise ValueError(f"Font size {size} must be positive.")
# validate_font_size(DEFAULT_FONT_SIZE)
