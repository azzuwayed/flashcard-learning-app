import tkinter as tk
from tkinter import ttk, messagebox

class ProgressView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
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

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Reset Statistics", command=self.reset_statistics).pack(side=tk.LEFT, padx=5)

        self.load_statistics()

    def load_statistics(self):
        self.tree.delete(*self.tree.get_children())
        try:
            statistics = self.controller.db_manager.get_flashcard_statistics()
            for stat in statistics:
                success_rate = f"{(stat['correct'] / stat['total'] * 100):.2f}%" if stat['total'] > 0 else "N/A"
                self.tree.insert("", tk.END, values=(stat['question'], stat['category'], stat['correct'], stat['total'], success_rate))
        except Exception as e:
            self.controller.error_handler.show_error("Failed to load statistics", str(e))

    def reset_statistics(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all statistics? This action cannot be undone."):
            try:
                self.controller.db_manager.reset_statistics()
                self.load_statistics()
                self.controller.show_toast("Statistics reset successfully")
            except Exception as e:
                self.controller.error_handler.show_error("Failed to reset statistics", str(e))