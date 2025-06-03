from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QLabel, QPushButton, QLineEdit, QStackedWidget
)
from PyQt6.QtCore import Qt

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

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

        self.loginFrame = LoginFrame(self)
        self.registerFrame = RegisterFrame(self)

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
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

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
        self.loginLayout.addWidget(self.loginButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.parent.showInitFrame)
        self.loginLayout.addWidget(self.backButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.loginLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.loginLayout)

class RegisterFrame(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

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
        self.registerLayout.addWidget(self.registerButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.parent.showInitFrame)
        self.registerLayout.addWidget(self.backButton, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.registerLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.registerLayout)