from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from widgets.submission_individual import submissionIndividual
from database.LLM_database_manage import LLMDatabaseManager

class NewSubmissionPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NCAI - New Submission")
        
        self.mainLayout = QHBoxLayout()
        
        #/ Create the rest of the submissions page - right side
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        self.rightFrame.setStyleSheet("#rightFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        self.title = QLabel("Create a new submission")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        #\

        #/ Create handler that will contain the new submission form
        self.submissionsHandlerFrame = QWidget()
        self.submissionsHandlerLayout = QVBoxLayout()   
        self.submissionsHandlerFrame.setObjectName("submissionsHandlerFrame")
        self.submissionsHandlerFrame.setStyleSheet("#submissionsHandlerFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        self.standardText = QComboBox()
        self.standardText.setPlaceholderText("Enter standard code (e.g., 91099)")
        self.submissionsHandlerLayout.addWidget(self.standardText, alignment=Qt.AlignmentFlag.AlignCenter)

        self.yearText = QComboBox()
        self.yearText.setPlaceholderText("Enter year (e.g., 2024)")
        self.submissionsHandlerLayout.addWidget(self.yearText, alignment=Qt.AlignmentFlag.AlignCenter)

        self.ghostText = QTextEdit()
        self.ghostText.setPlaceholderText("This movie, Mad Max, isd irected by...")
        self.submissionsHandlerLayout.addWidget(self.ghostText, alignment=Qt.AlignmentFlag.AlignCenter)

        self.submitButton = QPushButton("Submit")
        self.submissionsHandlerLayout.addWidget(self.submitButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.submitButton.clicked.connect(self.handleSubit)

        self.submissionsHandlerFrame.setLayout(self.submissionsHandlerLayout)
        #\

        self.rightLayout.addWidget(self.submissionsHandlerFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.rightFrame.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightFrame, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        

        self.loadAvailableStandards()
        self.setLayout(self.mainLayout)

    def loadAvailableStandards(self):
        DBMgr = LLMDatabaseManager()
        aval_standard = DBMgr.returnAvailableStandards()

        self.standardText.clear()
        self.standardText.addItems(aval_standard)

    def handleSubit(self):
        pass