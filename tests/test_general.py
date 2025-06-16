# import socketing.cookie
# import socketing.login
# import os

# def test_login():
#     login = socketing.login.Login()
    
#     password = "test_passworD1234!"
#     assert login.validate(password) == True, "Password validation failed"
#     salt, key = login.encrypt(password)
#     assert login.unencrypt(password, salt, key) == True, "Password decryption failed"
#     assert login.unencrypt("wrong_password", salt, key) == False, "Incorrect password check failed"
#     print("Login tests passed!")

# def test_cookie_manager():
#     cm = socketing.cookie.CookieManager()
#     cm.initCookieStorage()
#
#     cookie_id = cm.createCookie()
#     assert isinstance(cookie_id, str) and len(cookie_id) == 32, "Cookie ID format incorrect"
#     assert cm.checkCookie(cookie_id) == True, "Cookie should exist after creation"
#
#     cm.cookies[cookie_id] = 0  # Expire the cookie
#     assert cm.checkBestBeforeDate(cookie_id) == False, "Expired cookie should be invalid"
#
#     cookie_id2 = cm.createCookie()
#     assert cm.freshenCookie(cookie_id2) == True, "Should be able to freshen cookie"
#
#     assert cm.rottenCookie(cookie_id2) == True, "Should be able to remove cookie"
#     assert cm.checkCookie(cookie_id2) == False, "Cookie should not exist after removal"
#
#     cookie_id3 = cm.createCookie()
#     cm.saveCookies()
#     assert os.path.exists("cookies.txt"), "cookies.txt should exist after saving"
#     with open("cookies.txt", "r") as f:
#         lines = f.readlines()
#         assert any(cookie_id3 in line for line in lines), "Saved cookie not found in file"
#     print("CookieManager tests passed!")

# def test_grant_cookie():
#     login = socketing.login.Login()
#     cm = socketing.cookie.CookieManager()
#     cm.initCookieStorage()
#     cookie_id = cm.createCookie()
#
#     login.checkCookie = cm.checkCookie
#     login.freshenCookie = cm.freshenCookie
#     login.createCookie = cm.createCookie
#     assert login.grantCookie(cookie_id) == True, "grantCookie should return True"
#     print("grantCookie tests passed!")

# test_login()
# test_cookie_manager()
# test_grant_cookie()
# print("All tests passed!")

import sys, os

# Add project root to sys.path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.pages.home import HomePage
from gui.pages.about import AboutPage
from gui.pages.user import UserPage
from gui.pages.login import LoginPage
from gui.pages.submissions import SubmissionsPage
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QMainWindow
from PyQt6.QtCore import Qt
import logging

class testHomeSize(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI")
        self.resize(1440, 900)
        self.setCentralWidget(HomePage())

class testAboutSize(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI")
        self.resize(1440, 900)
        self.setCentralWidget(AboutPage())

class testUserSize(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI")
        self.resize(1440, 900)
        self.setCentralWidget(UserPage())

class testLoginSize(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI")
        self.resize(1440, 900)
        self.setCentralWidget(LoginPage())

class testSubmissionSize(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI")
        self.resize(1440, 900)
        self.setCentralWidget(SubmissionsPage())

class PageTester(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI - Page Tester")
        self.resize(400, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        title = QLabel("NCAI Page Tester")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.homeBtn = QPushButton("Test Home Page")
        self.homeBtn.clicked.connect(self.testHomePage)
        layout.addWidget(self.homeBtn)
        
        self.aboutBtn = QPushButton("Test About Page")
        self.aboutBtn.clicked.connect(self.testAboutPage)
        layout.addWidget(self.aboutBtn)
        
        self.userBtn = QPushButton("Test User Page")
        self.userBtn.clicked.connect(self.testUserPage)
        layout.addWidget(self.userBtn)

        self.userBtn = QPushButton("Test Login Page")
        self.userBtn.clicked.connect(self.testLoginPage)
        layout.addWidget(self.userBtn)

        self.userBtn = QPushButton("Test Submission Page")
        self.userBtn.clicked.connect(self.testSubmissionPage)
        layout.addWidget(self.userBtn)
        
        self.testAllBtn = QPushButton("Test All Pages")
        self.testAllBtn.clicked.connect(self.testAllPages)
        layout.addWidget(self.testAllBtn)
        
        self.openWindows = []
    
    def testHomePage(self):
        try:
            window = testHomeSize()
            window.show()
            self.openWindows.append(window)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Home Page: {str(e)}")
            logging.error(f"Failed to open Home Page: {str(e)}")
    
    def testAboutPage(self):
        try:
            window = testAboutSize()
            window.show()
            self.openWindows.append(window)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open About Page: {str(e)}")
            logging.error(f"Failed to open About Page: {str(e)}")
    
    def testUserPage(self):
        try:
            window = testUserSize()
            window.show()
            self.openWindows.append(window)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open User Page: {str(e)}")
            logging.error(f"Failed to open User Page: {str(e)}")

    def testLoginPage(self):
        try:
            window = testLoginSize()
            window.show()
            self.openWindows.append(window)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open User Page: {str(e)}")
            logging.error(f"Failed to open User Page: {str(e)}")

    def testSubmissionPage(self):
        try:
            window = testSubmissionSize()
            window.show()
            self.openWindows.append(window)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Submissions Page: {str(e)}")
            logging.error(f"Failed to open Submissions Page: {str(e)}")
    
    def testAllPages(self):
        self.testHomePage()
        self.testAboutPage()
        self.testUserPage()
        self.testLoginPage()

app = QApplication(sys.argv)
window = PageTester()
window.show()
sys.exit(app.exec())

