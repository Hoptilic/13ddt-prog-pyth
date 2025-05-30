"""
This is the main entry point for the application.
"""

# System imports
import os
import sys
import time
import random
import logging

# PyQT Imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QPushButton, QLineEdit, 
    QMessageBox, QStackedWidget
)
from PyQt6.QtCore import Qt

# Local imports
from gui.pages import *
import gui.widgets as widgets
import gui.styles as styles

class MainWindow(QMainWindow):
    """
    Main window of the application.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI")
        self.resize(1440, 900)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.pages = {
            "home": home.HomePage(),
            "about": about.AboutPage(),
            "login": login.LoginPage(),
            # "submissions": pages.SubmissionsPage(),
            # "user": pages.UserPage()
        }

        for page in self.pages.values():
            self.stacked_widget.addWidget(page)

        # This behaviour will change as the login page will be skipped if the user is already signed in
        self.stacked_widget.setCurrentWidget(self.pages["login"])

# Run the app
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())