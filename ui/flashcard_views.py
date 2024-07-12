"""
flashcard_views.py

This file contains the FlashcardViews class for displaying, adding, and editing flashcards,
as well as the EditCardDialog class for editing flashcard details.
"""

import tkinter as tk
from tkinter import ttk, messagebox

class FlashcardViews(ttk.Frame):
    """
    A class to represent the different views for managing flashcards.
    """
    
    def __init__(self, parent, controller, mode="view"):
        """
        Initialize the FlashcardViews.

        Parameters:
        - parent (tk.Widget): The parent widget.
        - controller (FlashcardApp): The main application controller.
        - mode (str): The mode of the view ("view", "add", or "edit").
        """
        super().__init__(parent)
        self.controller = controller
        self.mode = mode

        if mode == "view":
            self.create_view_flashcards()
        elif mode == "add":
            self.create_add_flashcard()
        elif mode == "edit":
            self.create_edit_flashcards()

    def create_view_flashcards(self):
        """Create the view for displaying flashcards."""
        tree = ttk.Treeview(self, columns=("Question", "Answer", "Category"), show="headings")
        tree.heading("Question", text="Question")
        tree.heading("Answer", text="Answer")
        tree.heading("Category", text="Category")
        tree.column("Question", width=250)
        tree.column("Answer", width=250)
        tree.column("Category", width=100)
        tree.pack(fill=tk.BOTH, expand=True)

        for card in self.controller.flashcards:
            tree.insert("", tk.END, values=(card[1], card[2], card[3]))

    def create_add_flashcard(self):
        """Create the view for adding a new flashcard."""
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form_frame, text="Add New Flashcard", style="Header.TLabel").pack(pady=(0, 20))

        self.question_entry = self.create_entry(form_frame, "Question:", width=50)
        self.answer_entry = self.create_entry(form_frame, "Answer:", width=50)

        ttk.Label(form_frame, text="Category:").pack(anchor="w", pady=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(form_frame, textvariable=self.category_var, values=[cat['name'] for cat in self.controller.categories])
        self.category_combobox.pack(fill=tk.X, pady=(0, 20))

        # Set default category
        default_category = self.controller.db_manager.get_default_category()
        if default_category:
            self.category_var.set(default_category['name'])

        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="Save", command=self.save_flashcard).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT)

        # Bind Enter key to save_flashcard method
        self.question_entry.bind("<Return>", lambda event: self.answer_entry.focus())
        self.answer_entry.bind("<Return>", lambda event: self.save_flashcard())

    def create_edit_flashcards(self):
        """Create the view for editing existing flashcards."""
        tree = ttk.Treeview(self, columns=("ID", "Question", "Answer", "Category"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Question", text="Question")
        tree.heading("Answer", text="Answer")
        tree.heading("Category", text="Category")
        tree.pack(fill=tk.BOTH, expand=True)

        for card in self.controller.flashcards:
            tree.insert("", tk.END, values=card)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Edit", command=lambda: self.edit_selected(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=lambda: self.delete_selected(tree)).pack(side=tk.LEFT, padx=5)

    def create_entry(self, parent, label_text, width=50):
        """
        Create a labeled entry widget.

        Parameters:
        - parent (tk.Widget): The parent widget.
        - label_text (str): The label text.
        - width (int): The width of the entry.

        Returns:
        - ttk.Entry: The created entry widget.
        """
        ttk.Label(parent, text=label_text).pack(anchor="w", pady=(0, 5))
        entry = ttk.Entry(parent, width=width)
        entry.pack(fill=tk.X, pady=(0, 10))
        return entry

    def save_flashcard(self):
        """Save the new flashcard to the database."""
        question = self.question_entry.get().strip()
        answer = self.answer_entry.get().strip()
        category = self.category_var.get()

        if not (question and answer and category):
            self.controller.show_toast("All fields are required!")
            return

        category_id = next((cat['id'] for cat in self.controller.categories if cat['name'] == category), None)
        if category_id is None:
            self.controller.show_toast("Invalid category selected!")
            return

        new_id = self.controller.db_manager.add_flashcard(question, answer, category_id)
        if new_id:
            self.controller.flashcards.append((new_id, question, answer, category))
            self.controller.show_toast("Flashcard added successfully!")
            self.clear_form()  # Clear the form for the next entry
        else:
            self.controller.show_toast("Failed to add flashcard. Please try again.")

    def clear_form(self):
        """Clear the form for adding a new flashcard."""
        self.question_entry.delete(0, tk.END)
        self.answer_entry.delete(0, tk.END)
        self.question_entry.focus()  # Set focus back to the question entry

    def edit_selected(self, tree):
        """
        Edit the selected flashcard.

        Parameters:
        - tree (ttk.Treeview): The treeview widget displaying the flashcards.
        """
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            EditCardDialog(self, self.controller, item['values'])

    def delete_selected(self, tree):
        """
        Delete the selected flashcard.

        Parameters:
        - tree (ttk.Treeview): The treeview widget displaying the flashcards.
        """
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            card_id = item['values'][0]
            if self.controller.db_manager.delete_flashcard(card_id):
                self.controller.flashcards = [card for card in self.controller.flashcards if card[0] != card_id]
                tree.delete(selected)
                self.controller.show_toast("Flashcard deleted successfully!")
            else:
                self.controller.show_toast("Failed to delete flashcard.")

class EditCardDialog(tk.Toplevel):
    """
    A dialog for editing a flashcard.
    """
    
    def __init__(self, parent, controller, card_data):
        """
        Initialize the EditCardDialog.

        Parameters:
        - parent (tk.Widget): The parent widget.
        - controller (FlashcardApp): The main application controller.
        - card_data (tuple): The flashcard data.
        """
        super().__init__(parent)
        self.controller = controller
        self.card_id, self.question, self.answer, self.category = card_data
        self.title("Edit Flashcard")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for editing the flashcard."""
        self.question_entry = self.create_entry(self, "Question:", self.question)
        self.answer_entry = self.create_entry(self, "Answer:", self.answer)

        ttk.Label(self, text="Category:").pack(pady=(0, 5))
        self.category_var = tk.StringVar(value=self.category)
        self.category_combobox = ttk.Combobox(self, textvariable=self.category_var, values=[cat['name'] for cat in self.controller.categories])
        self.category_combobox.pack(pady=(0, 20), padx=10, fill=tk.X)

        ttk.Button(self, text="Save Changes", command=self.save_changes).pack(pady=(0, 10), padx=10, fill=tk.X)

    def create_entry(self, parent, label_text, value):
        """
        Create a labeled entry widget with a default value.

        Parameters:
        - parent (tk.Widget): The parent widget.
        - label_text (str): The label text.
        - value (str): The default value of the entry.

        Returns:
        - ttk.Entry: The created entry widget.
        """
        ttk.Label(parent, text=label_text).pack(pady=(10, 5))
        entry = ttk.Entry(parent, width=50)
        entry.insert(0, value)
        entry.pack(pady=(0, 10), padx=10, fill=tk.X)
        return entry

    def save_changes(self):
        """Save the changes to the flashcard."""
        new_question = self.question_entry.get().strip()
        new_answer = self.answer_entry.get().strip()
        new_category = self.category_var.get()

        if not (new_question and new_answer and new_category):
            self.controller.show_toast("All fields are required!")
            return

        category_id = next((cat['id'] for cat in self.controller.categories if cat['name'] == new_category), None)
        if category_id is None:
            self.controller.show_toast("Invalid category selected!")
            return

        if self.controller.db_manager.update_flashcard(self.card_id, new_question, new_answer, category_id):
            self.controller.flashcards = [(id, q, a, c) if id != self.card_id else (self.card_id, new_question, new_answer, new_category) for id, q, a, c in self.controller.flashcards]
            self.controller.show_toast("Flashcard updated successfully!")
            self.destroy()
        else:
            self.controller.show_toast("Failed to update flashcard.")
