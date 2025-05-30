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
#     # Test cookie creation
#     cookie_id = cm.createCookie()
#     assert isinstance(cookie_id, str) and len(cookie_id) == 32, "Cookie ID format incorrect"
#     assert cm.checkCookie(cookie_id) == True, "Cookie should exist after creation"
#     # Test best before date (simulate expired cookie)
#     cm.cookies[cookie_id] = 0  # Expire the cookie
#     assert cm.checkBestBeforeDate(cookie_id) == False, "Expired cookie should be invalid"
#     # Test freshenCookie
#     cookie_id2 = cm.createCookie()
#     assert cm.freshenCookie(cookie_id2) == True, "Should be able to freshen cookie"
#     # Test rottenCookie
#     assert cm.rottenCookie(cookie_id2) == True, "Should be able to remove cookie"
#     assert cm.checkCookie(cookie_id2) == False, "Cookie should not exist after removal"
#     # Test saveCookies and file output
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
#     # Patch Login to use our CookieManager instance
#     login.checkCookie = cm.checkCookie
#     login.freshenCookie = cm.freshenCookie
#     login.createCookie = cm.createCookie
#     assert login.grantCookie(cookie_id) == True, "grantCookie should return True"
#     print("grantCookie tests passed!")

# if __name__ == "__main__":
#     test_login()
#     test_cookie_manager()
#     test_grant_cookie()
#     print("All tests passed!")

from gui.pages.home import HomePage
from gui.pages.about import AboutPage
from gui.pages.user import UserPage
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QMainWindow
import sys

# class testHomeSize(QMainWindow):
#     """
#     Test the HomePage class to ensure it initializes correctly.
#     """
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("NCAI")
#         self.resize(1440, 900)
#         self.setCentralWidget(HomePage())

# class testAboutsize(QMainWindow):
#     """
#     Test the AboutPage class to ensure it initializes correctly.
#     """
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("NCAI")
#         self.resize(1440, 900)
#         self.setCentralWidget(AboutPage())

class testUsersize(QMainWindow):
    """
    Test the UserPage class to ensure it initializes correctly.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCAI")
        self.resize(1440, 900)
        self.setCentralWidget(UserPage())

app = QApplication(sys.argv)
window = testUsersize()
window.show()
sys.exit(app.exec())
