"""
Card widget for a single recent submission.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QPushButton, QTextEdit
)

from PyQt6.QtCore import Qt, pyqtSignal
import os, sys

class RecentSubmissionIndividual(QWidget):
    """Compact card view for a single submission with click-through."""
    submission_clicked = pyqtSignal(dict)  # Emits submission data when clicked
    
    def __init__(self, submission_data=None): # setting submission data to none means that we assume that there is no submission data so that it doesnt crash and burn immediately
        super().__init__()

        self.setWindowTitle("Recent Submission")
        self.submission_data = submission_data or {}

        self.mainLayout = QVBoxLayout()

        self.indLayout = QVBoxLayout()
        self.mainFrame = QWidget()
        self.mainFrame.setObjectName("mainFrame")

        if submission_data:
            # Display actual submission data
            self.standardLabel = QLabel(f"Standard: {submission_data.get('standard', 'N/A')} ({submission_data.get('year', 'N/A')})")
            self.standardLabel.setObjectName("standardLabel")
            self.indLayout.addWidget(self.standardLabel, alignment=Qt.AlignmentFlag.AlignLeft)

            self.gradeLabel = QLabel(f"Grade: {submission_data.get('grade', 'Not graded')}")
            self.gradeLabel.setObjectName("gradeLabel")
            self.indLayout.addWidget(self.gradeLabel, alignment=Qt.AlignmentFlag.AlignLeft)

            # Show truncated submission text
            submission_text = submission_data.get('submissionText', '')
            if len(submission_text) > 100:
                submission_text = submission_text[:100] + "..."
            
            self.submissionLabel = QLabel(f"Submission: {submission_text}")
            self.submissionLabel.setWordWrap(True)
            self.submissionLabel.setObjectName("submissionLabel")
            self.indLayout.addWidget(self.submissionLabel, alignment=Qt.AlignmentFlag.AlignLeft)

            # Show timestamp
            timestamp = submission_data.get('timestamp', '')
            if timestamp:
                self.timestampLabel = QLabel(f"Submitted: {timestamp}")
                self.timestampLabel.setObjectName("timestampLabel")
                self.indLayout.addWidget(self.timestampLabel, alignment=Qt.AlignmentFlag.AlignRight)
            
            # Add click hint
            click_hint = QLabel("Click to view details")
            click_hint.setObjectName("clickHintLabel")
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
        
        # Enable clicking if we have submission data (cursor on inner card only)
        if submission_data:
            try:
                self.mainFrame.setCursor(Qt.CursorShape.PointingHandCursor)
            except Exception:
                pass


        current_dir = os.path.dirname(__file__)
        assets = os.path.join(current_dir, '..', 'styles', 'sheets')

        page_ss = self.load_qss(os.path.join(assets, "recentSubmissionWidget.qss"), "recentSubmissionWidget.qss")

        self.setStyleSheet(page_ss)
    
    def mousePressEvent(self, event):
        """Handle mouse click to emit submission data only when clicking the card frame."""
        try:
            if event.button() == Qt.MouseButton.LeftButton and self.submission_data:
                # Map click to inner frame coordinates; only emit if click is within mainFrame
                pos_in_frame = self.mainFrame.mapFrom(self, event.position().toPoint())
                if self.mainFrame.rect().contains(pos_in_frame):
                    self.submission_clicked.emit(self.submission_data)
        finally:
            super().mousePressEvent(event)

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