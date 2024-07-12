"""
study_session.py

This file contains the PreStudyOptionsDialog class for setting up study session options,
and the StudySession class for managing the study session itself.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random

class PreStudyOptionsDialog:
    """
    A dialog for setting up the study session options.
    """
    
    def __init__(self, parent, categories):
        """
        Initialize the PreStudyOptionsDialog.

        Parameters:
        - parent (tk.Widget): The parent widget.
        - categories (list): The list of categories.
        """
        self.top = tk.Toplevel(parent)
        self.top.title("Study Session Options")
        self.categories = categories
        self.result = None

        ttk.Label(self.top, text="Session Length:").pack(padx=10, pady=5)
        self.length_var = tk.IntVar(value=20)
        ttk.Spinbox(self.top, from_=5, to=50, textvariable=self.length_var).pack(padx=10, pady=5)

        ttk.Label(self.top, text="Categories:").pack(padx=10, pady=5)
        self.category_vars = []
        for category in categories:
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.top, text=category['name'], variable=var).pack(padx=10, pady=2, anchor="w")
            self.category_vars.append((category['name'], var))

        ttk.Button(self.top, text="Start Session", command=self.save).pack(padx=10, pady=10)

        self.top.transient(parent)
        self.top.grab_set()
        parent.wait_window(self.top)

    def save(self):
        """Save the selected options and close the dialog."""
        self.result = {
            "length": self.length_var.get(),
            "categories": [name for name, var in self.category_vars if var.get()]
        }
        self.top.destroy()

    def show(self):
        """Return the selected options."""
        return self.result

class StudySession(ttk.Frame):
    """
    A class to manage the study session.
    """
    
    def __init__(self, parent, controller, options):
        """
        Initialize the StudySession.

        Parameters:
        - parent (tk.Widget): The parent widget.
        - controller (FlashcardApp): The main application controller.
        - options (dict): The options for the study session.
        """
        super().__init__(parent)
        self.controller = controller
        self.options = options
        self.study_deck = self.get_study_deck()
        self.current_card_index = 0
        self.session_stats = {"total": len(self.study_deck), "correct": 0, "incorrect": 0}
        self.create_widgets()

    def get_study_deck(self):
        """Prepare the study deck based on the selected categories and session length."""
        try:
            category_ids = [cat['id'] for cat in self.controller.categories if cat['name'] in self.options['categories']]
            flashcards = self.controller.db_manager.get_flashcards_by_categories(category_ids)
            
            if not flashcards:
                return []

            weighted_deck = []
            for card in flashcards:
                weight = self.calculate_card_weight(card[0])
                weighted_deck.extend([card] * weight)
            random.shuffle(weighted_deck)
            return weighted_deck[:min(self.options["length"], len(weighted_deck))]
        except Exception as e:
            self.controller.error_handler.show_error("Failed to prepare study deck", str(e))
            return []

    def create_widgets(self):
        """Create the widgets for the study session."""
        if not self.study_deck:
            ttk.Label(self, text="No flashcards available for the selected categories.", wraplength=300).pack(pady=20)
            ttk.Button(self, text="Back to Main Menu", command=self.controller.show_main_menu).pack(pady=10)
            return

        self.progress_label = ttk.Label(self, text=f"Question 1/{self.session_stats['total']}")
        self.progress_label.pack(pady=(0, 20))

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=(0, 20))

        self.question_label = ttk.Label(self, text="", wraplength=700)
        self.question_label.pack(pady=20)

        self.answer_label = ttk.Label(self, text="", wraplength=700)
        self.answer_label.pack(pady=20)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=20)

        self.show_answer_button = ttk.Button(button_frame, text="Show Answer", command=self.show_answer)
        self.show_answer_button.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        self.correct_button = ttk.Button(button_frame, text="Correct ✅", command=self.mark_correct, state="disabled")
        self.correct_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.incorrect_button = ttk.Button(button_frame, text="Incorrect ❌", command=self.mark_incorrect, state="disabled")
        self.incorrect_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        self.show_question()

    def calculate_card_weight(self, card_id):
        """
        Calculate the weight of a flashcard based on its study history.

        Parameters:
        - card_id (int): The ID of the flashcard.

        Returns:
        - int: The weight of the flashcard.
        """
        try:
            history = self.controller.db_manager.get_study_history(card_id)
            if not history:
                return 5
            correct_ratio = sum(1 for result in history if result[0]) / len(history)
            return max(1, int(5 * (1 - correct_ratio)))
        except Exception as e:
            self.controller.error_handler.show_error("Failed to calculate card weight", str(e))
            return 1

    def show_question(self):
        """Display the current question."""
        if self.current_card_index < len(self.study_deck):
            self.progress_label.config(text=f"Question {self.current_card_index + 1}/{self.session_stats['total']}")
            self.question_label.config(text=self.study_deck[self.current_card_index][1])
            self.answer_label.config(text="")
            
            self.correct_button.config(state="disabled")
            self.incorrect_button.config(state="disabled")
            self.show_answer_button.config(state="normal")

            progress = (self.current_card_index + 1) / self.session_stats['total'] * 100
            self.progress_bar["value"] = progress
        else:
            self.show_session_summary()

    def show_answer(self):
        """Display the answer to the current question."""
        self.answer_label.config(text=self.study_deck[self.current_card_index][2])
        self.correct_button.config(state="normal")
        self.incorrect_button.config(state="normal")
        self.show_answer_button.config(state="disabled")

    def mark_correct(self):
        """Mark the current question as correct and move to the next question."""
        self.controller.db_manager.add_study_result(self.study_deck[self.current_card_index][0], True)
        self.session_stats["correct"] += 1
        self.next_question()

    def mark_incorrect(self):
        """Mark the current question as incorrect and move to the next question."""
        self.controller.db_manager.add_study_result(self.study_deck[self.current_card_index][0], False)
        self.session_stats["incorrect"] += 1
        self.next_question()

    def next_question(self):
        """Move to the next question in the study deck, ensuring no duplicate questions in a row."""
        previous_question = self.study_deck[self.current_card_index][1]
        while self.current_card_index < len(self.study_deck):
            self.current_card_index += 1
            if self.current_card_index < len(self.study_deck) and self.study_deck[self.current_card_index][1] != previous_question:
                break
        self.show_question()

    def show_session_summary(self):
        """Display the summary of the study session."""
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(self, text="Session Summary", style="Header.TLabel").pack(pady=(0, 20))
        ttk.Label(self, text=f"Total Questions: {self.session_stats['total']}").pack()
        ttk.Label(self, text=f"Correct Answers: {self.session_stats['correct']}").pack()
        ttk.Label(self, text=f"Incorrect Answers: {self.session_stats['incorrect']}").pack()
        
        if self.session_stats['total'] > 0:
            accuracy = (self.session_stats['correct'] / self.session_stats['total']) * 100
            ttk.Label(self, text=f"Accuracy: {accuracy:.2f}%").pack(pady=(10, 20))
            self.create_circular_progress_bar(accuracy)
        else:
            ttk.Label(self, text="No questions were answered in this session.").pack(pady=(10, 20))

        ttk.Button(self, text="Back to Main Menu", command=self.controller.show_main_menu).pack(pady=(20, 0))

    def create_circular_progress_bar(self, percentage):
        """
        Create a circular progress bar to display the accuracy percentage.

        Parameters:
        - percentage (float): The accuracy percentage.
        """
        canvas = tk.Canvas(self, width=100, height=100, bg=self.controller.style.lookup("TFrame", "background"))
        canvas.pack(pady=20)

        canvas.create_arc(10, 10, 90, 90, start=0, extent=359.999, fill="lightgray")
        canvas.create_arc(10, 10, 90, 90, start=90, extent=-(percentage * 3.6), fill="#6200EE")
        canvas.create_text(50, 50, text=f"{percentage:.1f}%", font=("Helvetica", 16, "bold"))
