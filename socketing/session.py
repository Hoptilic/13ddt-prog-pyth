"""
Session file manager: reads/writes session.txt for current user and cookie.
"""
import os

class SessionFileManager:
    """Manage session.txt for username+cookie (save/load/clear)."""
    def __init__(self, session_file="session.txt"):
        self.sessionFile = session_file
        self.currentUser = None
        self.currentCookie = None
        self.loadSession()

    def saveSession(self, username, cookie):
        with open(self.sessionFile, "w") as f:
            f.write(f"{username}:{cookie}")
        self.currentUser = username
        self.currentCookie = cookie

    def loadSession(self):
        if os.path.exists(self.sessionFile):
            with open(self.sessionFile, "r") as f:
                line = f.read().strip()
                if ":" in line:
                    username, cookie = line.split(":", 1)
                    self.currentUser = username
                    self.currentCookie = cookie
        else:
            self.currentUser = None
            self.currentCookie = None

    def clearSession(self):
        if os.path.exists(self.sessionFile):
            os.remove(self.sessionFile)
        self.currentUser = None
        self.currentCookie = None

    def get_current_user_from_session(self):
        self.loadSession()
        return self.currentUser