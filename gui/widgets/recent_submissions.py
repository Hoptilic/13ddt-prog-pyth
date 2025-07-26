from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QPushButton, QScrollArea
)

from PyQt6.QtCore import Qt, pyqtSignal
from database.LLM_database_manage import LLMDatabaseManager
from socketing.session import SessionFileManager
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

        self.recentFrame.setStyleSheet("#recentFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

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

class RecentSubmissionIndividual(QWidget):
    """
    Widget to display an individual recent submission.
    """
    submission_clicked = pyqtSignal(dict)  # Emits submission data when clicked
    
    def __init__(self, submission_data=None):
        super().__init__()

        self.setWindowTitle("Recent Submission")
        self.submission_data = submission_data or {}

        self.mainLayout = QVBoxLayout()

        self.indLayout = QVBoxLayout()
        self.mainFrame = QWidget()
        self.mainFrame.setObjectName("mainFrame")
        self.mainFrame.setStyleSheet("""
            #mainFrame {
                border: 2px solid black; 
                padding: 10px; 
                border-radius: 10px;
                background-color: white;
            }
            #mainFrame:hover {
                background-color: #f8f9fa;
                border-color: #007acc;
            }
        """)

        if submission_data:
            # Display actual submission data
            self.standardLabel = QLabel(f"Standard: {submission_data.get('standard', 'N/A')} ({submission_data.get('year', 'N/A')})")
            self.standardLabel.setStyleSheet("font-weight: bold;")
            self.indLayout.addWidget(self.standardLabel, alignment=Qt.AlignmentFlag.AlignLeft)

            self.gradeLabel = QLabel(f"Grade: {submission_data.get('grade', 'Not graded')}")
            self.gradeLabel.setStyleSheet("color: #007acc;")
            self.indLayout.addWidget(self.gradeLabel, alignment=Qt.AlignmentFlag.AlignLeft)

            # Show truncated submission text
            submission_text = submission_data.get('submissionText', '')
            if len(submission_text) > 100:
                submission_text = submission_text[:100] + "..."
            
            self.submissionLabel = QLabel(f"Submission: {submission_text}")
            self.submissionLabel.setWordWrap(True)
            self.submissionLabel.setStyleSheet("color: #666;")
            self.indLayout.addWidget(self.submissionLabel, alignment=Qt.AlignmentFlag.AlignLeft)

            # Show timestamp
            timestamp = submission_data.get('timestamp', '')
            if timestamp:
                self.timestampLabel = QLabel(f"Submitted: {timestamp}")
                self.timestampLabel.setStyleSheet("font-size: 10px; color: #999;")
                self.indLayout.addWidget(self.timestampLabel, alignment=Qt.AlignmentFlag.AlignRight)
            
            # Add click hint
            click_hint = QLabel("Click to view details")
            click_hint.setStyleSheet("font-size: 10px; color: #007acc; font-style: italic;")
            click_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.indLayout.addWidget(click_hint)
            
        else:
            # Placeholder for when no data is provided
            self.submissionLabel = QLabel("placeholder test")
            self.submissionLabel.setWordWrap(True)
            self.indLayout.addWidget(self.submissionLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.mainFrame.setLayout(self.indLayout)
        self.mainLayout.addWidget(self.mainFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.mainLayout)
        
        # Enable clicking if we have submission data
        if submission_data:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """Handle mouse click to emit submission data."""
        if event.button() == Qt.MouseButton.LeftButton and self.submission_data:
            self.submission_clicked.emit(self.submission_data)
        super().mousePressEvent(event) 