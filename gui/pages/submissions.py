from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from widgets.submission_individual import submissionIndividual

class SubmissionsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NCAI - Submissions")
        
        self.mainLayout = QHBoxLayout()
        
        #/ Create the rest of the submissions page - right side
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        self.rightFrame.setStyleSheet("#rightFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        self.title = QLabel("Knowledgebase")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        #\

        #/ Create handler that will contain all the submissions
        self.submissionsHandlerFrame = QWidget()
        self.submissionsHandlerLayout = QVBoxLayout()   
        self.submissionsHandlerFrame.setObjectName("submissionsHandlerFrame")
        self.submissionsHandlerFrame.setStyleSheet("#submissionsHandlerFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        for i in range(3):
            self.submissionsHandlerLayout.addWidget(submissionIndividual(), alignment=Qt.AlignmentFlag.AlignCenter)

        self.submissionsHandlerFrame.setLayout(self.submissionsHandlerLayout)
        #\

        self.rightLayout.addWidget(self.submissionsHandlerFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.rightFrame.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightFrame, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(self.mainLayout)