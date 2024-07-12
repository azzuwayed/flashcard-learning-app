"""
database_manager.py

This file contains the DatabaseManager class for managing the flashcards application's database.
"""

import sqlite3
import os
import logging

class DatabaseManager:
    """
    A class to manage the SQLite database for the flashcards application.
    """

    def __init__(self, db_file="flashcards.db"):
        """
        Initialize the DatabaseManager with the specified database file.
        
        Parameters:
        - db_file (str): The name of the database file.
        """
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def close(self):
        """Close the SQLite database connection."""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create the necessary tables if they do not exist."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT NOT NULL
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS flashcards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flashcard_id INTEGER,
                    is_correct BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (flashcard_id) REFERENCES flashcards (id)
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")
            raise

    def initialize_default_category(self):
        """Initialize the default category if it does not exist."""
        try:
            self.cursor.execute('SELECT * FROM categories WHERE name = "Default"')
            default_category = self.cursor.fetchone()
            if not default_category:
                self.cursor.execute('INSERT INTO categories (name, color) VALUES (?, ?)', ("Default", "#808080"))
                self.conn.commit()
                logging.info("Default category initialized.")
        except sqlite3.Error as e:
            logging.error(f"Error initializing default category: {e}")
            raise

    def get_default_category(self):
        """Get the default category details."""
        try:
            self.cursor.execute('SELECT id, name, color FROM categories WHERE name = "Default"')
            default_category = self.cursor.fetchone()
            if default_category:
                return {"id": default_category[0], "name": default_category[1], "color": default_category[2]}
            else:
                return None
        except sqlite3.Error as e:
            logging.error(f"Error getting default category: {e}")
            raise

    def add_flashcard(self, question, answer, category_id):
        """
        Add a new flashcard to the database.

        Parameters:
        - question (str): The question text.
        - answer (str): The answer text.
        - category_id (int): The ID of the category.

        Returns:
        - int: The ID of the newly added flashcard.
        """
        try:
            self.cursor.execute('''
                INSERT INTO flashcards (question, answer, category_id)
                VALUES (?, ?, ?)
            ''', (question, answer, category_id))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error adding flashcard: {e}")
            raise

    def get_all_flashcards(self):
        """Retrieve all flashcards from the database."""
        try:
            self.cursor.execute('''
                SELECT f.id, f.question, f.answer, c.name
                FROM flashcards f
                JOIN categories c ON f.category_id = c.id
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving flashcards: {e}")
            raise

    def update_flashcard(self, id, question, answer, category_id):
        """
        Update an existing flashcard in the database.

        Parameters:
        - id (int): The ID of the flashcard.
        - question (str): The updated question text.
        - answer (str): The updated answer text.
        - category_id (int): The updated category ID.

        Returns:
        - bool: True if the flashcard was updated successfully, False otherwise.
        """
        try:
            self.cursor.execute('''
                UPDATE flashcards
                SET question = ?, answer = ?, category_id = ?
                WHERE id = ?
            ''', (question, answer, category_id, id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error updating flashcard: {e}")
            return False

    def delete_flashcard(self, id):
        """
        Delete a flashcard from the database.

        Parameters:
        - id (int): The ID of the flashcard.

        Returns:
        - bool: True if the flashcard was deleted successfully, False otherwise.
        """
        try:
            self.cursor.execute('DELETE FROM flashcards WHERE id = ?', (id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error deleting flashcard: {e}")
            return False

    def add_study_result(self, flashcard_id, is_correct):
        """
        Add a study result to the database.

        Parameters:
        - flashcard_id (int): The ID of the flashcard.
        - is_correct (bool): Whether the user's answer was correct.

        Returns:
        - bool: True if the study result was added successfully, False otherwise.
        """
        try:
            self.cursor.execute('''
                INSERT INTO study_history (flashcard_id, is_correct)
                VALUES (?, ?)
            ''', (flashcard_id, is_correct))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding study result: {e}")
            return False

    def get_study_history(self, flashcard_id):
        """
        Retrieve the study history for a flashcard.

        Parameters:
        - flashcard_id (int): The ID of the flashcard.

        Returns:
        - list: A list of study results.
        """
        try:
            self.cursor.execute('''
                SELECT is_correct FROM study_history
                WHERE flashcard_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (flashcard_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving study history: {e}")
            raise

    def get_all_categories(self):
        """Retrieve all categories from the database."""
        try:
            self.cursor.execute('SELECT id, name, color FROM categories')
            return [{"id": row[0], "name": row[1], "color": row[2]} for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error retrieving categories: {e}")
            raise

    def add_category(self, name, color):
        """
        Add a new category to the database.

        Parameters:
        - name (str): The name of the category.
        - color (str): The color associated with the category.

        Returns:
        - int: The ID of the newly added category.
        """
        try:
            self.cursor.execute('INSERT INTO categories (name, color) VALUES (?, ?)', (name, color))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error adding category: {e}")
            raise

    def get_category_id_by_name(self, category_name):
        """
        Get the ID of a category by its name.

        Parameters:
        - category_name (str): The name of the category.

        Returns:
        - int: The ID of the category.
        """
        try:
            self.cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logging.error(f"Error getting category ID: {e}")
            raise

    def update_category(self, id, name, color):
        """
        Update an existing category in the database.

        Parameters:
        - id (int): The ID of the category.
        - name (str): The updated name of the category.
        - color (str): The updated color of the category.

        Returns:
        - bool: True if the category was updated successfully, False otherwise.
        """
        try:
            self.cursor.execute('UPDATE categories SET name = ?, color = ? WHERE id = ?', (name, color, id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error updating category: {e}")
            return False

    def delete_category(self, id):
        """
        Delete a category from the database.

        Parameters:
        - id (int): The ID of the category.

        Returns:
        - bool: True if the category was deleted successfully, False otherwise.
        """
        try:
            default_category = self.get_default_category()
            if default_category:
                self.cursor.execute('UPDATE flashcards SET category_id = ? WHERE category_id = ?', (default_category['id'], id))
            
            self.cursor.execute('DELETE FROM categories WHERE id = ?', (id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error deleting category: {e}")
            return False

    def get_flashcards_by_categories(self, category_ids):
        """
        Retrieve flashcards by their category IDs.

        Parameters:
        - category_ids (list): A list of category IDs.

        Returns:
        - list: A list of flashcards that belong to the specified categories.
        """
        try:
            placeholders = ','.join(['?' for _ in category_ids])
            query = f'''
                SELECT f.id, f.question, f.answer, c.name, c.color
                FROM flashcards f
                JOIN categories c ON f.category_id = c.id
                WHERE c.id IN ({placeholders})
            '''
            self.cursor.execute(query, category_ids)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving flashcards by categories: {e}")
            raise

    def get_flashcard_statistics(self):
        """
        Retrieve statistics for all flashcards.

        Returns:
        - list: A list of dictionaries containing flashcard statistics.
        """
        try:
            query = '''
                SELECT f.question, c.name as category,
                       SUM(CASE WHEN sh.is_correct THEN 1 ELSE 0 END) as correct,
                       COUNT(sh.id) as total
                FROM flashcards f
                LEFT JOIN study_history sh ON f.id = sh.flashcard_id
                LEFT JOIN categories c ON f.category_id = c.id
                GROUP BY f.id
            '''
            self.cursor.execute(query)
            return [dict(zip(["question", "category", "correct", "total"], row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error retrieving flashcard statistics: {e}")
            raise

    def reset_statistics(self):
        """
        Reset the study history statistics.

        Returns:
        - bool: True if the statistics were reset successfully, False otherwise.
        """
        try:
            self.cursor.execute('DELETE FROM study_history')
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error resetting statistics: {e}")
            return False
