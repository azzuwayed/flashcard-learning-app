"""
flashcard_app.py

This file contains the FlashcardApp class which is the main application class for the flashcards application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database_manager import DatabaseManager
from settings_manager import SettingsManager
from ui.main_menu import MainMenu
from ui.flashcard_views import FlashcardViews
from ui.study_session import StudySession, PreStudyOptionsDialog
from ui.settings_view import SettingsView
from ui.progress_view import ProgressView
from ui.category_manager import CategoryManager
from utils import show_toast, ErrorHandler
import logging

class FlashcardApp:
    """
    The main application class for the flashcards application.
    """

    def __init__(self, root):
        """
        Initialize the FlashcardApp.

        Parameters:
        - root (tk.Tk): The root window of the application.
        """
        self.root = root
        self.root.title("Flashcard Learning App")
        
        self.db_manager = DatabaseManager()
        self.settings_manager = SettingsManager()
        self.error_handler = ErrorHandler(self.root)
        
        self.db_manager.initialize_default_category()
        
        self.flashcards = []
        self.categories = []
        self.load_data()

        self.apply_settings()
        self.create_widgets()

    def apply_settings(self):
        """Apply settings from the SettingsManager to the application."""
        self.scaling_factor = self.settings_manager.get("scaling_factor")
        self.root.tk.call('tk', 'scaling', self.scaling_factor)
        
        base_width, base_height = 800, 600
        scaled_width = int(base_width * self.scaling_factor)
        scaled_height = int(base_height * self.scaling_factor)
        self.root.geometry(f"{scaled_width}x{scaled_height}")
        
        self.style = ttk.Style()
        self.set_theme()

    def set_theme(self):
        """Set the theme based on the current settings."""
        theme = self.settings_manager.get_current_theme()
        
        self.style.theme_use("clam")
        
        colors = theme["colors"]
        fonts = theme["fonts"]
        styles = theme["styles"]

        main_font_size = int(fonts["main"]["size"] * self.scaling_factor)
        header_font_size = int(fonts["header"]["size"] * self.scaling_factor)

        main_font = (fonts["main"]["family"], main_font_size)
        header_font = (fonts["header"]["family"], header_font_size, fonts["header"]["weight"])

        self.style.configure(".", font=main_font, background=colors["background"])
        self.style.configure("TFrame", background=colors["background"])
        self.style.configure("TLabel", background=colors["background"], foreground=colors["foreground"], font=main_font)
        self.style.configure("Header.TLabel", font=header_font)
        self.style.configure("TButton", 
                            background=colors["button"], 
                            foreground=colors["button_text"],
                            font=(fonts["main"]["family"], main_font_size, "bold"),
                            padding=int(styles["button"]["padding"] * self.scaling_factor))
        self.style.map("TButton", 
                       background=[("active", colors["accent"])],
                       foreground=[("active", colors["background"])])
        entry_height = int(30 * self.scaling_factor)
        self.style.configure("TEntry", 
                            fieldbackground=colors["background"], 
                            foreground=colors["foreground"],
                            borderwidth=styles["entry"]["borderwidth"],
                            font=main_font,
                            height=entry_height)
        self.style.configure("TCombobox", 
                            fieldbackground=colors["background"], 
                            foreground=colors["foreground"],
                            borderwidth=styles["entry"]["borderwidth"],
                            font=main_font,
                            height=entry_height)
        self.style.configure("Treeview", 
                            background=styles["treeview"]["background"],
                            fieldbackground=styles["treeview"]["fieldbackground"], 
                            foreground=colors["foreground"],
                            font=main_font,
                            rowheight=int(styles["treeview"]["rowheight"] * self.scaling_factor))
        self.style.configure("Treeview.Heading", 
                            background=colors["button"], 
                            foreground=colors["button_text"],
                            font=(fonts["main"]["family"], main_font_size, "bold"))
        self.style.configure("Vertical.TScrollbar", background=colors["button"], troughcolor=colors["background"])
        self.style.configure("Horizontal.TScrollbar", background=colors["button"], troughcolor=colors["background"])
        self.style.configure("TProgressbar", background=colors["accent"], troughcolor=colors["background"])
        
        self.root.configure(bg=colors["background"])
        
        self.root.update_idletasks()
        self.root.update()

    def load_data(self):
        """Load flashcards and categories from the database."""
        try:
            self.flashcards = self.db_manager.get_all_flashcards()
            self.categories = self.db_manager.get_all_categories()
        except Exception as e:
            self.error_handler.show_error("Failed to load data", str(e))
            logging.error(f"Failed to load data: {e}")

    def create_widgets(self):
        """Create the main widgets for the application."""
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.content_frame = ttk.Frame(self.main_frame, padding="20")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.create_header()
        self.show_main_menu()

    def create_header(self):
        """Create the header widgets for the application."""
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))

        self.back_button = ttk.Button(self.header_frame, text="← Back", command=self.go_back, style="Header.TButton")
        self.back_button.pack(side=tk.LEFT)
        self.back_button.pack_forget()

        self.title_label = ttk.Label(self.header_frame, text="Flashcard App", style="Header.TLabel")
        self.title_label.pack(side=tk.LEFT, padx=20)

    def go_back(self):
        """Handle the back button click event."""
        self.show_main_menu()

    def show_main_menu(self):
        """Show the main menu view."""
        self.clear_content()
        self.back_button.pack_forget()
        self.title_label.config(text="Flashcard App")
        MainMenu(self.content_frame, self).pack(fill=tk.BOTH, expand=True)

    def clear_content(self):
        """Clear the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_settings(self):
        """Show the settings view."""
        self.clear_content()
        self.back_button.pack(side=tk.LEFT)
        self.title_label.config(text="Settings")
        SettingsView(self.content_frame, self.settings_manager, self.apply_settings, self.show_toast).pack(fill=tk.BOTH, expand=True)
        self.set_theme()

    def show_toast(self, message):
        """
        Show a toast message.

        Parameters:
        - message (str): The message to display.
        """
        show_toast(self.root, message, self.settings_manager.get_current_theme()["colors"]["accent"], self.scaling_factor)

    def view_flashcards(self):
        """Show the view flashcards view."""
        self.clear_content()
        self.back_button.pack(side=tk.LEFT)
        self.title_label.config(text="View Flashcards")
        FlashcardViews(self.content_frame, self).pack(fill=tk.BOTH, expand=True)

    def add_flashcard(self):
        """Show the add flashcard view."""
        self.clear_content()
        self.back_button.pack(side=tk.LEFT)
        self.title_label.config(text="Add Flashcard")
        FlashcardViews(self.content_frame, self, mode="add").pack(fill=tk.BOTH, expand=True)

    def edit_flashcards(self):
        """Show the edit flashcards view."""
        self.clear_content()
        self.back_button.pack(side=tk.LEFT)
        self.title_label.config(text="Edit Flashcards")
        FlashcardViews(self.content_frame, self, mode="edit").pack(fill=tk.BOTH, expand=True)

    def start_study_session(self):
        """Start a study session."""
        if not self.flashcards:
            self.show_toast("No flashcards available. Please add some flashcards before starting a study session.")
            return

        options = PreStudyOptionsDialog(self.root, self.categories).show()
        if options:
            self.clear_content()
            self.back_button.pack(side=tk.LEFT)
            self.title_label.config(text="Study Session")
            study_session = StudySession(self.content_frame, self, options)
            study_session.pack(fill=tk.BOTH, expand=True)
            
            if not study_session.study_deck:
                self.show_toast("No flashcards available for the selected categories.")

    def manage_categories(self):
        """Show the manage categories view."""
        self.clear_content()
        self.back_button.pack(side=tk.LEFT)
        self.title_label.config(text="Manage Categories")
        CategoryManager(self.content_frame, self).pack(fill=tk.BOTH, expand=True)

    def view_progress(self):
        """Show the view progress view."""
        self.clear_content()
        self.back_button.pack(side=tk.LEFT)
        self.title_label.config(text="View Progress")
        ProgressView(self.content_frame, self).pack(fill=tk.BOTH, expand=True)

    def __del__(self):
        """Destructor to ensure database connection is closed."""
        self.db_manager.close()

    def quit_app(self):
        """Quit the application."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit the application?"):
            self.db_manager.close()
            self.root.quit()
            self.root.destroy()
