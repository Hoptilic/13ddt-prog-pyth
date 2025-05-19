import tkinter as tk
from tkinter import messagebox
import os
from socketing.login import Login
from socketing.cookie import CookieManager

USER_FILE = "users.txt"
SESSION_FILE = "session.txt"

def save_user(username, salt, key):
    with open(USER_FILE, "a") as f:
        f.write(f"{username}:{salt}:{key}\n")

def load_users():
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) == 3:
                    users[parts[0]] = (parts[1], parts[2])
    return users

def save_session(username, cookie):
    with open(SESSION_FILE, "w") as f:
        f.write(f"{username}:{cookie}")

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            line = f.read().strip()
            if ":" in line:
                username, cookie = line.split(":", 1)
                return username, cookie
    return None, None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login GUI")
        self.login = Login()
        self.users = load_users()
        self.cookie_manager = CookieManager()
        self.cookie_manager.createJar()
        self.current_cookie = None
        self.current_user = None

        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        tk.Label(self.frame, text="Username:").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.frame, text="Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.grid(row=1, column=1)

        self.login_btn = tk.Button(self.frame, text="Login", command=self.login_user)
        self.login_btn.grid(row=2, column=0, pady=5)

        self.register_btn = tk.Button(self.frame, text="Register", command=self.register_user)
        self.register_btn.grid(row=2, column=1, pady=5)

        self.logout_btn = tk.Button(self.frame, text="Logout", command=self.logout_user, state=tk.DISABLED)
        self.logout_btn.grid(row=3, column=0, columnspan=2, pady=5)

        self.status_label = tk.Label(self.frame, text="Not logged in.")
        self.status_label.grid(row=4, column=0, columnspan=2)

        # Try auto-login with cookie/session
        self.auto_login_with_cookie()

    def auto_login_with_cookie(self):
        username, cookie = load_session()
        if username and cookie:
            print(f"[DEBUG] Attempting auto-login with username={username}, cookie={cookie}")
            print(f"[DEBUG] Current cookies: {self.cookie_manager.cookies}")
            if self.cookie_manager.checkCookie(cookie):
                self.current_user = username
                self.current_cookie = cookie
                self.status_label.config(text=f"Logged in as {username}\nSession: {cookie}")
                self.logout_btn.config(state=tk.NORMAL)
                self.login_btn.config(state=tk.DISABLED)
                self.register_btn.config(state=tk.DISABLED)
                messagebox.showinfo("Welcome back", f"Auto-logged in as {username}!")
            else:
                print(f"[DEBUG] Cookie {cookie} not found or invalid.")
        else:
            print("[DEBUG] No session file or session data found.")

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username in self.users:
            salt, key = self.users[username]
            try:
                if self.login.unencrypt(password, salt, key):
                    # Session/cookie management
                    self.current_cookie = self.cookie_manager.bake()
                    self.current_user = username
                    save_session(username, self.current_cookie)
                    self.status_label.config(text=f"Logged in as {username}\nSession: {self.current_cookie}")
                    self.logout_btn.config(state=tk.NORMAL)
                    self.login_btn.config(state=tk.DISABLED)
                    self.register_btn.config(state=tk.DISABLED)
                    messagebox.showinfo("Success", "Login successful! Session started.")
                else:
                    messagebox.showerror("Error", "Incorrect password.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "User not found.")

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username in self.users:
            messagebox.showerror("Error", "User already exists.")
            return
        try:
            if self.login.validate(password):
                salt, key = self.login.encrypt(password)
                save_user(username, salt, key)
                self.users = load_users()
                messagebox.showinfo("Success", "User registered!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def logout_user(self):
        if self.current_cookie:
            self.cookie_manager.rottenCookie(self.current_cookie)
            clear_session()
            self.current_cookie = None
            self.current_user = None
            self.status_label.config(text="Not logged in.")
            self.logout_btn.config(state=tk.DISABLED)
            self.login_btn.config(state=tk.NORMAL)
            self.register_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Logged out", "Session ended and cookie removed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()