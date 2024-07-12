import os
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import customtkinter as ctk

# Set appearance mode and default color theme for customtkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Suppress deprecation warning for Tkinter on macOS
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# Type aliases
FlashcardRecord = Tuple[int, str, str, str, str, str, float, int]


class DatabaseManager:
    def __init__(self, db_name: str = 'flashcards.db'):
        self.db_name = db_name
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_name)

    def init_db(self) -> None:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS flashcards
                         (id INTEGER PRIMARY KEY,
                          question TEXT NOT NULL,
                          answer TEXT NOT NULL,
                          category TEXT,
                          last_reviewed DATE,
                          next_review DATE,
                          ease_factor REAL DEFAULT 2.5,
                          interval INTEGER DEFAULT 0)''')

    def add_question(self, question: str, answer: str, category: str) -> None:
        with self.get_connection() as conn:
            c = conn.cursor()
            now = datetime.now().date()
            c.execute(
                "INSERT INTO flashcards (question, answer, category, last_reviewed, next_review) VALUES (?, ?, ?, ?, ?)",
                (question, answer, category, now, now))

    def edit_question(self, id: int, question: str, answer: str, category: str) -> None:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE flashcards SET question = ?, answer = ?, category = ? WHERE id = ?",
                      (question, answer, category, id))

    def remove_question(self, id: int) -> None:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM flashcards WHERE id = ?", (id,))

    def get_all_questions(self) -> List[FlashcardRecord]:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM flashcards")
            return c.fetchall()

    def get_due_questions(self) -> List[FlashcardRecord]:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM flashcards WHERE next_review <= date('now') ORDER BY next_review")
            return c.fetchall()

    def update_card_review(self, id: int, ease: int, interval: int, ease_factor: float) -> None:
        with self.get_connection() as conn:
            c = conn.cursor()
            next_review = (datetime.now() + timedelta(days=interval)).date()
            c.execute(
                "UPDATE flashcards SET last_reviewed = ?, next_review = ?, ease_factor = ?, interval = ? WHERE id = ?",
                (datetime.now().date(), next_review, ease_factor, interval, id))

    def get_statistics(self) -> Tuple[int, int, float]:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM flashcards")
            total_cards = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM flashcards WHERE next_review <= date('now')")
            due_cards = c.fetchone()[0]
            c.execute("SELECT AVG(ease_factor) FROM flashcards")
            avg_ease = c.fetchone()[0] or 0.0
            return total_cards, due_cards, avg_ease


class SpacedRepetitionSystem:
    @staticmethod
    def calculate_next_interval(ease: int, prev_interval: int, ease_factor: float) -> Tuple[int, float]:
        if ease == 1:
            interval = 1
        elif ease == 2:
            interval = 6
        else:
            if prev_interval < 1:
                interval = 1
            elif prev_interval == 1:
                interval = 6
            else:
                interval = round(prev_interval * ease_factor)

        if ease == 3:
            ease_factor += 0.1
        elif ease == 0:
            ease_factor -= 0.2

        ease_factor = max(1.3, min(2.5, ease_factor))
        return interval, ease_factor


class FlashcardApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Enhanced Flashcard App")
        self.geometry("600x400")

        self.db_manager = DatabaseManager()
        self.srs = SpacedRepetitionSystem()

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.main_menu()

    def main_menu(self) -> None:
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_frame, text="Enhanced Flashcard App", font=('Helvetica', 24, 'bold')).pack(pady=20)

        ctk.CTkButton(self.main_frame, text="Add Question", command=self.add_question).pack(pady=10, fill=tk.X)
        ctk.CTkButton(self.main_frame, text="View Questions", command=self.view_questions).pack(pady=10, fill=tk.X)
        ctk.CTkButton(self.main_frame, text="Study", command=self.study).pack(pady=10, fill=tk.X)
        ctk.CTkButton(self.main_frame, text="Statistics", command=self.show_statistics).pack(pady=10, fill=tk.X)

    def add_question(self) -> None:
        dialog = ctk.CTkInputDialog(text="Enter the question:", title="Add Question")
        question = dialog.get_input()
        if question:
            dialog = ctk.CTkInputDialog(text="Enter the answer:", title="Add Answer")
            answer = dialog.get_input()
            if answer:
                dialog = ctk.CTkInputDialog(text="Enter the category (optional):", title="Add Category")
                category = dialog.get_input()
                self.db_manager.add_question(question, answer, category)
                messagebox.showinfo("Success", "Question added successfully")

    def view_questions(self) -> None:
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tree = ttk.Treeview(self.main_frame, columns=("ID", "Question", "Answer", "Category"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Question", text="Question")
        tree.heading("Answer", text="Answer")
        tree.heading("Category", text="Category")
        tree.column("ID", width=50)
        tree.column("Question", width=200)
        tree.column("Answer", width=200)
        tree.column("Category", width=100)
        tree.pack(expand=True, fill=tk.BOTH, pady=10)

        questions = self.db_manager.get_all_questions()
        for question in questions:
            tree.insert("", "end", values=(question[0], question[1], question[2], question[3]))

        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ctk.CTkButton(button_frame, text="Edit", command=lambda: self.edit_question(tree)).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="Remove", command=lambda: self.remove_question(tree)).pack(side=tk.LEFT,
                                                                                                    padx=5)
        ctk.CTkButton(button_frame, text="Back", command=self.main_menu).pack(side=tk.RIGHT, padx=5)

    def edit_question(self, tree: ttk.Treeview) -> None:
        selected_item = tree.selection()
        if selected_item:
            question = tree.item(selected_item)['values']
            dialog = ctk.CTkInputDialog(text="Edit the question:", title="Edit Question")
            new_question = dialog.get_input()
            if new_question:
                dialog = ctk.CTkInputDialog(text="Edit the answer:", title="Edit Answer")
                new_answer = dialog.get_input()
                if new_answer:
                    dialog = ctk.CTkInputDialog(text="Edit the category:", title="Edit Category")
                    new_category = dialog.get_input()
                    self.db_manager.edit_question(question[0], new_question, new_answer, new_category)
                    self.view_questions()
        else:
            messagebox.showwarning("Warning", "Please select a question to edit.")

    def remove_question(self, tree: ttk.Treeview) -> None:
        selected_item = tree.selection()
        if selected_item:
            question = tree.item(selected_item)['values']
            if messagebox.askyesno("Confirm", "Are you sure you want to remove this question?"):
                self.db_manager.remove_question(question[0])
                self.view_questions()
        else:
            messagebox.showwarning("Warning", "Please select a question to remove.")

    def study(self) -> None:
        self.due_questions = self.db_manager.get_due_questions()
        if not self.due_questions:
            messagebox.showinfo("No Cards Due", "There are no cards due for review. Great job!")
            return

        self.current_question_index = 0
        self.show_question()

    def show_question(self) -> None:
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        question = self.due_questions[self.current_question_index]
        ctk.CTkLabel(self.main_frame, text=question[1], font=('Helvetica', 18)).pack(pady=20)
        ctk.CTkLabel(self.main_frame, text=f"Category: {question[3]}", font=('Helvetica', 14)).pack(pady=10)

        self.answer_var = tk.StringVar()
        ctk.CTkEntry(self.main_frame, textvariable=self.answer_var, font=('Helvetica', 14), width=300).pack(pady=20)

        ctk.CTkButton(self.main_frame, text="Check Answer", command=self.check_answer).pack(pady=10)
        ctk.CTkButton(self.main_frame, text="Show Answer", command=lambda: self.show_answer(question[2])).pack(pady=10)
        ctk.CTkButton(self.main_frame, text="Back to Main Menu", command=self.main_menu).pack(pady=10)

    def check_answer(self) -> None:
        user_answer = self.answer_var.get().strip().lower()
        correct_answer = self.due_questions[self.current_question_index][2].lower()

        if user_answer == correct_answer:
            messagebox.showinfo("Correct!", "Your answer is correct!")
            self.rate_recall(3)  # Assuming 3 is "Good" recall
        else:
            messagebox.showinfo("Incorrect", f"The correct answer is: {correct_answer}")
            self.rate_recall(1)  # Assuming 1 is "Again" (poor recall)

    def show_answer(self, answer: str) -> None:
        messagebox.showinfo("Answer", f"The correct answer is: {answer}")

    def rate_recall(self, ease: int) -> None:
        question = self.due_questions[self.current_question_index]
        interval, ease_factor = self.srs.calculate_next_interval(ease, question[7], question[6])
        self.db_manager.update_card_review(question[0], ease, interval, ease_factor)

        self.current_question_index += 1
        if self.current_question_index < len(self.due_questions):
            self.show_question()
        else:
            messagebox.showinfo("Study Complete", "You've reviewed all due cards!")
            self.main_menu()

    def show_statistics(self) -> None:
        total_cards, due_cards, avg_ease = self.db_manager.get_statistics()

        stats_window = ctk.CTkToplevel(self)
        stats_window.title("Statistics")
        stats_window.geometry("300x200")

        ctk.CTkLabel(stats_window, text="Flashcard Statistics", font=('Helvetica', 18, 'bold')).pack(pady=20)
        ctk.CTkLabel(stats_window, text=f"Total Cards: {total_cards}").pack(pady=5)
        ctk.CTkLabel(stats_window, text=f"Due Cards: {due_cards}").pack(pady=5)
        ctk.CTkLabel(stats_window, text=f"Average Ease: {avg_ease:.2f}").pack(pady=5)


if __name__ == "__main__":
    app = FlashcardApp()
    app.mainloop()