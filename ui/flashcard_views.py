import tkinter as tk
from tkinter import ttk

class FlashcardViews(ttk.Frame):
    def __init__(self, parent, controller, mode="view"):
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
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form_frame, text="Add New Flashcard", style="Header.TLabel").pack(pady=(0, 20))

        ttk.Label(form_frame, text="Question:").pack(anchor="w", pady=(0, 5))
        self.question_entry = ttk.Entry(form_frame, width=50)
        self.question_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form_frame, text="Answer:").pack(anchor="w", pady=(0, 5))
        self.answer_entry = ttk.Entry(form_frame, width=50)
        self.answer_entry.pack(fill=tk.X, pady=(0, 10))

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

    def save_flashcard(self):
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
        self.question_entry.delete(0, tk.END)
        self.answer_entry.delete(0, tk.END)
        self.question_entry.focus()  # Set focus back to the question entry

    def create_edit_flashcards(self):
        tree = ttk.Treeview(self, columns=("ID", "Question", "Answer", "Category"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Question", text="Question")
        tree.heading("Answer", text="Answer")
        tree.heading("Category", text="Category")
        tree.pack(fill=tk.BOTH, expand=True)

        for card in self.controller.flashcards:
            tree.insert("", tk.END, values=card)

        def edit_selected():
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                EditCardDialog(self, self.controller, item['values'])

        def delete_selected():
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

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Edit", command=edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_selected).pack(side=tk.LEFT, padx=5)

class EditCardDialog(tk.Toplevel):
    def __init__(self, parent, controller, card_data):
        super().__init__(parent)
        self.controller = controller
        self.card_id, self.question, self.answer, self.category = card_data
        self.title("Edit Flashcard")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Question:").pack(pady=(10, 5))
        self.question_entry = ttk.Entry(self, width=50)
        self.question_entry.insert(0, self.question)
        self.question_entry.pack(pady=(0, 10), padx=10, fill=tk.X)

        ttk.Label(self, text="Answer:").pack(pady=(0, 5))
        self.answer_entry = ttk.Entry(self, width=50)
        self.answer_entry.insert(0, self.answer)
        self.answer_entry.pack(pady=(0, 10), padx=10, fill=tk.X)

        ttk.Label(self, text="Category:").pack(pady=(0, 5))
        self.category_var = tk.StringVar(value=self.category)
        self.category_combobox = ttk.Combobox(self, textvariable=self.category_var, values=[cat['name'] for cat in self.controller.categories])
        self.category_combobox.pack(pady=(0, 20), padx=10, fill=tk.X)

        ttk.Button(self, text="Save Changes", command=self.save_changes).pack(pady=(0, 10), padx=10, fill=tk.X)

    def save_changes(self):
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