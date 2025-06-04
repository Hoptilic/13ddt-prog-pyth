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
    QApplication, QMainWindow, 
    QStackedWidget, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

# Local imports
from gui.pages import *
from gui.widgets import *
import gui.widgets as widgets
import gui.styles as styles

class EventManager(QObject):
    """
    Central event manager for application-wide signals and events.
    Use this to decouple communication between pages, widgets, and the main window.
    """
    login_success = pyqtSignal(str)  # emits username
    logout = pyqtSignal() # emits nothing (logout doesnt need anything passed, maybe?)
    register_success = pyqtSignal(str)  # emits username
    switch_page = pyqtSignal(str)  # emits page name

    def __init__(self):
        super().__init__()


class MainWindow(QMainWindow):
    """
    Main window of the application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI")
        self.resize(1440, 900)
        self.event_manager = EventManager()

        # At some point make another widget so that the left_nav is loaded once at the start of the program instead of in each page

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.pages = {
            "home": home.HomePage(),
            "about": about.AboutPage(),
            "login": login.LoginPage(event_manager=self.event_manager),
            #"submissions": submissions.SubmissionsPage(),
            "user": user.UserPage()
        }

        for page in self.pages.values():
            self.stacked_widget.addWidget(page)

        # Connect event manager signals to slots
        self.event_manager.login_success.connect(lambda username: self.switch_page("home"))
        self.event_manager.switch_page.connect(self.switch_page)

        # This behaviour will change as the login page will be skipped if the user is already signed in
        self.stacked_widget.setCurrentWidget(self.pages["login"])

    def switch_page(self, page_name):
        """
        Switch to the specified page.
        """
        if page_name in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_name])
        else:
            logging.error(f"Page '{page_name}' does not exist.")

# Run the app
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())