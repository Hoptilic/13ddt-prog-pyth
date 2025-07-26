from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QPushButton, QScrollArea
)

from PyQt6.QtCore import Qt, pyqtSignal
from database.LLM_database_manage import LLMDatabaseManager
from socketing.session import SessionFileManager
from widgets.submission_individual import RecentSubmissionIndividual
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class RecentSubmissions(QWidget):
    """
    Widget to display recent submissions from the database.
    """
    submission_clicked = pyqtSignal(dict)  # Emits submission data when clicked
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Recent Submissions")
        self.session_manager = SessionFileManager()

        self.mainLayout = QVBoxLayout()

        # Create the layout for the recent submissions
        self.recentFrame = QWidget()
        self.recentFrame.setObjectName("recentFrame")
        self.recentLayout = QVBoxLayout()

        self.recentFrame.setObjectName("recentFrame")

        self.title = QLabel("Recent Submissions")
        self.recentLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Create scrollable area for submissions
        self.scrollArea = QScrollArea()
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setWidgetResizable(True)

        self.loadRecentSubmissions()

        self.recentLayout.addWidget(self.scrollArea)
        self.recentFrame.setLayout(self.recentLayout)
        self.mainLayout.addWidget(self.recentFrame, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.mainLayout)

    def loadRecentSubmissions(self):
        """
        Load recent submissions from the database and display them.
        """
        try:
            # Clear existing submissions
            for i in reversed(range(self.scrollLayout.count())): 
                self.scrollLayout.itemAt(i).widget().setParent(None)

            if not self.session_manager.currentUser:
                self.placeholderLabel = QLabel("Please log in to view submissions.")
                self.scrollLayout.addWidget(self.placeholderLabel, alignment=Qt.AlignmentFlag.AlignCenter)
                return

            db_manager = LLMDatabaseManager()
            submissions = db_manager.getUserSubmissions(self.session_manager.currentUser, limit=5)
            db_manager.exit()

            if not submissions:
                self.placeholderLabel = QLabel("No recent submissions yet.")
                self.scrollLayout.addWidget(self.placeholderLabel, alignment=Qt.AlignmentFlag.AlignCenter)
            else:
                for submission in submissions:
                    submission_widget = RecentSubmissionIndividual(submission)
                    # Connect the submission click to our signal
                    submission_widget.submission_clicked.connect(self.submission_clicked.emit)
                    self.scrollLayout.addWidget(submission_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            error_label = QLabel(f"Error loading submissions: {str(e)}")
            self.scrollLayout.addWidget(error_label, alignment=Qt.AlignmentFlag.AlignCenter)