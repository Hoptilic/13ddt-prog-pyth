"""
Home page: entry point with actions to start a new submission or view previous ones.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import Qt
import json
from openai import OpenAI
import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class HomePage(QWidget):
    """Landing page with navigation buttons to submissions and new submission."""
    def __init__(self, event_manager=None):
        super().__init__()
        self.event_manager = event_manager

        self.setWindowTitle("NCAI - Home")
        
        self.mainLayout = QHBoxLayout()

        #/ Create the rest of the home page - right side
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        self.rightFrame.setStyleSheet("#rightFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")
        #\

        self.title = QLabel("What will we be doing today?")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.selectionFrame = QWidget()
        self.selectionLayout = QVBoxLayout()

        self.previousButton = QPushButton("View Past Submissions")
        self.selectionLayout.addWidget(self.previousButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.previousButton.clicked.connect(self.handlePreviousSubmissions)

        self.submitButton = QPushButton("Create New Submission")
        self.selectionLayout.addWidget(self.submitButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.submitButton.clicked.connect(self.handleSubmit)

        self.selectionFrame.setLayout(self.selectionLayout)
        self.rightLayout.addWidget(self.selectionFrame, alignment=Qt.AlignmentFlag.AlignCenter)

        self.rightFrame.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightFrame, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Set the layout at the end to avoid issues with the layout not being set
        self.setLayout(self.mainLayout)


    def handleSubmit(self):
        """Route to New Submission page via central event manager."""
        self.event_manager.newSubmission.emit()


    def handlePreviousSubmissions(self):
        """Route to Submissions page via central event manager."""
        self.event_manager.switch_page.emit("submissions")
