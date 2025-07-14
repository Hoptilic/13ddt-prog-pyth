from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox,
    QLabel, QPushButton, QLineEdit, QStackedWidget
)
import os, sys
from PyQt6.QtCore import Qt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from socketing.login import Login
from socketing.cookie import CookieManager
from socketing.session import SessionFileManager

class LoginPage(QWidget):
    def __init__(self, event_manager=None):
        super().__init__()
        self.event_manager = event_manager
        self.login_manager = Login()
        self.cookie_manager = CookieManager()
        self.session_manager = SessionFileManager()

        self.setWindowTitle("NCAI - Login")
        self.mainLayout = QVBoxLayout()
        self.stackedWidget = QStackedWidget()

        self.initFrame = QWidget()
        self.initLayout = QVBoxLayout()

        self.title = QLabel("Welcome to NCAI")
        self.initLayout.addWidget(self.title)

        self.loginMenuButton = QPushButton("Login")
        self.loginMenuButton.clicked.connect(self.showLoginFrame)
        self.initLayout.addWidget(self.loginMenuButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.registerMenuButton = QPushButton("Register")
        self.registerMenuButton.clicked.connect(self.showRegisterFrame)
        self.initLayout.addWidget(self.registerMenuButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.initLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.initFrame.setLayout(self.initLayout)

        self.loginFrame = LoginFrame(self, self.event_manager, self.login_manager, self.cookie_manager, self.session_manager)
        self.registerFrame = RegisterFrame(self, self.event_manager, self.login_manager, self.cookie_manager, self.session_manager)

        self.stackedWidget.addWidget(self.initFrame)
        self.stackedWidget.addWidget(self.loginFrame)
        self.stackedWidget.addWidget(self.registerFrame)

        self.mainLayout.addWidget(self.stackedWidget)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.mainLayout)
        self.stackedWidget.setCurrentIndex(0)

    def showLoginFrame(self):
        self.stackedWidget.setCurrentIndex(1)

    def showRegisterFrame(self):
        self.stackedWidget.setCurrentIndex(2)

    def showInitFrame(self):
        self.stackedWidget.setCurrentIndex(0)

class LoginFrame(QWidget):
    def __init__(self, parent, event_manager=None, login_manager=None, cookie_manager=None, session_manager=None):
        super().__init__()
        self.parent = parent
        self.event_manager = event_manager
        self.login_manager = login_manager
        self.cookie_manager = cookie_manager
        self.session_manager = session_manager

        self.loginLayout = QVBoxLayout()

        self.loginTitle = QLabel("Login")
        self.loginLayout.addWidget(self.loginTitle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.usernameLabel = QLabel("Username:")
        self.usernameEntry = QLineEdit()
        self.loginLayout.addWidget(self.usernameLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.loginLayout.addWidget(self.usernameEntry, alignment=Qt.AlignmentFlag.AlignCenter)

        self.passwordLabel = QLabel("Password:")
        self.passwordEntry = QLineEdit()
        self.passwordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.loginLayout.addWidget(self.passwordLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.loginLayout.addWidget(self.passwordEntry, alignment=Qt.AlignmentFlag.AlignCenter)

        self.loginButton = QPushButton("Login")
        self.loginButton.clicked.connect(self.login_user)
        self.loginLayout.addWidget(self.loginButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.parent.showInitFrame)
        self.loginLayout.addWidget(self.backButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.loginLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.loginLayout)

    def login_user(self):
        self.cookie_manager.createJar() # Always create the jar, even if the login fails, so that it atleast exists (part of app init)

        username = self.usernameEntry.text()

        if self.login_manager.verify_user(username):
            salt, key = self.login_manager.retrieve_salt(username), self.login_manager.retrieve_key(username)
            try:
                if self.login_manager.unencrypt(self.passwordEntry.text(), salt, key):
                    current_cookie = self.cookie_manager.bake()
                    self.loginButton.setEnabled(False)
                    self.session_manager.save_session(username, current_cookie)
                    if self.event_manager:
                        self.event_manager.login_success.emit(username)
                    QMessageBox.information(self, "Success", "Login successful! Session started.")
                else:
                    QMessageBox.critical(self, "Error", "Incorrect password.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        else:
            QMessageBox.critical(self, "Error", "User not found.")


        # users = self.login_manager.load_users()
        # self.cookie_manager.createJar()

        # username = self.usernameEntry.text()
        # if username in users:
        #     salt, key = users[username]
        #     try:
        #         if self.login_manager.unencrypt(self.passwordEntry.text(), salt, key):
        #             current_cookie = self.cookie_manager.bake()
        #             self.loginButton.setEnabled(False)
        #             self.session_manager.save_session(username, current_cookie)
        #             if self.event_manager:
        #                 self.event_manager.login_success.emit(username)
        #             QMessageBox.information(self, "Success", "Login successful! Session started.")
        #         else:
        #             QMessageBox.critical(self, "Error", "Incorrect password.")
        #     except Exception as e:
        #         QMessageBox.critical(self, "Error", str(e))
        # else:
        #     QMessageBox.critical(self, "Error", "User not found.")

class RegisterFrame(QWidget):
    def __init__(self, parent, event_manager=None, login_manager=None, cookie_manager=None, session_manager=None):
        super().__init__()
        self.parent = parent
        self.event_manager = event_manager
        self.login_manager = login_manager
        self.cookie_manager = cookie_manager
        self.session_manager = session_manager

        self.registerLayout = QVBoxLayout()

        self.registerTitle = QLabel("Register")
        self.registerLayout.addWidget(self.registerTitle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.usernameLabel = QLabel("Username:")
        self.usernameEntry = QLineEdit()
        self.registerLayout.addWidget(self.usernameLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.registerLayout.addWidget(self.usernameEntry, alignment=Qt.AlignmentFlag.AlignCenter)

        self.passwordLabel = QLabel("Password:")
        self.passwordEntry = QLineEdit()
        self.passwordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.registerLayout.addWidget(self.passwordLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.registerLayout.addWidget(self.passwordEntry, alignment=Qt.AlignmentFlag.AlignCenter)

        self.registerButton = QPushButton("Register")
        self.registerButton.clicked.connect(self.register_user)
        self.registerLayout.addWidget(self.registerButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.parent.showInitFrame)
        self.registerLayout.addWidget(self.backButton, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.registerLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.registerLayout)

    def register_user(self):
        self.cookie_manager.createJar() # Always create the jar, even if the login fails, so that it atleast exists (part of app init)

        username = self.usernameEntry.text()

        if self.login_manager.verify_user(username):
            QMessageBox.critical(self, "Error", "User already exists.")
            return
                    
        try:
            if self.login_manager.validate(self.passwordEntry.text()):
                salt, key = self.login_manager.encrypt(self.passwordEntry.text())
                if self.login_manager.register_user(username, key, salt):
                    QMessageBox.information(self, "Success", "User registered successfully!")
                    self.parent.showLoginFrame()
                else:
                    QMessageBox.critical(self, "Error", "Failed to register user.")
            else:
                QMessageBox.critical(self, "Error", "Password does not meet complexity requirements.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        # users = self.login_manager.load_users()
        # self.cookie_manager.createJar()

        # username = self.usernameEntry.text()
        # if username in users:
        #     QMessageBox.critical(self, "Error", "User already exists.")
        #     return
        # try:
        #     if self.login_manager.validate(self.passwordEntry.text()):
        #         salt, key = self.login_manager.encrypt(self.passwordEntry.text())
        #         self.login_manager.save_user(username, salt, key)
        #         QMessageBox.information(self, "Success", "User registered!")
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", str(e))