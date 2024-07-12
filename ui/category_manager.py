import tkinter as tk
from tkinter import ttk, colorchooser

class CategoryManager(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Category List
        self.tree = ttk.Treeview(self, columns=("Name", "Color"), show="headings")
        self.tree.heading("Name", text="Category Name")
        self.tree.heading("Color", text="Color")
        self.tree.column("Name", width=200)
        self.tree.column("Color", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Add Category", command=self.add_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Category", command=self.edit_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Category", command=self.delete_category).pack(side=tk.LEFT, padx=5)

        self.load_categories()

    def load_categories(self):
        self.tree.delete(*self.tree.get_children())
        categories = self.controller.db_manager.get_all_categories()
        for category in categories:
            self.tree.insert("", "end", values=(category["name"], category["color"]))

    def add_category(self):
        dialog = CategoryDialog(self, "Add Category")
        if dialog.result:
            new_id = self.controller.db_manager.add_category(dialog.result["name"], dialog.result["color"])
            if new_id:
                self.controller.show_toast(f"Category '{dialog.result['name']}' added successfully")
                self.load_categories()
            else:
                self.controller.show_toast("Failed to add category")

    def edit_category(self):
        selected = self.tree.selection()
        if not selected:
            self.controller.show_toast("Please select a category to edit")
            return
        
        item = self.tree.item(selected[0])
        category_name, category_color = item['values']
        category_id = self.controller.db_manager.get_category_id_by_name(category_name)
        
        if not category_id:
            self.controller.show_toast("Category not found")
            return
        
        dialog = CategoryDialog(self, "Edit Category", category_name, category_color)
        if dialog.result:
            success = self.controller.db_manager.update_category(category_id, dialog.result["name"], dialog.result["color"])
            if success:
                self.controller.show_toast(f"Category '{dialog.result['name']}' updated successfully")
                self.load_categories()
            else:
                self.controller.show_toast("Failed to update category")

    def delete_category(self):
        selected = self.tree.selection()
        if not selected:
            self.controller.show_toast("Please select a category to delete")
            return
        
        item = self.tree.item(selected[0])
        category_name = item['values'][0]
        
        if category_name == "Default":
            self.controller.show_toast("Cannot delete the Default category")
            return
        
        category_id = self.controller.db_manager.get_category_id_by_name(category_name)
        if not category_id:
            self.controller.show_toast("Category not found")
            return
        
        if tk.messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the category '{category_name}'? All flashcards in this category will be moved to the Default category."):
            success = self.controller.db_manager.delete_category(category_id)
            if success:
                self.controller.show_toast(f"Category '{category_name}' deleted successfully")
                self.load_categories()
            else:
                self.controller.show_toast("Failed to delete category")
                
class CategoryDialog:
    def __init__(self, parent, title, name="", color="#000000"):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.result = None

        ttk.Label(self.top, text="Category Name:").pack(padx=10, pady=5)
        self.name_entry = ttk.Entry(self.top)
        self.name_entry.insert(0, name)
        self.name_entry.pack(padx=10, pady=5)

        ttk.Label(self.top, text="Category Color:").pack(padx=10, pady=5)
        self.color_button = ttk.Button(self.top, text="Choose Color", command=self.choose_color)
        self.color_button.pack(padx=10, pady=5)

        self.color = color
        self.update_color_button()

        ttk.Button(self.top, text="Save", command=self.save).pack(padx=10, pady=10)

        self.top.transient(parent)
        self.top.grab_set()
        parent.wait_window(self.top)

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.color)[1]
        if color:
            self.color = color
            self.update_color_button()

    def update_color_button(self):
        self.color_button.configure(text=f"Color: {self.color}")

    def save(self):
        name = self.name_entry.get().strip()
        if name:
            self.result = {"name": name, "color": self.color}
            self.top.destroy()
        else:
            tk.messagebox.showwarning("Invalid Input", "Category name cannot be empty.")