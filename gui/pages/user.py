from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from socketing.session import SessionFileManager
from socketing.login import Login


class UserPage(QWidget):
    def __init__(self, event_manager=None):
        super().__init__()
        self.event_manager = event_manager
        self.session = SessionFileManager()
        self.login = Login()

        self.setWindowTitle("NCAI - User")

        self.mainLayout = QHBoxLayout()

        # Right side container
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        self.title = QLabel("User")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Security management container
        self.securityFrame = QWidget()
        self.securityLayout = QVBoxLayout()
        self.securityFrame.setObjectName("securityFrame")

        self.securityTitle = QLabel("Security Management")
        self.securityTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.securityLayout.addWidget(self.securityTitle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.securityDesc = QLabel("Manage your security settings here...")
        self.securityDesc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.securityLayout.addWidget(self.securityDesc, alignment=Qt.AlignmentFlag.AlignCenter)

        # Change password inputs
        self.currentPasswordLabel = QLabel("Current Password")
        self.securityLayout.addWidget(self.currentPasswordLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.currentPasswordInput = QLineEdit()
        self.currentPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.securityLayout.addWidget(self.currentPasswordInput, alignment=Qt.AlignmentFlag.AlignCenter)

        self.newPasswordLabel = QLabel("New Password")
        self.securityLayout.addWidget(self.newPasswordLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.newPasswordInput = QLineEdit()
        self.newPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.securityLayout.addWidget(self.newPasswordInput, alignment=Qt.AlignmentFlag.AlignCenter)

        self.confirmPasswordLabel = QLabel("Confirm New Password")
        self.securityLayout.addWidget(self.confirmPasswordLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.confirmPasswordInput = QLineEdit()
        self.confirmPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.securityLayout.addWidget(self.confirmPasswordInput, alignment=Qt.AlignmentFlag.AlignCenter)

        # Action buttons
        self.changePasswordButton = QPushButton("Change Password")
        self.deleteAccountButton = QPushButton("Delete Account")
        self.securityLayout.addWidget(self.changePasswordButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.securityLayout.addWidget(self.deleteAccountButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.securityFrame.setLayout(self.securityLayout)

        # Assemble right side
        self.rightLayout.addWidget(self.securityFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.rightFrame.setLayout(self.rightLayout)

        self.mainLayout.addWidget(self.rightFrame, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.mainLayout)

        # Connect actions
        self.changePasswordButton.clicked.connect(self.handle_change_password)
        self.deleteAccountButton.clicked.connect(self.handle_delete_account)

        # Load page-specific stylesheet
        current_dir = os.path.dirname(__file__)
        assets = os.path.join(current_dir, '..', 'styles', 'sheets')
        page_ss = self.load_qss(os.path.join(assets, 'user.qss'), 'user.qss')
        if page_ss:
            self.setStyleSheet(page_ss)

    def handle_change_password(self):
        username = self.session.get_current_user_from_session()
        if not username:
            QMessageBox.warning(self, "Not logged in", "Please log in to change your password.")
            return

        current = self.currentPasswordInput.text()
        new = self.newPasswordInput.text()
        confirm = self.confirmPasswordInput.text()

        if new != confirm:
            QMessageBox.warning(self, "Mismatch", "New password and confirmation do not match.")
            return

        # Delegate to Login service
        try:
            ok = self.login.change_password(username, current, new)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid password", str(e))
            return
        if ok:
            QMessageBox.information(self, "Success", "Password updated successfully.")
            self.currentPasswordInput.clear()
            self.newPasswordInput.clear()
            self.confirmPasswordInput.clear()
        else:
            QMessageBox.warning(self, "Incorrect password", "Current password is incorrect or update failed.")

    def handle_delete_account(self):
        username = self.session.get_current_user_from_session()
        if not username:
            QMessageBox.warning(self, "Not logged in", "Please log in to delete your account.")
            return

        confirm = QMessageBox.question(
            self,
            "Delete Account",
            f"Are you sure you want to delete the account '{username}'? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        if self.login.delete_account(username):
            QMessageBox.information(self, "Account deleted", "Your account has been deleted.")
            # Clear the session and return to login
            try:
                self.session.clearSession()
            except Exception:
                pass
            if self.event_manager:
                try:
                    self.event_manager.switch_page.emit("login")
                except Exception:
                    pass
        else:
            QMessageBox.critical(self, "Error", "Failed to delete account.")

    def load_qss(self, path, name):
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading QSS file {name}: {e}")
            return ""