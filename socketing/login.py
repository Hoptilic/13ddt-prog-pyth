import hashlib
import os, sys
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    
    def grantCookie(self, cookie_id):
        """
        Grants a cookie to the user.
        Checks if the user already has a cookie - if they do, the cookie is refreshed.
        If there is no cookie, a new one is created.
        """
        # Check if the user already has a cookie
        if self.checkCookie(cookie_id):
            # Refresh the cookie
            self.freshenCookie(cookie_id)
        else:
            # Create a new cookie
            self.createCookie()
        
        return True

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