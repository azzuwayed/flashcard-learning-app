import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_file="flashcards.db"):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def close(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
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
            print(f"Error creating tables: {e}")

    def initialize_default_category(self):
        try:
            self.cursor.execute('SELECT * FROM categories WHERE name = "Default"')
            default_category = self.cursor.fetchone()
            if not default_category:
                self.cursor.execute('INSERT INTO categories (name, color) VALUES (?, ?)', ("Default", "#808080"))
                self.conn.commit()
                print("Default category initialized.")
            else:
                print("Default category already exists.")
        except sqlite3.Error as e:
            print(f"Error initializing default category: {e}")

    def get_default_category(self):
        try:
            self.cursor.execute('SELECT id, name, color FROM categories WHERE name = "Default"')
            default_category = self.cursor.fetchone()
            if default_category:
                return {"id": default_category[0], "name": default_category[1], "color": default_category[2]}
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error getting default category: {e}")
            return None

    def add_flashcard(self, question, answer, category_id):
        try:
            self.cursor.execute('''
                INSERT INTO flashcards (question, answer, category_id)
                VALUES (?, ?, ?)
            ''', (question, answer, category_id))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding flashcard: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def get_all_flashcards(self):
        try:
            self.cursor.execute('''
                SELECT f.id, f.question, f.answer, c.name
                FROM flashcards f
                JOIN categories c ON f.category_id = c.id
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving flashcards: {e}")
            return []

    def update_flashcard(self, id, question, answer, category_id):
        try:
            self.cursor.execute('''
                UPDATE flashcards
                SET question = ?, answer = ?, category_id = ?
                WHERE id = ?
            ''', (question, answer, category_id, id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating flashcard: {e}")
            return False

    def delete_flashcard(self, id):
        try:
            self.cursor.execute('DELETE FROM flashcards WHERE id = ?', (id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting flashcard: {e}")
            return False

    def add_study_result(self, flashcard_id, is_correct):
        try:
            self.cursor.execute('''
                INSERT INTO study_history (flashcard_id, is_correct)
                VALUES (?, ?)
            ''', (flashcard_id, is_correct))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding study result: {e}")
            return False

    def get_study_history(self, flashcard_id):
        try:
            self.cursor.execute('''
                SELECT is_correct FROM study_history
                WHERE flashcard_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (flashcard_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving study history: {e}")
            return []

    def get_all_categories(self):
        try:
            self.cursor.execute('SELECT id, name, color FROM categories')
            return [{"id": row[0], "name": row[1], "color": row[2]} for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving categories: {e}")
            return []

    def add_category(self, name, color):
        try:
            self.cursor.execute('INSERT INTO categories (name, color) VALUES (?, ?)', (name, color))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding category: {e}")
            return None

    def update_category(self, id, name, color):
        try:
            self.cursor.execute('UPDATE categories SET name = ?, color = ? WHERE id = ?', (name, color, id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating category: {e}")
            return False

    def delete_category(self, id):
        try:
            self.cursor.execute('DELETE FROM categories WHERE id = ?', (id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting category: {e}")
            return False

    def get_flashcards_by_categories(self, category_ids):
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
            print(f"Error retrieving flashcards by categories: {e}")
            return []

    def get_flashcard_statistics(self):
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
            print(f"Error retrieving flashcard statistics: {e}")
            return []

    def reset_statistics(self):
        try:
            self.cursor.execute('DELETE FROM study_history')
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error resetting statistics: {e}")
            return False