import tkinter as tk
from tkinter import ttk
import random

class PreStudyOptionsDialog:
    def __init__(self, parent, categories):
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
        self.result = {
            "length": self.length_var.get(),
            "categories": [name for name, var in self.category_vars if var.get()]
        }
        self.top.destroy()

    def show(self):
        return self.result

class StudySession(ttk.Frame):
    def __init__(self, parent, controller, options):
        super().__init__(parent)
        self.controller = controller
        self.options = options
        self.study_deck = self.get_study_deck()
        self.current_card_index = 0
        self.session_stats = {"total": len(self.study_deck), "correct": 0, "incorrect": 0}
        self.create_widgets()

    def get_study_deck(self):
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

        ttk.Button(button_frame, text="Show Answer", command=self.show_answer).pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        ttk.Button(button_frame, text="Correct ✅", command=self.mark_correct).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(button_frame, text="Incorrect ❌", command=self.mark_incorrect).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        self.show_question()

    def calculate_card_weight(self, card_id):
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
        if self.current_card_index < len(self.study_deck):
            self.progress_label.config(text=f"Question {self.current_card_index + 1}/{self.session_stats['total']}")
            self.question_label.config(text=self.study_deck[self.current_card_index][1])
            self.answer_label.config(text="")
            
            progress = (self.current_card_index + 1) / self.session_stats['total'] * 100
            self.progress_bar["value"] = progress
        else:
            self.show_session_summary()

    def show_answer(self):
        self.answer_label.config(text=self.study_deck[self.current_card_index][2])

    def mark_correct(self):
        self.controller.db_manager.add_study_result(self.study_deck[self.current_card_index][0], True)
        self.session_stats["correct"] += 1
        self.controller.show_toast("Correct!")
        self.next_question()

    def mark_incorrect(self):
        self.controller.db_manager.add_study_result(self.study_deck[self.current_card_index][0], False)
        self.session_stats["incorrect"] += 1
        self.controller.show_toast("Incorrect")
        self.next_question()

    def next_question(self):
        self.current_card_index += 1
        if self.current_card_index < len(self.study_deck):
            while self.current_card_index < len(self.study_deck) - 1 and self.study_deck[self.current_card_index][1] == self.study_deck[self.current_card_index - 1][1]:
                self.current_card_index += 1
        self.show_question()

    def show_session_summary(self):
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
        canvas = tk.Canvas(self, width=100, height=100, bg=self.controller.style.lookup("TFrame", "background"))
        canvas.pack(pady=20)

        canvas.create_arc(10, 10, 90, 90, start=0, extent=359.999, fill="lightgray")
        canvas.create_arc(10, 10, 90, 90, start=90, extent=-(percentage * 3.6), fill="#6200EE")
        canvas.create_text(50, 50, text=f"{percentage:.1f}%", font=("Helvetica", 16, "bold"))