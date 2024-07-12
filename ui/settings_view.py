"""
settings_view.py

This file contains the SettingsView class for managing the application's settings.
"""

import tkinter as tk
from tkinter import ttk

class SettingsView(ttk.Frame):
    """
    A class to manage the settings view for the flashcards application.
    """
    
    def __init__(self, parent, settings_manager, apply_settings, show_toast):
        """
        Initialize the SettingsView.

        Parameters:
        - parent (tk.Widget): The parent widget.
        - settings_manager (SettingsManager): The settings manager.
        - apply_settings (callable): A callback function to apply the new settings.
        - show_toast (callable): A callback function to show toast messages.
        """
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.apply_settings = apply_settings
        self.show_toast = show_toast
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the SettingsView."""
        # Theme Selection
        ttk.Label(self, text="Theme:").pack(anchor="w", pady=(0, 5))
        self.theme_var = tk.StringVar(value=self.settings_manager.get("theme_name"))
        theme_names = self.settings_manager.get_theme_names()
        ttk.Combobox(self, textvariable=self.theme_var, values=theme_names).pack(fill=tk.X, pady=(0, 10))

        # UI Scale
        ttk.Label(self, text="UI Scale:").pack(anchor="w", pady=(0, 5))
        self.scale_var = tk.DoubleVar(value=self.settings_manager.get("scaling_factor"))
        scale_options = [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
        ttk.Combobox(self, textvariable=self.scale_var, values=scale_options).pack(fill=tk.X, pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Reset to Default", command=self.reset_settings).pack(side=tk.LEFT)

    def save_settings(self):
        """Save the settings."""
        try:
            new_settings = {
                "theme_name": self.theme_var.get(),
                "scaling_factor": float(self.scale_var.get())
            }
            self.validate_settings(new_settings)
            self.settings_manager.update(new_settings)
            self.apply_settings()
            self.show_toast("Settings saved successfully!")
        except ValueError as e:
            self.show_toast(str(e))

    def reset_settings(self):
        """Reset the settings to default values."""
        default_settings = self.settings_manager.get_default_settings()
        self.theme_var.set(default_settings["theme_name"])
        self.scale_var.set(default_settings["scaling_factor"])
        self.settings_manager.reset_to_default()
        self.apply_settings()
        self.show_toast("Settings reset to default!")

    def validate_settings(self, settings):
        """
        Validate the new settings.

        Parameters:
        - settings (dict): The settings to validate.

        Raises:
        - ValueError: If any setting value is invalid.
        """
        theme_name = settings["theme_name"]
        scaling_factor = settings["scaling_factor"]

        if theme_name not in self.settings_manager.get_theme_names():
            raise ValueError("Invalid theme name.")
        
        if scaling_factor not in [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]:
            raise ValueError("Invalid scaling factor.")
