"""
utils.py

This file contains utility functions and classes for the flashcards application.
"""

import tkinter as tk
from tkinter import messagebox
import logging
import os

def show_toast(root, message, bg_color, scaling_factor=1.0):
    """
    Display a temporary toast message on the screen.

    Parameters:
    - root (tk.Tk): The root window.
    - message (str): The message to display.
    - bg_color (str): The background color of the toast.
    - scaling_factor (float): The scaling factor for the padding and font size.
    """
    if not message or not isinstance(message, str):
        raise ValueError("Message must be a non-empty string.")
    
    if not isinstance(bg_color, str) or not bg_color.startswith("#"):
        raise ValueError("Background color must be a valid hex color code.")
    
    if not (0.5 <= scaling_factor <= 2.0):
        raise ValueError("Scaling factor must be between 0.5 and 2.0.")

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
    """
    A class to handle and log errors in the flashcards application.
    """
    
    def __init__(self, root):
        """
        Initialize the error handler.

        Parameters:
        - root (tk.Tk): The root window.
        """
        self.root = root
        log_level = os.getenv("FLASHCARDS_LOG_LEVEL", "ERROR").upper()
        logging.basicConfig(filename='flashcard_app.log', level=log_level,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def show_error(self, title, message):
        """
        Show an error message dialog and log the error.

        Parameters:
        - title (str): The title of the error message.
        - message (str): The error message.
        """
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string.")
        
        if not message or not isinstance(message, str):
            raise ValueError("Message must be a non-empty string.")
        
        messagebox.showerror(title, message)
        logging.error(f"{title}: {message}")

    def log_error(self, error):
        """
        Log an error message.

        Parameters:
        - error (Exception): The error to log.
        """
        if not isinstance(error, Exception):
            raise ValueError("Error must be an instance of Exception.")
        
        print(f"Error logged: {error}")
        logging.error(str(error))