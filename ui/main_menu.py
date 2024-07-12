"""
main_menu.py

This file contains the MainMenu class for displaying the main menu of the flashcards application.
"""

import tkinter as tk
from tkinter import ttk

class MainMenu(ttk.Frame):
    """
    A class to represent the main menu of the flashcards application.
    """

    def __init__(self, parent, controller):
        """
        Initialize the MainMenu.

        Parameters:
        - parent (tk.Widget): The parent widget.
        - controller (FlashcardApp): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller
        self.create_buttons()

    def create_buttons(self):
        """
        Create the buttons for the main menu.
        """
        buttons = [
            ("View Flashcards", self.controller.view_flashcards, "📚"),
            ("Add Flashcard", self.controller.add_flashcard, "➕"),
            ("Edit Flashcards", self.controller.edit_flashcards, "✏️"),
            ("Start Study Session", self.controller.start_study_session, "🎓"),
            ("View Progress", self.controller.view_progress, "📊"),
            ("Manage Categories", self.controller.manage_categories, "🗂️"),
            ("Settings", self.controller.show_settings, "⚙️"),
            ("Quit App", self.controller.quit_app, "🚪")
        ]

        for text, command, icon in buttons:
            self.create_button(text, command, icon)

    def create_button(self, text, command, icon):
        """
        Create a single button for the main menu.

        Parameters:
        - text (str): The text to display on the button.
        - command (callable): The function to call when the button is clicked.
        - icon (str): The icon to display on the button.
        """
        btn = ttk.Button(self, text=f"{icon} {text}", command=command)
        btn.pack(fill=tk.X, pady=10)

# Example usage
# if __name__ == "__main__":
#     root = tk.Tk()
#     main_menu = MainMenu(root, controller)
#     main_menu.pack(fill=tk.BOTH, expand=True)
#     root.mainloop()
