import tkinter as tk
from tkinter import ttk

class SettingsView(ttk.Frame):
    def __init__(self, parent, settings_manager, apply_settings, show_toast):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.apply_settings = apply_settings
        self.show_toast = show_toast
        self.create_widgets()

    def create_widgets(self):
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

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Reset to Default", command=self.reset_settings).pack(side=tk.LEFT)

    def save_settings(self):
        new_settings = {
            "theme_name": self.theme_var.get(),
            "scaling_factor": float(self.scale_var.get())
        }
        self.settings_manager.update(new_settings)
        self.apply_settings()
        self.show_toast("Settings saved successfully!")

    def reset_settings(self):
        default_settings = self.settings_manager.get_default_settings()
        self.theme_var.set(default_settings["theme_name"])
        self.scale_var.set(default_settings["scaling_factor"])
        self.settings_manager.reset_to_default()
        self.apply_settings()
        self.show_toast("Settings reset to default!")