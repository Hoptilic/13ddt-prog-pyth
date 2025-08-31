from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database.LLM_database_manage import LLMDatabaseManager
from socketing.session import SessionFileManager
from gui.widgets.submission_individual import RecentSubmissionIndividual

class SubmissionsPage(QWidget):
    def __init__(self, event_manager=None):
        super().__init__()
        self.event_manager = event_manager
        self.session_manager = SessionFileManager()

        self.setWindowTitle("NCAI - My Submissions")
        
        self.mainLayout = QHBoxLayout()
        
        # Right side container
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        # Header
        self.title = QLabel("My Submissions")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Actions row
        actions_row = QHBoxLayout()
        self.refreshButton = QPushButton("Refresh")
        self.newButton = QPushButton("New Submission")
        self.newButton.setObjectName("newSubmissionButton")
        actions_row.addWidget(self.refreshButton)
        actions_row.addStretch(1)
        actions_row.addWidget(self.newButton)
        self.rightLayout.addLayout(actions_row)

        # Scroll area for submissions
        self.submissionsHandlerFrame = QWidget()
        self.submissionsHandlerFrame.setObjectName("submissionsHandlerFrame")
        self.submissionsHandlerLayout = QVBoxLayout(self.submissionsHandlerFrame)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.submissionsHandlerFrame)
        self.rightLayout.addWidget(self.scrollArea)

        self.rightFrame.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightFrame, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.mainLayout)

        # Wire actions
        self.refreshButton.clicked.connect(self.load_submissions)
        self.newButton.clicked.connect(lambda: self.event_manager.switch_page.emit("newSubmission") if self.event_manager else None)

        # Styling via QSS
        current_dir = os.path.dirname(__file__)
        assets = os.path.join(current_dir, '..', 'styles', 'sheets')
        self.setStyleSheet(self.load_qss(os.path.join(assets, "submissions.qss"), "submissions.qss"))

        # Initial load
        self.load_submissions()

    def showEvent(self, event):
        # Refresh when page becomes visible
        self.load_submissions()
        super().showEvent(event)

    def load_submissions(self):
        # Clear list
        while self.submissionsHandlerLayout.count():
            item = self.submissionsHandlerLayout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        username = self.session_manager.currentUser
        if not username:
            self.submissionsHandlerLayout.addWidget(QLabel("Please log in to view your submissions."), alignment=Qt.AlignmentFlag.AlignCenter)
            return

        try:
            db = LLMDatabaseManager()
            subs = db.getUserSubmissions(username, limit=50)
            db.exit()
        except Exception as e:
            self.submissionsHandlerLayout.addWidget(QLabel(f"Error loading submissions: {e}"), alignment=Qt.AlignmentFlag.AlignCenter)
            return

        if not subs:
            self.submissionsHandlerLayout.addWidget(QLabel("No submissions yet."), alignment=Qt.AlignmentFlag.AlignCenter)
            return

        for sub in subs:
            w = RecentSubmissionIndividual(sub)
            if self.event_manager:
                w.submission_clicked.connect(self.event_manager.view_submission.emit)
            self.submissionsHandlerLayout.addWidget(w, alignment=Qt.AlignmentFlag.AlignCenter)

        self.submissionsHandlerLayout.addStretch(1)

    def load_qss(self, path, name):
        try:
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading QSS file {name}: {str(e)}")
            return ""