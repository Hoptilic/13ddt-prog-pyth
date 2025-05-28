from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QPushButton
)

from PyQt6.QtCore import Qt

class RecentSubmissions(QWidget):
    """
    Widget to display recent submissions.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Recent Submissions")

        self.mainLayout = QVBoxLayout()

        # Create the layout for the recent submissions
        self.recentFrame = QWidget()
        self.recentFrame.setObjectName("recentFrame")
        self.recentLayout = QVBoxLayout()

        self.recentFrame.setStyleSheet("#recentFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        self.title = QLabel("Recent Submissions")
        self.recentLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Placeholder for recent submissions
        self.placeholderLabel = QLabel("No recent submissions yet.")
        self.recentLayout.addWidget(self.placeholderLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.placeholderSubmission = RecentSubmissionIndividual()
        self.recentLayout.addWidget(self.placeholderSubmission, alignment=Qt.AlignmentFlag.AlignCenter)

        self.recentFrame.setLayout(self.recentLayout)
        self.mainLayout.addWidget(self.recentFrame, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.mainLayout)

class RecentSubmissionIndividual(QWidget):
    """
    Widget to display an individual recent submission.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Recent Submission")

        self.mainLayout = QVBoxLayout()

        self.indLayout = QVBoxLayout()
        self.mainFrame = QWidget()
        self.mainFrame.setObjectName("mainFrame")
        self.mainFrame.setStyleSheet("#mainFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        self.submissionLabel = QLabel("plcaeholder test")
        self.submissionLabel.setWordWrap(True)
        self.indLayout.addWidget(self.submissionLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.mainFrame.setLayout(self.indLayout)
        self.mainLayout.addWidget(self.mainFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.mainLayout) 