from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout,
    QLabel, QVBoxLayout, QPushButton
)

from PyQt6.QtCore import Qt

class AccountWidget(QWidget):
    """
    Widget to display recent submissions.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Recent Submissions")

        self.mainLayout = QHBoxLayout()

        #/ Create the layout for the user icon area
        self.usericonFrame = QWidget()
        self.usericonFrame.setObjectName("recentFrame")
        self.usericonLayout = QVBoxLayout()
        self.usericonFrame.setStyleSheet("#recentFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        # Add a placeholder account image and down arrow thing from the wireframe
        self.icon = QLabel()
        self.icon.setFixedSize(64, 64)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setText("👤")
        self.usericonLayout.addWidget(self.icon, alignment=Qt.AlignmentFlag.AlignCenter)

        self.downArrow = QLabel()
        self.downArrow.setFixedSize(64, 64)
        self.downArrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.downArrow.setText("⬇️")
        self.usericonLayout.addWidget(self.downArrow, alignment=Qt.AlignmentFlag.AlignCenter)

        self.usericonFrame.setLayout(self.usericonLayout)
        #\ 

        #/ Create the layout for the username and package area
        self.userpackageFrame = QWidget()
        self.userpackageFrame.setObjectName("userpackageFrame")
        self.userpackageLayout = QVBoxLayout()
        self.userpackageFrame.setStyleSheet("#userpackageFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")
        
        self.usernameLabel = QLabel("placeholder")
        self.usernameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.userpackageLayout.addWidget(self.usernameLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.packageLabel = QLabel("placeholder")
        self.packageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.userpackageLayout.addWidget(self.packageLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.userpackageFrame.setLayout(self.userpackageLayout)
        #\

        #/ Add the notifications icon
        self.notificationsButton = QPushButton("🔔")
        self.notificationsButton.setFixedSize(64, 64)
        #\

        # Add all the frames and stuff in a specific order so that it looks decent enough
        self.mainLayout.addWidget(self.usericonFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.userpackageFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.notificationsButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.mainLayout)