from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton
)

from PyQt6.QtCore import Qt

class leftNav(QWidget):
    """
    Left navigation widget for the application.
    Contains buttons to navigate to different pages.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NCAI - Navigation")
        
        self.mainLayout = QVBoxLayout()
        
        # Create the layout for the left navigation
        self.navFrame = QWidget()
        self.navFrame.setObjectName("navFrame")
        self.navLayout = QVBoxLayout()

        self.navFrame.setStyleSheet("#navFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        self.placeholderTitle = QLabel("Account Stuff")
        self.navLayout.addWidget(self.placeholderTitle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.homeButton = QPushButton("Dashboard")
        self.navLayout.addWidget(self.homeButton)

        self.submissionsButton = QPushButton("My Submissions")
        self.navLayout.addWidget(self.submissionsButton)

        self.aboutButton = QPushButton("About")
        self.navLayout.addWidget(self.aboutButton)

        self.placeholderTitle2 = QLabel("Previous submissions stuff")
        self.navLayout.addWidget(self.placeholderTitle2, alignment=Qt.AlignmentFlag.AlignCenter)

        self.navFrame.setLayout(self.navLayout)
        self.mainLayout.addWidget(self.navFrame, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.setLayout(self.mainLayout)