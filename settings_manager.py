"""
settings_manager.py

This file contains the SettingsManager class for managing the application's settings and themes.
"""

import json
import os
import logging

class SettingsManager:
    """
    A class to manage the settings and themes for the flashcards application.
    """
    
    def __init__(self, settings_file=None, themes_file=None):
        """
        Initialize the SettingsManager with the specified settings and themes files.
        
        Parameters:
        - settings_file (str): The name of the settings file. Default is 'settings.json'.
        - themes_file (str): The name of the themes file. Default is 'themes.json'.
        """
        self.settings_file = settings_file or os.getenv("FLASHCARDS_SETTINGS_FILE", "settings.json")
        self.themes_file = themes_file or os.getenv("FLASHCARDS_THEMES_FILE", "themes.json")
        self.default_settings = {
            "scaling_factor": 1.0,
            "theme_name": "light"
        }
        self.settings = self.load_settings()
        self.themes = self.load_themes()

    def load_settings(self):
        """
        Load settings from the settings file. If the file does not exist, return default settings.

        Returns:
        - dict: The loaded or default settings.
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    loaded_settings = json.load(f)
                    # Ensure all keys are present
                    for key, value in self.default_settings.items():
                        if key not in loaded_settings:
                            loaded_settings[key] = value
                    logging.info("Settings loaded successfully.")
                    return loaded_settings
            else:
                logging.warning(f"Settings file '{self.settings_file}' not found. Using default settings.")
                return self.default_settings.copy()
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Error loading settings: {e}")
            return self.default_settings.copy()

    def load_themes(self):
        """
        Load themes from the themes file.

        Returns:
        - dict: The loaded themes.
        """
        try:
            with open(self.themes_file, "r") as f:
                logging.info("Themes loaded successfully.")
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Error loading themes: {e}")
            return {}

    def save_settings(self):
        """Save the current settings to the settings file."""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f)
                logging.info("Settings saved successfully.")
        except IOError as e:
            logging.error(f"Error saving settings: {e}")

    def get(self, key):
        """
        Get the value of a setting by key.

        Parameters:
        - key (str): The setting key.

        Returns:
        - The value of the setting, or None if the key does not exist.
        """
        return self.settings.get(key)

    def set(self, key, value):
        """
        Set the value of a setting.

        Parameters:
        - key (str): The setting key.
        - value: The value to set.
        """
        self.settings[key] = value
        self.save_settings()

    def update(self, new_settings):
        """
        Update the settings with a dictionary of new settings.

        Parameters:
        - new_settings (dict): A dictionary of new settings.
        """
        self.settings.update(new_settings)
        self.save_settings()

    def get_current_theme(self):
        """
        Get the current theme based on the 'theme_name' setting.

        Returns:
        - dict: The current theme.
        """
        theme_name = self.settings.get("theme_name", "light")
        if theme_name not in self.themes:
            logging.warning(f"Theme '{theme_name}' not found. Using 'light' theme.")
            theme_name = "light"
        return self.themes.get(theme_name, {})

    def get_theme_names(self):
        """
        Get a list of all available theme names.

        Returns:
        - list: A list of theme names.
        """
        return list(self.themes.keys())

    def get_default_settings(self):
        """
        Get the default settings.

        Returns:
        - dict: The default settings.
        """
        return self.default_settings

    def reset_to_default(self):
        """
        Reset the settings to the default settings.
        """
        self.settings = self.default_settings.copy()
        self.save_settings()
        logging.info("Settings reset to default.")
