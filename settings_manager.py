import json
import os

class SettingsManager:
    def __init__(self, settings_file="settings.json", themes_file="themes.json"):
        self.settings_file = settings_file
        self.themes_file = themes_file
        self.default_settings = {
            "scaling_factor": 1.0,
            "theme_name": "light"
        }
        self.settings = self.load_settings()
        self.themes = self.load_themes()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                loaded_settings = json.load(f)
                # Ensure all keys are present
                for key, value in self.default_settings.items():
                    if key not in loaded_settings:
                        loaded_settings[key] = value
                return loaded_settings
        else:
            return self.default_settings.copy()

    def load_themes(self):
        with open(self.themes_file, "r") as f:
            return json.load(f)

    def save_settings(self):
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f)

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def update(self, new_settings):
        self.settings.update(new_settings)
        self.save_settings()

    def get_current_theme(self):
        theme_name = self.settings.get("theme_name", "light")
        if theme_name not in self.themes:
            print(f"Warning: Theme '{theme_name}' not found. Using 'light' theme.")
            theme_name = "light"
        return self.themes[theme_name]

    def get_theme_names(self):
        return list(self.themes.keys())

    def get_default_settings(self):
        return self.default_settings

    def reset_to_default(self):
        self.settings = self.default_settings.copy()
        self.save_settings()