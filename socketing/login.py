import hashlib
import os
import re

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
    
class CookieManager():
    """
    This class handles the management of cookies.
    It includes methods for adding, removing, and checking cookies.
    """
    def __init__(self):
        self.cookies = {}

    def initCookieStorage(self):
        """
        Initializes the cookie storage, creating the text file in the local appdata.
        """
        # Check if the cookie file exists
        if not os.path.exists("cookies.txt"):
            # Create the file
            with open("cookies.txt", "w") as f:
                f.write("")

    def createCookie(self):
        """
        Creates a cookie with a 24 hour lifetime.
        """
        # Generate a unique cookie ID
        cookie_id = os.urandom(16).hex()
        # Give the cookie a 24 hour best-before date in seconds
        self.cookies[cookie_id] = 24 * 60 * 60
        return cookie_id
    
    def rottenCookie(self, cookie_id):
        """
        Removes a cookie from the storage.
        """
        if cookie_id in self.cookies:
            del self.cookies[cookie_id]
            return True
        else:
            return False
        
    def checkBestBeforeDate(self, cookie_id):
        """
        Checks if a cookie has expired based on it's age - only cookies younger than 24 hours are valid.
        """
        if cookie_id in self.cookies:
            if self.cookies[cookie_id] > 24 * 60 * 60:
                return True
            else:
                self.rottenCookie(cookie_id)
                return False

    def freshenCookie(self, cookie_id):
        """
        Refreshes the cookie's expiration time.
        """
        if cookie_id in self.cookies:
            self.cookies[cookie_id] = 24 * 60 * 60
            return True
        else:
            return False

    def checkCookie(self, cookie_id):
        """
        Checks if a cookie is valid.
        """
        if cookie_id in self.cookies:
            return True
        else:
            return False
        
    def saveCookies(self):
        """
        Saves the cookies to a text file.
        """
        with open("cookies.txt", "w") as f:
            for cookie_id, timeout in self.cookies.items():
                f.write(f"{cookie_id}:{timeout}\n")