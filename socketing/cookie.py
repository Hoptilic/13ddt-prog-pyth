import os
import time

class CookieManager():
    """
    This class deals with the management of cookies.
    It includes methods for adding (baking), removing (rotten), checking (best before + validity) and saving.
    """
    def __init__(self):
        self.cookies = {}

        # Loads the cookies from the text file if it exists
        if os.path.exists("cookies.txt"):
            with open("cookies.txt", "r") as f:
                for line in f:
                    cookie_id, timeout = line.strip().split(":")
                    self.cookies[cookie_id] = int(timeout)
        else:
            # Initialize the cookie storage
            self.createJar()

    def createJar(self):
        """
        Initializes the cookie storage, creating the text file in the local appdata.
        """
        # Check if the cookie file exists
        if not os.path.exists("cookies.txt"):
            # Create the file
            with open("cookies.txt", "w") as f:
                f.write("")

    def bake(self):
        """
        Creates a cookie with a 24 hour lifetime in unix time.
        """
        import time
        cookie_id = os.urandom(16).hex()
        # Store as unix timestamp (seconds since epoch)
        expires_at = int(time.time()) + 24 * 60 * 60
        self.cookies[cookie_id] = expires_at
        self.saveCookies()
        return cookie_id
    
    def rottenCookie(self, cookie_id):
        """
        Removes a cookie from the storage.
        """
        if cookie_id in self.cookies:
            del self.cookies[cookie_id]
            self.saveCookies()
            return True
        else:
            return False
        
    def checkBestBeforeDate(self, cookie_id):
        """
        Checks if a cookie has expired based on its age - only cookies younger than 24 hours from their creation date are valid.
        """
        import time
        if cookie_id in self.cookies:
            if self.cookies[cookie_id] > int(time.time()):
                return True
            else:
                self.rottenCookie(cookie_id)
                return False

    def freshenCookie(self, cookie_id):
        """
        Refreshes the cookie's expiration time.
        """
        import time
        if cookie_id in self.cookies:
            self.cookies[cookie_id] = int(time.time()) + 24 * 60 * 60
            self.saveCookies()
            return True
        else:
            return False

    def checkCookie(self, cookie_id):
        """
        Checks if a cookie is valid.
        """
        if cookie_id in self.cookies:
            print("Cookie found")
            return True
        else:
            print("Cookie not found")
            return False
        
    def saveCookies(self):
        """
        Saves the cookies to a text file.
        """
        with open("cookies.txt", "w") as f:
            for cookie_id, timeout in self.cookies.items():
                f.write(f"{cookie_id}:{timeout}\n")