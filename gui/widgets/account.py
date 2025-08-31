from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout,
    QLabel, QVBoxLayout, QPushButton, QMenu, QFrame
)

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from socketing.session import SessionFileManager

class AccountWidget(QWidget):
    """
    Widget to display recent submissions.
    """
    def __init__(self):
        super().__init__()

        self.session_manager = SessionFileManager()
        self.setWindowTitle("Recent Submissions")

        # Layout root
        self.mainLayout = QHBoxLayout()

        # Left: user icon + dropdown trigger
        self.usericonFrame = QWidget()
        self.usericonFrame.setObjectName("usericonFrame")
        self.usericonLayout = QVBoxLayout()

        # Clickable container (icon + chevron)
        self.accountContainer = QFrame()
        self.accountContainer.setObjectName("accountContainer")
        self.accountContainerLayout = QVBoxLayout()
        self.accountContainer.setLayout(self.accountContainerLayout)

        # Add account image
        self.icon = QLabel()
        self.icon.setObjectName("userIcon")
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setText("👤")
        self.accountContainerLayout.addWidget(self.icon, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add down arrow below the icon
        self.downArrow = QLabel()
        self.downArrow.setObjectName("downArrow")
        self.downArrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.downArrow.setText("▼")
        self.accountContainerLayout.addWidget(self.downArrow, alignment=Qt.AlignmentFlag.AlignCenter)

        # Hover/click events
        self.accountContainer.enterEvent = self.on_account_hover_enter
        self.accountContainer.leaveEvent = self.on_account_hover_leave
        self.accountContainer.mousePressEvent = self.on_account_click

        # Dropdown menu
        self.dropdown_menu = QMenu(self)
        self.dropdown_menu.setObjectName("accountMenu")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.dropdown_menu.setGraphicsEffect(shadow)
        self.dropdown_menu.addAction("View Profile", self.view_profile)
        self.dropdown_menu.addAction("Account Settings", self.account_settings)
        self.dropdown_menu.addSeparator()
        self.dropdown_menu.addAction("Logout", self.logout)
        self.dropdown_menu.aboutToHide.connect(self.on_dropdown_about_to_hide)

        # Hover delay timer
        self.hover_timer = QTimer()
        self.hover_timer.timeout.connect(self.show_dropdown)
        self.hover_timer.setSingleShot(True)
        self.is_hovering = False

        # Layout tuning
        self.accountContainerLayout.setSpacing(2)
        self.accountContainerLayout.setContentsMargins(6, 6, 6, 6)
        self.usericonLayout.addWidget(self.accountContainer, alignment=Qt.AlignmentFlag.AlignCenter)
        self.usericonLayout.setSpacing(0)
        self.usericonFrame.setLayout(self.usericonLayout)

        # Middle: username
        self.userpackageFrame = QWidget()
        self.userpackageFrame.setObjectName("userpackageFrame")
        self.userpackageLayout = QVBoxLayout()
        self.usernameLabel = QLabel("placeholder")
        self.usernameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.userpackageLayout.addWidget(self.usernameLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.userpackageFrame.setLayout(self.userpackageLayout)

        # Right: notifications button
        self.notificationsButton = QPushButton("🔔")
        self.notificationsButton.setObjectName("notificationsButton")

        # Assemble
        self.mainLayout.addWidget(self.usericonFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.userpackageFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.notificationsButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.mainLayout)

        # Load stylesheet
        current_dir = os.path.dirname(__file__)
        assets = os.path.join(current_dir, '..', 'styles', 'sheets')
        page_ss = self.load_qss(os.path.join(assets, "accountWidget.qss"), "accountWidget.qss")
        self.setStyleSheet(page_ss)

    def update_account_info(self):
        """
        Update the account information displayed in the widget.
        This method should be called whenever the account information changes.
        """
        user = self.session_manager.get_current_user_from_session()        
        if user:
            self.usernameLabel.setText(f'{user}')
        else:
            self.usernameLabel.setText("Not logged in")

    def on_account_hover_enter(self, event):
        """Handle mouse enter event for account container"""
        self.is_hovering = True
        self.hover_timer.start(300)
        
    def on_account_hover_leave(self, event):
        """Handle mouse leave event for account container"""
        self.is_hovering = False
        self.hover_timer.stop()
        # Don't auto-hide dropdown on hover leave - let user click or menu handle it
        
    def on_dropdown_hover_enter(self, event):
        """Handle mouse enter event for dropdown menu"""
        pass
        
    def on_dropdown_hover_leave(self, event):
        """Handle mouse leave event for dropdown menu"""
        pass
        
    def on_account_click(self, event):
        """Handle click event for account container"""
        self.hover_timer.stop()
        # Ensure clicks also show the menu even if not currently hovering
        self.is_hovering = True
        if self.dropdown_menu.isVisible():
            self.dropdown_menu.hide()
        else:
            self.show_dropdown()
        
    def show_dropdown(self):
        """Show the dropdown menu"""
        if not self.dropdown_menu.isVisible() and self.is_hovering:
            # Position dropdown below the account container
            pos = self.accountContainer.mapToGlobal(self.accountContainer.rect().bottomLeft())
            pos.setY(pos.y() + 5)  # Add small gap
            self.dropdown_menu.popup(pos)
            
    def hide_dropdown(self):
        """Hide the dropdown menu"""
        if self.dropdown_menu.isVisible():
            self.dropdown_menu.hide()
            
    def on_dropdown_about_to_hide(self):
        """Handle when dropdown is about to hide"""
    pass

    def view_profile(self):
        """Handle view profile action"""
        print("View Profile clicked")
        # TODO: Implement profile viewing
        
    def account_settings(self):
        """Handle account settings action"""
        print("Account Settings clicked")
        # TODO: Implement settings page
        
    def logout(self):
        """Handle logout action"""
        print("Logout clicked")
        # TODO: Implement proper logout flow

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