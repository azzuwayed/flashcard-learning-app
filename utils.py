import tkinter as tk
from tkinter import messagebox
import logging

def show_toast(root, message, bg_color, scaling_factor=1.0):
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.config(bg=bg_color)
    
    padding = int(10 * scaling_factor)
    font_size = int(12 * scaling_factor)
    
    label = tk.Label(toast, text=message, fg="white", bg=bg_color, padx=padding, pady=padding, font=("Helvetica", font_size))
    label.pack()

    toast.update_idletasks()
    width = toast.winfo_width()
    height = toast.winfo_height()
    
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    
    toast.geometry(f"+{x}+{y}")

    toast.after(3000, toast.destroy)

class ErrorHandler:
    def __init__(self, root):
        self.root = root
        logging.basicConfig(filename='flashcard_app.log', level=logging.ERROR,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def show_error(self, title, message):
        messagebox.showerror(title, message)
        logging.error(f"{title}: {message}")

    def log_error(self, error):
        print(f"Error logged: {error}")
        logging.error(str(error))