import sqlite3

class LoginDBManager():
    '''
    A class to manage the login database, including user authentication and registration.
    '''

    def __init__(self, db_path="./database/login.db"):
        """
        Initializes the LoginDBManager with the path to the SQLite database. Only create the database if it does not exist.
        Table Format:
        username|hashed_password|salt
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        """
        Creates the users table, but only if it does not already exist.
        """

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                hashed_password TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        ''')
        self.connection.commit()

    def register_user(self, username, hashed_password, salt):
        """
        Registers a new user with the given username, hashed password, and salt.
        Returns True if registration is successful, False if the username already exists (integrityerror will trigger if the username already exists).
        """
        try:
            self.cursor.execute('INSERT INTO users (username, hashed_password, salt) VALUES (?, ?, ?)',
                                (username, hashed_password, salt))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, hashed_password):
        """
        Authenticates a user by checking the username and hashed password.
        Returns True if authentication is successful, False otherwise.
        Return false if the username does not exist or the password does not match.
        """
        self.cursor.execute('SELECT hashed_password FROM users WHERE username = ?', (username,))
        row = self.cursor.fetchone()
        if row:
            return row[0] == hashed_password
        return False
    
    def verify_user(self, username):
        """
        Verifies if a user exists in the database.
        Returns True if the user exists, False otherwise.
        """
        self.cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone() is not None
    
    def retrieve_salt(self, username):
        """
        Retrieves the salt for a given username.
        Returns the salt if the user exists, None otherwise.
        """
        self.cursor.execute('SELECT salt FROM users WHERE username = ?', (username,))
        row = self.cursor.fetchone()
        return row[0] if row else None
    
    def retrieve_key(self, username):
        """
        Retrieves the hashed password for a given username.
        Returns the hashed password if the user exists, None otherwise.
        """
        self.cursor.execute('SELECT hashed_password FROM users WHERE username = ?', (username,))
        row = self.cursor.fetchone()
        return row[0] if row else None