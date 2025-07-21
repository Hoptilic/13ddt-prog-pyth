from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QPushButton
)

from PyQt6.QtCore import Qt

from .recent_submissions import RecentSubmissions
from .account import AccountWidget

import os, sys

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

        # Add the account widget at the top
        self.account_widget = AccountWidget()
        self.navLayout.addWidget(self.account_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.homeButton = QPushButton("Dashboard")
        self.navLayout.addWidget(self.homeButton)
        self.homeButton.setObjectName("homeButton")

        self.submissionsButton = QPushButton("My Submissions")
        self.navLayout.addWidget(self.submissionsButton)
        self.submissionsButton.setObjectName("submissionsButton")

        self.aboutButton = QPushButton("About")
        self.navLayout.addWidget(self.aboutButton)
        self.aboutButton.setObjectName("aboutButton")

        # Add the recent submissions widget at the bottom
        self.navLayout.addWidget(RecentSubmissions(), alignment=Qt.AlignmentFlag.AlignCenter)

        self.navFrame.setLayout(self.navLayout)
        self.mainLayout.addWidget(self.navFrame, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(self.mainLayout)

        self.update_widget()

        current_dir = os.path.dirname(__file__)
        assets = os.path.join(current_dir, '..', 'styles', 'sheets')

        page_ss = self.load_qss(os.path.join(assets, "leftnav.qss"), "leftnav.qss")

        self.setStyleSheet(page_ss)

    def update_widget(self):
        self.account_widget.update_account_info()

    def load_qss(self, path, name):
        """
        Load a QSS file and return its content.
        """
        try:
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading QSS file {name}: {str(e)}")
            return ""