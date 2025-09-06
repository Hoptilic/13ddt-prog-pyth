from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QMessageBox, QFormLayout, QSizePolicy
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

        # Root layout (only one main frame; weight adjustments internal)
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(24, 16, 24, 16)
        self.mainLayout.setSpacing(0)

        # Content frame
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightFrame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.rightLayout = QVBoxLayout(self.rightFrame)
        self.rightLayout.setContentsMargins(12, 12, 12, 12)
        self.rightLayout.setSpacing(10)

        # Title (small, fixed height)
        self.title = QLabel("Account Settings")
        tfont = self.title.font()
        tfont.setPointSize(12)
        tfont.setBold(True)
        self.title.setFont(tfont)
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.rightLayout.addWidget(self.title, 0)

        # Security section frame (auto-size to contents)
        self.securityFrame = QWidget()
        self.securityFrame.setObjectName("securityFrame")
        self.securityFrame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.securityLayout = QVBoxLayout(self.securityFrame)
        self.securityLayout.setContentsMargins(10, 10, 10, 10)
        self.securityLayout.setSpacing(8)

        # Security header
        self.securityTitle = QLabel("Security Management")
        sfont = self.securityTitle.font()
        sfont.setPointSize(10)
        sfont.setBold(True)
        self.securityTitle.setFont(sfont)
        self.securityDesc = QLabel("Update your password or permanently delete your account.")
        self.securityDesc.setWordWrap(True)
        dfont = self.securityDesc.font()
        dfont.setPointSize(8)
        self.securityDesc.setFont(dfont)
        self.securityLayout.addWidget(self.securityTitle)
        self.securityLayout.addWidget(self.securityDesc)

        # Password subheading
        self.passwordSubtitle = QLabel("Change Password")
        pfont = self.passwordSubtitle.font()
        pfont.setPointSize(9)
        pfont.setBold(True)
        self.passwordSubtitle.setFont(pfont)
        self.securityLayout.addWidget(self.passwordSubtitle)

        formFrame = QWidget()
        formLayout = QFormLayout(formFrame)
        formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        formLayout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        formLayout.setHorizontalSpacing(8)
        formLayout.setVerticalSpacing(6)

        self.currentPasswordInput = QLineEdit()
        self.currentPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.newPasswordInput = QLineEdit()
        self.newPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirmPasswordInput = QLineEdit()
        self.confirmPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)

        formLayout.addRow(QLabel("Current"), self.currentPasswordInput)
        formLayout.addRow(QLabel("New"), self.newPasswordInput)
        formLayout.addRow(QLabel("Confirm"), self.confirmPasswordInput)
        self.securityLayout.addWidget(formFrame)

        # Change password button centered row
        btnRow = QHBoxLayout()
        btnRow.addStretch(1)
        self.changePasswordButton = QPushButton("Change Password")
        self.changePasswordButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        btnRow.addWidget(self.changePasswordButton)
        btnRow.addStretch(1)
        self.securityLayout.addLayout(btnRow)

        # Danger zone
        self.dangerSubtitle = QLabel("Danger Zone")
        dzfont = self.dangerSubtitle.font()
        dzfont.setPointSize(9)
        dzfont.setBold(True)
        self.dangerSubtitle.setFont(dzfont)
        self.securityLayout.addWidget(self.dangerSubtitle)
        self.deleteHelp = QLabel("Deleting your account will remove all submissions. This cannot be undone.")
        self.deleteHelp.setWordWrap(True)
        hfont = self.deleteHelp.font()
        hfont.setPointSize(8)
        self.deleteHelp.setFont(hfont)
        self.securityLayout.addWidget(self.deleteHelp)
        self.deleteAccountButton = QPushButton("Delete Account")
        self.deleteAccountButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.securityLayout.addWidget(self.deleteAccountButton, 0, Qt.AlignmentFlag.AlignLeft)

        # Add security frame
        self.rightLayout.addWidget(self.securityFrame, 0)
        self.rightLayout.addStretch(1)
        self.mainLayout.addWidget(self.rightFrame, 0, Qt.AlignmentFlag.AlignTop)

        # Connections
        self.changePasswordButton.clicked.connect(self.handle_change_password)
        self.deleteAccountButton.clicked.connect(self.handle_delete_account)

        # Styles
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