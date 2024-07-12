import tkinter as tk
from flashcard_app import FlashcardApp

def main():
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()