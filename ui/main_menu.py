import tkinter as tk
from tkinter import ttk

class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        buttons = [
            ("View Flashcards", controller.view_flashcards, "📚"),
            ("Add Flashcard", controller.add_flashcard, "➕"),
            ("Edit Flashcards", controller.edit_flashcards, "✏️"),
            ("Start Study Session", controller.start_study_session, "🎓"),
            ("View Progress", controller.view_progress, "📊"),
            ("Manage Categories", controller.manage_categories, "🗂️")
        ]

        for text, command, icon in buttons:
            btn = ttk.Button(self, text=f"{icon} {text}", command=command)
            btn.pack(fill=tk.X, pady=10)