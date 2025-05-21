from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QPushButton, QLineEdit, 
    QMessageBox, QStackedWidget
)
from PyQt6.QtCore import Qt

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NCAI - Login")
        
        self.mainLayout = QVBoxLayout()
        
        # Create the layout for the username and password frame
        self.bodyFrame = QWidget()
        self.bodyLayout = QVBoxLayout()

        self.usernameLabel = QLabel("Username:")
        self.usernameEntry = QLineEdit()
        self.bodyLayout.addWidget(self.usernameLabel)
        self.bodyLayout.addWidget(self.usernameEntry)

        self.passwordLabel = QLabel("Password:")
        self.passwordEntry = QLineEdit()
        self.passwordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.bodyLayout.addWidget(self.passwordLabel)
        self.bodyLayout.addWidget(self.passwordEntry)

        self.bodyFrame.setLayout(self.bodyLayout)
        self.mainLayout.addWidget(self.bodyFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        # Set the layout at the end to avoid issues with the layout not being set
        self.setLayout(self.mainLayout)