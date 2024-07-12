import tkinter as tk
from flashcard_app import FlashcardApp
import os
os.environ['PYTHONUTF8'] = '1'

def main():
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()