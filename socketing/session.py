import os

class SessionManager:
    """
    Handles only the session.txt file: saving, loading, and clearing the current session (username and cookie).
    """
    def __init__(self, session_file="session.txt"):
        self.session_file = session_file
        self.current_user = None
        self.current_cookie = None
        self.load_session()

    def save_session(self, username, cookie):
        with open(self.session_file, "w") as f:
            f.write(f"{username}:{cookie}")
        self.current_user = username
        self.current_cookie = cookie

    def load_session(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, "r") as f:
                line = f.read().strip()
                if ":" in line:
                    username, cookie = line.split(":", 1)
                    self.current_user = username
                    self.current_cookie = cookie
        else:
            self.current_user = None
            self.current_cookie = None

    def clear_session(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
        self.current_user = None
        self.current_cookie = None

    def get_current_user_from_session(self):
        self.load_session()
        return self.current_user