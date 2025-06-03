from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
import sys
import os
from socketing.login import Login
from socketing.cookie import CookieManager
from socketing.session import SessionManager

session_manager = SessionManager()

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login GUI")
        self.login = Login()
        self.users = self.login.load_users()
        self.cookie_manager = CookieManager()
        self.cookie_manager.createJar()
        self.current_cookie = None
        self.current_user = None
        self.session_manager = session_manager
        self.init_ui()
        self.auto_login_with_cookie()

    def init_ui(self):
        layout = QVBoxLayout()
        user_layout = QHBoxLayout()
        pass_layout = QHBoxLayout()
        btn_layout = QHBoxLayout()

        self.username_label = QLabel("Username:")
        self.username_entry = QLineEdit()
        user_layout.addWidget(self.username_label)
        user_layout.addWidget(self.username_entry)

        self.password_label = QLabel("Password:")
        self.password_entry = QLineEdit()
        pass_layout.addWidget(self.password_label)
        pass_layout.addWidget(self.password_entry)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login_user)
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register_user)
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout_user)
        self.logout_btn.setEnabled(False)
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.register_btn)
        btn_layout.addWidget(self.logout_btn)

        self.status_label = QLabel("Not logged in.")

        layout.addLayout(user_layout)
        layout.addLayout(pass_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def auto_login_with_cookie(self):
        username = self.session_manager.current_user
        cookie = self.session_manager.current_cookie
        if username and cookie:
            print(f"[DEBUG] Attempting auto-login with username={username}, cookie={cookie}")
            print(f"[DEBUG] Current cookies: {self.cookie_manager.cookies}")
            if self.cookie_manager.checkCookie(cookie):
                self.current_user = username
                self.current_cookie = cookie
                self.status_label.setText(f"Logged in as {username}\nSession: {cookie}")
                self.logout_btn.setEnabled(True)
                self.login_btn.setEnabled(False)
                self.register_btn.setEnabled(False)
                QMessageBox.information(self, "Welcome back", f"Auto-logged in as {username}!")
            else:
                print(f"[DEBUG] Cookie {cookie} not found or invalid.")
        else:
            print("[DEBUG] No session file or session data found.")

    def login_user(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        if username in self.users:
            salt, key = self.users[username]
            try:
                if self.login.unencrypt(password, salt, key):
                    self.current_cookie = self.cookie_manager.bake()
                    self.current_user = username
                    self.session_manager.save_session(username, self.current_cookie)
                    self.status_label.setText(f"Logged in as {username}\nSession: {self.current_cookie}")
                    self.logout_btn.setEnabled(True)
                    self.login_btn.setEnabled(False)
                    self.register_btn.setEnabled(False)
                    QMessageBox.information(self, "Success", "Login successful! Session started.")
                else:
                    QMessageBox.critical(self, "Error", "Incorrect password.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        else:
            QMessageBox.critical(self, "Error", "User not found.")

    def register_user(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        if username in self.users:
            QMessageBox.critical(self, "Error", "User already exists.")
            return
        try:
            if self.login.validate(password):
                salt, key = self.login.encrypt(password)
                self.login.save_user(username, salt, key)
                self.users = self.login.load_users()
                QMessageBox.information(self, "Success", "User registered!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def logout_user(self):
        if self.current_cookie:
            self.cookie_manager.rottenCookie(self.current_cookie)
            self.session_manager.clear_session()
            self.current_cookie = None
            self.current_user = None
            self.status_label.setText("Not logged in.")
            self.logout_btn.setEnabled(False)
            self.login_btn.setEnabled(True)
            self.register_btn.setEnabled(True)
            QMessageBox.information(self, "Logged out", "Session ended and cookie removed.")


app = QApplication(sys.argv)
window = LoginApp()
window.show()
sys.exit(app.exec())
