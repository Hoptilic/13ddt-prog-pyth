"""App entry point: builds the main window, pages, and routes between them."""

# System imports
import os
import sys
import time
import random
import logging

# PyQT Imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, 
    QStackedWidget, QWidget, QHBoxLayout, QGraphicsOpacityEffect
)
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; continue if not installed
    pass
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve

# Local imports
from gui.pages import *
from gui.widgets import *
import gui.widgets as widgets
from socketing.cookie import CookieManager
from socketing.session import SessionFileManager

class EventManager(QObject):
    """
    Central event manager for application-wide signals and events.
    Use this to decouple communication between pages, widgets, and the main window.
    """
    login_success = pyqtSignal(str)  # emits username
    logout = pyqtSignal() # emits nothing (logout doesnt need anything passed, maybe?)
    register_success = pyqtSignal(str)  # emits username
    switch_page = pyqtSignal(str)  # emits page name
    newSubmission = pyqtSignal()  # emits nothing, used to switch to new submission page
    view_submission = pyqtSignal(dict)  # emits submission data to view existing submission

    def __init__(self):
        super().__init__()


class MainWindow(QMainWindow):
    """Main window: hosts stacked pages and left navigation, handles routing."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI")
        self.resize(1440, 900)
        self.event_manager = EventManager()

        # Load global stylesheet like in newSubmission.py
        current_dir = os.path.dirname(__file__)
        assets = os.path.join(current_dir, 'gui', 'styles', 'sheets')
        global_ss = self.load_qss(os.path.join(assets, "index.qss"), "index.qss")
        self.setStyleSheet(global_ss)

        # At some point make another widget so that the left_nav is loaded once at the start of the program instead of in each page
        self.main_frame = QWidget()
        self.main_layout = QHBoxLayout(self.main_frame)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for a cleaner look
        self.main_layout.setSpacing(0)
        self.main_frame.setLayout(self.main_layout)
        self.main_frame.setObjectName("mainFrame")

        self.stacked_widget = QStackedWidget()
        self.main_layout.insertWidget(1, self.stacked_widget, 3)
        self.setCentralWidget(self.main_frame)
        # Animation state (effect created only during animations)
        self._stack_opacity = None
        self._fade_out = None
        self._fade_in = None
        # Toggle animations globally (disable if causing paint issues)
        self.enable_animations = False

        self.pages = {
            "home": home.HomePage(event_manager=self.event_manager),
            "about": about.AboutPage(),
            "login": login.LoginPage(event_manager=self.event_manager),
            "newSubmission": newSubmission.NewSubmissionPage(),
            "submissions": submissions.SubmissionsPage(event_manager=self.event_manager),
            "user": user.UserPage(event_manager=self.event_manager)
        }

        # Adds each page at index 1 to make space for the leftnav
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)

        # Connect event manager signals to slots
        self.event_manager.login_success.connect(lambda username: self.switch_page("home"))
        self.event_manager.newSubmission.connect(lambda: self.switch_page("newSubmission"))
        self.event_manager.view_submission.connect(self.view_submission)
        self.event_manager.switch_page.connect(self.switch_page)

        # This behaviour will change as the login page will be skipped if the user is already signed in
        if not self.attempt_auto_login():
            self.stacked_widget.setCurrentWidget(self.pages["login"])

    def switch_page(self, page_name):
        """
        Switch to the specified page.
        """
        if page_name in self.pages:
            # Animate fade-out then perform switch and fade-in
            def perform_switch():
                # Existing switch logic
                if page_name == "login":
                    self.stacked_widget.setCurrentWidget(self.pages[page_name])
                    # Remove left nav if present
                    first_item = self.main_layout.itemAt(0)
                    if first_item is not None and getattr(first_item, 'widget', None):
                        w = first_item.widget()
                        if isinstance(w, left_nav.leftNav):
                            self.main_layout.removeWidget(w)
                            w.setParent(None)
                else:
                    self.stacked_widget.setCurrentWidget(self.pages[page_name])
                    # Only insert left nav if not present
                    first_item = self.main_layout.itemAt(0)
                    existing_widget = first_item.widget() if first_item and first_item.widget() else None
                    if not isinstance(existing_widget, left_nav.leftNav):
                        self.main_layout.insertWidget(0, left_nav.leftNav(event_manager=self.event_manager), 1, alignment=Qt.AlignmentFlag.AlignLeft)

            # Setup animations
            if self.enable_animations:
                try:
                    # Create and attach opacity effect only for the duration of the animation
                    if self._stack_opacity is None:
                        self._stack_opacity = QGraphicsOpacityEffect(self.stacked_widget)
                        self.stacked_widget.setGraphicsEffect(self._stack_opacity)
                    self._stack_opacity.setOpacity(1.0)
                    # Fade out
                    self._fade_out = QPropertyAnimation(self._stack_opacity, b"opacity")
                    self._fade_out.setDuration(200)
                    self._fade_out.setStartValue(1.0)
                    self._fade_out.setEndValue(0.0)
                    self._fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)

                    # On fade-out finished, switch and fade-in
                    def on_fade_out_finished():
                        perform_switch()
                        self._fade_in = QPropertyAnimation(self._stack_opacity, b"opacity")
                        self._fade_in.setDuration(200)
                        self._fade_in.setStartValue(0.0)
                        self._fade_in.setEndValue(1.0)
                        self._fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
                        # When fade-in completes, remove the effect to avoid painting issues during normal interaction
                        def on_fade_in_finished():
                            try:
                                self.stacked_widget.setGraphicsEffect(None)
                            except Exception:
                                pass
                            self._stack_opacity = None
                            self._fade_in = None
                            self._fade_out = None
                        self._fade_in.finished.connect(on_fade_in_finished)
                        self._fade_in.start()

                    self._fade_out.finished.connect(on_fade_out_finished)
                    self._fade_out.start()
                    return
                except Exception:
                    # Fallback to immediate switch on animation issues
                    try:
                        self.stacked_widget.setGraphicsEffect(None)
                    except Exception:
                        pass
                    self._stack_opacity = None
                    self._fade_in = None
                    self._fade_out = None

            # Fallback path: no animation
            # Add the left navigation widget if not on login page - only add it once so we don't have multiple instances
            # Makes updating the information and handling events much, much easier as the left_nav object is created
            # In the main logic file by defualt
            try:
                self.stacked_widget.setGraphicsEffect(None)
            except Exception:
                pass
            self._stack_opacity = None
            self._fade_in = None
            self._fade_out = None
            if page_name == "login":
                self.stacked_widget.setCurrentWidget(self.pages[page_name])
                # Remove left nav if present
                first_item = self.main_layout.itemAt(0)
                if first_item is not None and getattr(first_item, 'widget', None):
                    w = first_item.widget()
                    if isinstance(w, left_nav.leftNav):
                        self.main_layout.removeWidget(w)
                        w.setParent(None)
            else:
                self.stacked_widget.setCurrentWidget(self.pages[page_name])
                # Only insert the left navigation if it is not already there based on the name of the leftnav
                first_item = self.main_layout.itemAt(0)
                existing_widget = first_item.widget() if first_item and first_item.widget() else None
                if not isinstance(existing_widget, left_nav.leftNav):
                    self.main_layout.insertWidget(0, left_nav.leftNav(event_manager=self.event_manager), 1, alignment=Qt.AlignmentFlag.AlignLeft)
        else:
            logging.error(f"Page '{page_name}' does not exist.")

    def view_submission(self, submission_data):
        """
        Switch to newSubmission page and load the submission data for viewing.
        """
        self.switch_page("newSubmission")
        # Load the submission data into the newSubmission page
        self.pages["newSubmission"].loadExistingSubmission(submission_data)

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

    def attempt_auto_login(self) -> bool:
        """Attempt to auto-login using a saved session and a valid cookie.
        Returns True on success, else False.
        """
        try:
            session = SessionFileManager()
            cookie_mgr = CookieManager()
            cookie_mgr.createJar()
            username = session.get_current_user_from_session()
            cookie = session.currentCookie
            if username and cookie and cookie_mgr.checkCookie(cookie):
                # Optionally refresh the cookie
                try:
                    cookie_mgr.freshenCookie(cookie)
                except Exception:
                    pass
                # Route to home via existing signal wiring
                self.event_manager.login_success.emit(username)
                return True
        except Exception as e:
            print(f"Auto-login failed: {e}")
        return False

# Run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

