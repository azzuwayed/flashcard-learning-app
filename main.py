"""
main.py

This file initializes and runs the FlashcardApp.
"""

import tkinter as tk
from flashcard_app import FlashcardApp
import os
import logging

# Ensure UTF-8 encoding is used
os.environ['PYTHONUTF8'] = '1'

def main():
    """
    The main function to initialize and run the FlashcardApp.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        root = tk.Tk()
        app = FlashcardApp(root)
        logging.info("FlashcardApp initialized successfully.")
        root.mainloop()
    except Exception as e:
        logging.error(f"An error occurred while running the application: {e}")
        raise

if __name__ == "__main__":
    main()
