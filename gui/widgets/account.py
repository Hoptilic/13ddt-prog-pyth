from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout,
    QLabel, QVBoxLayout, QPushButton, QMenu, QFrame
)

from PyQt6.QtCore import Qt, QTimer
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

        self.mainLayout = QHBoxLayout()        #/ Create the layout for the user icon area with dropdown functionality
        self.usericonFrame = QWidget()
        self.usericonFrame.setObjectName("recentFrame")
        self.usericonLayout = QVBoxLayout()
        self.usericonFrame.setStyleSheet("#recentFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        # Create a combined account widget that acts as a clickable/hoverable unit
        self.accountContainer = QFrame()
        self.accountContainer.setObjectName("accountContainer")
        self.accountContainerLayout = QVBoxLayout()
        self.accountContainer.setLayout(self.accountContainerLayout)
        
        # Add account image
        self.icon = QLabel()
        self.icon.setFixedSize(48, 48)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setText("👤")
        self.accountContainerLayout.addWidget(self.icon, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add down arrow below the icon
        self.downArrow = QLabel()
        self.downArrow.setFixedSize(16, 16)
        self.downArrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.downArrow.setText("▼")
        self.accountContainerLayout.addWidget(self.downArrow, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Set up hover events for the account container
        self.accountContainer.enterEvent = self.on_account_hover_enter
        self.accountContainer.leaveEvent = self.on_account_hover_leave
        self.accountContainer.mousePressEvent = self.on_account_click
          # Create dropdown menu
        self.dropdown_menu = QMenu(self)  # Make it a child of the widget instead
        self.dropdown_menu.addAction("View Profile", self.view_profile)
        self.dropdown_menu.addAction("Account Settings", self.account_settings)
        self.dropdown_menu.addSeparator()
        self.dropdown_menu.addAction("Logout", self.logout)
        
        # Connect menu signals to prevent unwanted hiding
        self.dropdown_menu.aboutToHide.connect(self.on_dropdown_about_to_hide)
        
        # Timer for hover delay
        self.hover_timer = QTimer()
        self.hover_timer.timeout.connect(self.show_dropdown)
        self.hover_timer.setSingleShot(True)
        
        # Simpler state tracking
        self.is_hovering = False
        
        self.accountContainerLayout.setSpacing(2)
        self.accountContainerLayout.setContentsMargins(5, 5, 5, 5)
        
        self.usericonLayout.addWidget(self.accountContainer, alignment=Qt.AlignmentFlag.AlignCenter)
        self.usericonLayout.setSpacing(0)
        self.usericonFrame.setLayout(self.usericonLayout)
        #\ 

        #/ Create the layout for the username and package area
        self.userpackageFrame = QWidget()
        self.userpackageFrame.setObjectName("userpackageFrame")
        self.userpackageLayout = QVBoxLayout()
        self.userpackageFrame.setStyleSheet("#userpackageFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")
        
        self.usernameLabel = QLabel("placeholder")
        self.usernameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.userpackageLayout.addWidget(self.usernameLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        # Not currently using packages
        # self.packageLabel = QLabel("placeholder")
        # self.packageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.userpackageLayout.addWidget(self.packageLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.userpackageFrame.setLayout(self.userpackageLayout)
        #\

        #/ Add the notifications icon
        self.notificationsButton = QPushButton("🔔")
        self.notificationsButton.setFixedSize(64, 64)
        #\

        # Add all the frames and stuff in a specific order so that it looks decent enough
        self.mainLayout.addWidget(self.usericonFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.userpackageFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.notificationsButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.mainLayout)

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
        self.accountContainer.setStyleSheet("QFrame#accountContainer { background-color: #f0f0f0; border-radius: 5px; }")
        
    def on_account_hover_leave(self, event):
        """Handle mouse leave event for account container"""
        self.is_hovering = False
        self.hover_timer.stop()
        self.accountContainer.setStyleSheet("")
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
        self.accountContainer.setStyleSheet("")

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