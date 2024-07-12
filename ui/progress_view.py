"""
progress_view.py

This file contains the ProgressView class for displaying flashcard study statistics.
"""

import tkinter as tk
from tkinter import ttk, messagebox

class ProgressView(ttk.Frame):
    """
    A class to represent the progress view of the flashcards application.
    """
    
    def __init__(self, parent, controller):
        """
        Initialize the ProgressView.

        Parameters:
        - parent (tk.Widget): The parent widget.
        - controller (FlashcardApp): The main application controller.
        """
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the progress view."""
        self.create_treeview()
        self.create_buttons()
        self.load_statistics()

    def create_treeview(self):
        """Create the treeview for displaying statistics."""
        self.tree = ttk.Treeview(self, columns=("Question", "Category", "Correct", "Total", "Percentage"), show="headings")
        self.tree.heading("Question", text="Question")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Correct", text="Correct")
        self.tree.heading("Total", text="Total")
        self.tree.heading("Percentage", text="Success Rate")
        self.tree.column("Question", width=300)
        self.tree.column("Category", width=100)
        self.tree.column("Correct", width=70)
        self.tree.column("Total", width=70)
        self.tree.column("Percentage", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_buttons(self):
        """Create the buttons for interacting with the statistics."""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Reset Statistics", command=self.reset_statistics).pack(side=tk.LEFT, padx=5)

    def load_statistics(self):
        """Load the statistics from the database and display them in the treeview."""
        self.tree.delete(*self.tree.get_children())
        try:
            statistics = self.controller.db_manager.get_flashcard_statistics()
            for stat in statistics:
                success_rate = self.calculate_success_rate(stat['correct'], stat['total'])
                self.tree.insert("", tk.END, values=(stat['question'], stat['category'], stat['correct'], stat['total'], success_rate))
        except Exception as e:
            self.controller.error_handler.show_error("Failed to load statistics", str(e))

    def calculate_success_rate(self, correct, total):
        """
        Calculate the success rate for a flashcard.

        Parameters:
        - correct (int): The number of correct answers.
        - total (int): The total number of answers.

        Returns:
        - str: The success rate as a percentage string.
        """
        if total > 0:
            return f"{(correct / total * 100):.2f}%"
        return "N/A"

    def reset_statistics(self):
        """Reset the statistics after user confirmation."""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all statistics? This action cannot be undone."):
            try:
                self.controller.db_manager.reset_statistics()
                self.load_statistics()
                self.controller.show_toast("Statistics reset successfully")
            except Exception as e:
                self.controller.error_handler.show_error("Failed to reset statistics", str(e))
