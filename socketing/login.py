import hashlib
import os, sys
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.login_manage import LoginDBManager

class Login():
    """
    This class handles the login functionality.
    It includes methods for encrypting and decrypting passwords.
    """
    def __init__(self):
        pass

    def validate(self, password):
        """
        Sanitizes the password by removing leading and trailing whitespace, along with other unwanted characters.
        Only alphanumeric characters and some special characters are allowed.
        """
        # create tjhe regex pattern
        regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#\$%^&*()_+])[A-za-z\d!@#\$%^&*()_+]{8,}$'

        # Remove tails
        password = password.strip()

        if not re.match(regex, password):
            raise ValueError("Password contains invalid characters or does not meet complexity.")
        else:
            return True

    def encrypt(self, password):
        """
        Hashes the password using SHA-256.
        """
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        return salt.hex(), key.hex()
    
    def unencrypt(self, password, salt, key):
        """
        Verifies the password against the stored hash.
        """
        salt = bytes.fromhex(salt)
        key = bytes.fromhex(key)
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        return new_key == key

    def change_password(self, username: str, current_password: str, new_password: str, db_manager: LoginDBManager | None = None) -> bool:
        """
        Change the password for the given user after verifying the current password and validating the new one.
        Returns True on success, False on failure (e.g., wrong current password or DB update failure).
        May raise ValueError for invalid new passwords.
        """
        if db_manager is None:
            db_manager = LoginDBManager()

        # Validate new password strength
        self.validate(new_password)

        # Fetch current creds
        salt = db_manager.retrieve_salt(username)
        key = db_manager.retrieve_key(username)
        if not salt or not key:
            return False

        # Verify current password provided
        if not self.unencrypt(current_password, salt, key):
            return False

        # Hash and store new password
        new_salt, new_key = self.encrypt(new_password)
        return db_manager.update_password(username, new_key, new_salt)

    def delete_account(self, username: str, db_manager: LoginDBManager | None = None) -> bool:
        """
        Delete the specified user account. Returns True if deleted, False otherwise.
        """
        if db_manager is None:
            db_manager = LoginDBManager()
        return db_manager.delete_user(username)
    # def grantCookie(self, cookie_id):
    #     """
    #     Grants a cookie to the user.
    #     Checks if the user already has a cookie - if they do, the cookie is refreshed.
    #     If there is no cookie, a new one is created.
    #     """
    #     # Check if the user already has a cookie
    #     if self.checkCookie(cookie_id):
    #         # Refresh the cookie
    #         self.freshenCookie(cookie_id)
    #     else:
    #         # Create a new cookie
    #         self.createCookie()
        
    #     return True

    # Temporarily use text files until a database is implemented

    # def save_user(self, username, salt, key):
    #     USER_FILE = "users.txt"
    #     with open(USER_FILE, "a") as f:
    #         f.write(f"{username}:{salt}:{key}\n")

    # def load_users(self):
    #     users = {}
    #     USER_FILE = "users.txt"
    #     if os.path.exists(USER_FILE):
    #         with open(USER_FILE, "r") as f:
    #             for line in f:
    #                 parts = line.strip().split(":")
    #                 if len(parts) == 3:
    #                     users[parts[0]] = (parts[1], parts[2])
    #     return users
