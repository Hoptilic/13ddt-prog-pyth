from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QLabel, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NCAI - Login")
        
        self.mainLayout = QVBoxLayout()
        
        #/ Create the layout for the initial selection
        self.initFrame = QWidget()
        self.initLayout = QVBoxLayout()

        self.title = QLabel("Welcome to NCAI")
        self.initLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.loginMenuButton = QPushButton("Login")
        self.loginMenuButton.clicked.connect(self.loginButtonEvent)
        self.initLayout.addWidget(self.loginMenuButton)

        self.registerMenuButton = QPushButton("Register")
        self.registerMenuButton.clicked.connect(self.registerButtonEvent)
        self.initLayout.addWidget(self.registerMenuButton)

        self.initFrame.setLayout(self.initLayout)
        self.mainLayout.addWidget(self.initFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        # Set the layout at the end to avoid issues with the layout not being set
        self.setLayout(self.mainLayout)

    def loginButtonEvent(self):
        """
        Event handler for the login button.
        """
        self.loginFrame = loginFrame()
        self.mainLayout.addWidget(self.loginFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.initFrame.hide()

    def registerButtonEvent(self):
        """
        Event handler for the register button.
        """
        self.registerFrame = registerFrame()
        self.mainLayout.addWidget(self.registerFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.initFrame.hide()

class loginFrame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI - Login")

        self.loginFrame = QWidget()
        self.loginLayout = QVBoxLayout()

        self.loginTitle = QLabel("Login")
        self.loginLayout.addWidget(self.loginTitle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.usernameLabel = QLabel("Username:")
        self.usernameEntry = QLineEdit()
        self.loginLayout.addWidget(self.usernameLabel)
        self.loginLayout.addWidget(self.usernameEntry)

        self.passwordLabel = QLabel("Password:")
        self.passwordEntry = QLineEdit()
        self.passwordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.loginLayout.addWidget(self.passwordLabel)
        self.loginLayout.addWidget(self.passwordEntry)

        self.loginButton = QPushButton("Login")
        self.loginLayout.addWidget(self.loginButton, alignment=Qt.AlignmentFlag.AlignCenter)

        print("Login button clicked")
        self.setLayout(self.loginLayout)
        
class registerFrame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI - Register")

        self.registerFrame = QWidget()
        self.registerLayout = QVBoxLayout()

        self.registerTitle = QLabel("Register")
        self.registerLayout.addWidget(self.registerTitle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.usernameLabel = QLabel("Username:")
        self.usernameEntry = QLineEdit()
        self.registerLayout.addWidget(self.usernameLabel)
        self.registerLayout.addWidget(self.usernameEntry)

        self.passwordLabel = QLabel("Password:")
        self.passwordEntry = QLineEdit()
        self.passwordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.registerLayout.addWidget(self.passwordLabel)
        self.registerLayout.addWidget(self.passwordEntry)

        self.registerButton = QPushButton("Regster")
        self.registerLayout.addWidget(self.registerButton, alignment=Qt.AlignmentFlag.AlignCenter)

        print("Register button clicked")
        self.setLayout(self.registerLayout)