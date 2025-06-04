from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt

from ..widgets.left_nav import leftNav

class UserPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NCAI - User")
        
        self.mainLayout = QHBoxLayout()
        
        #/ Create the rest of the user page - right side
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        self.rightFrame.setStyleSheet("#rightFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")
        #\

        self.title = QLabel("User")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        #/ Create handler that will contain all the user buttons
        self.userFrame = QWidget()
        self.userLayout = QVBoxLayout()   
        self.userFrame.setObjectName("userFrame")
        self.userFrame.setStyleSheet("#userFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        # Add a placeholder account image
        self.icon = QLabel()
        self.icon.setFixedSize(64, 64)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setText("👤")
        self.userLayout.addWidget(self.icon, alignment=Qt.AlignmentFlag.AlignCenter)

        self.usernameLabel = QLabel("placeholder")
        self.usernameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.userLayout.addWidget(self.usernameLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.packageLabel = QLabel("pkg placeholder")
        self.packageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.userLayout.addWidget(self.packageLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.logoutButton = QPushButton("Logout")
        self.userLayout.addWidget(self.logoutButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.userFrame.setLayout(self.userLayout)
        #\

        #/ Create the security management frame
        self.securityFrame = QWidget()
        self.securityLayout = QVBoxLayout()
        self.securityFrame.setObjectName("securityFrame")
        self.securityFrame.setStyleSheet("#securityFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        self.securityTitle = QLabel("Security Management")
        self.securityTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.securityLayout.addWidget(self.securityTitle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.securityDesc = QLabel("Manage your security settings here...")
        self.securityDesc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.securityLayout.addWidget(self.securityDesc, alignment=Qt.AlignmentFlag.AlignCenter)

        self.changePasswordButton = QPushButton("Change Password")
        self.securityLayout.addWidget(self.changePasswordButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.deleteAccountButton = QPushButton("Delete Account")
        self.securityLayout.addWidget(self.deleteAccountButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.securityFrame.setLayout(self.securityLayout)
        #\

        self.rightLayout.addWidget(self.userFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.rightLayout.addWidget(self.securityFrame, alignment=Qt.AlignmentFlag.AlignCenter)

        self.rightFrame.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightFrame, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(self.mainLayout)