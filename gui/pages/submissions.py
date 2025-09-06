from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QGridLayout, QSizePolicy
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
        self.rightLayout.setContentsMargins(0, 0, 0, 0)

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
        self.submissionsHandlerLayout = QGridLayout(self.submissionsHandlerFrame)
        self.submissionsHandlerLayout.setHorizontalSpacing(8)
        self.submissionsHandlerLayout.setVerticalSpacing(8)
        self.submissionsHandlerLayout.setContentsMargins(8, 8, 8, 8)
        self.submissionsHandlerLayout.setColumnStretch(0, 1)
        self.submissionsHandlerLayout.setColumnStretch(1, 1)
        self.submissionsHandlerFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.scrollArea = QScrollArea()
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.submissionsHandlerFrame)
        self.rightLayout.addWidget(self.scrollArea)

        self.rightFrame.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightFrame, 1)
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
        # Clear grid
        while self.submissionsHandlerLayout.count():
            item = self.submissionsHandlerLayout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        # Lazy reload session so a fresh login after page construction is seen
        username = self.session_manager.currentUser
        if not username:
            try:
                self.session_manager.loadSession()
                username = self.session_manager.currentUser
            except Exception:
                pass
        if not username:
            label = QLabel("Please log in to view your submissions.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # Place message spanning available columns
            self.submissionsHandlerLayout.addWidget(label, 0, 0, 1, 2)
            return

        try:
            db = LLMDatabaseManager()
            subs = db.getUserSubmissions(username, limit=50)
            db.exit()
        except Exception as e:
            label = QLabel(f"Error loading submissions: {e}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.submissionsHandlerLayout.addWidget(label, 0, 0, 1, 2)
            return

        if not subs:
            label = QLabel("No submissions yet.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.submissionsHandlerLayout.addWidget(label, 0, 0, 1, 2)
            return

        columns = 2
        for i, sub in enumerate(subs):
            w = RecentSubmissionIndividual(sub)
            # Make cards taller and responsive in width
            w.setMinimumHeight(170)
            w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            if self.event_manager:
                w.submission_clicked.connect(self.event_manager.view_submission.emit)
            row, col = divmod(i, columns)
            self.submissionsHandlerLayout.addWidget(w, row, col, alignment=Qt.AlignmentFlag.AlignTop)

        # Add stretch to push items to top
        last_row = (len(subs) - 1) // columns + 1 if subs else 0
        self.submissionsHandlerLayout.setRowStretch(last_row, 1)

    def load_qss(self, path, name):
        try:
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading QSS file {name}: {str(e)}")
            return ""