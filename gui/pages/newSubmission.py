from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.socketing.handle import FeedbackModule
from database.LLM_database_manage import LLMDatabaseManager
import gui.styles.sheets as sheets

import json

class NewSubmissionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.feedback_module = FeedbackModule()

        self.setWindowTitle("NCAI - New Submission")
        
        self.mainLayout = QHBoxLayout()
        
        #/ Create the rest of the submissions page - right side
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        self.title = QLabel("Create a new submission")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        #\

        #/ Create handler that will contain the new submission form
        self.submissionsHandlerFrame = QWidget()
        self.submissionsHandlerLayout = QVBoxLayout()   
        self.submissionsHandlerFrame.setObjectName("submissionsHandlerFrame")

        self.standardText = QComboBox()
        self.standardText.setPlaceholderText("Enter standard code (e.g., 91099)")
        self.submissionsHandlerLayout.addWidget(self.standardText, alignment=Qt.AlignmentFlag.AlignCenter)
        self.standardText.currentIndexChanged.connect(self.handleStandardComboboxChange)

        self.yearText = QComboBox()
        self.yearText.setPlaceholderText("Enter year (e.g., 2024)")
        self.submissionsHandlerLayout.addWidget(self.yearText, alignment=Qt.AlignmentFlag.AlignCenter)
        self.yearText.currentIndexChanged.connect(self.handleYearComboboxChange)

        self.ghostText = QTextEdit()
        self.ghostText.setPlaceholderText("This movie, Mad Max, isd irected by...")
        self.ghostText.setDisabled(True)
        self.ghostText.document().documentLayout().documentSizeChanged.connect(self.update_ghostTextSize)
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

        current_dir = os.path.dirname(__file__)
        assets = os.path.join(current_dir, '..', 'styles', 'sheets')

        page_ss = self.load_qss(os.path.join(assets, "submissions.qss"), "submissions.qss")

        self.setStyleSheet(page_ss)

    def loadAvailableStandards(self):
        DBMgr = LLMDatabaseManager()
        aval_standard = DBMgr.returnAvailableStandards()

        self.standardText.clear()
        self.standardText.addItems(aval_standard)

        print("Available standards loaded:", aval_standard)

    def loadAvailableYears(self, standard):
        DBMgr = LLMDatabaseManager()
        aval_years = DBMgr.returnAvailableYears(standard)

        self.yearText.clear()
        self.yearText.addItems([str(year) for year in aval_years])

        print("Available years loaded:", aval_years)

    def handleSubit(self):
        standard = self.standardText.currentText().strip()
        yearText = self.yearText.currentText().strip()
        userInput = self.ghostText.toPlainText().strip()
        
        if not standard or not yearText:
            QMessageBox.warning(self, "Input Error", "Please enter both standard and year.")
            return
        try:
            year = int(yearText)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Year must be a number.")
            return
        if not userInput:
            QMessageBox.warning(self, "Input Error", "Please enter student work.")
            return
            
        # Use the FeedbackModule to handle the submission
        try:
            result = self.feedback_module.handleFullSubmission(
                standard=standard, 
                year=year, 
                userInput=userInput
            )

            print(result)
            
            # Check if result is an error list
            if isinstance(result, list) and len(result) >= 2:
                QMessageBox.critical(self, result[0], result[1])
                return
                
            # Display raw feedback
            # self.resultDisplay.setPlainText(json.dumps(result, indent=2))
            
            # Extract and display highlighted HTML
            try:
                highlighted_html = self.feedback_module.returnHighlightedHTML(result)
                print(highlighted_html)
                if highlighted_html and not highlighted_html.startswith("Error:"):
                    self.ghostText.setHtml(highlighted_html)
                else:
                    self.ghostText.setPlainText(highlighted_html or "No highlighted HTML available.")
            except Exception as e:
                self.ghostText.setPlainText(f"Error extracting highlighted HTML: {str(e)}")
                
        except Exception as ex:
            QMessageBox.critical(self, "Processing Error", str(ex))

    def handleStandardComboboxChange(self):
        selected_standard = self.standardText.currentText()
        print(f"Selected standard: {selected_standard}")

        self.loadAvailableYears(selected_standard)

    def handleYearComboboxChange(self):
        selected_year = self.yearText.currentText()
        print(f"Selected year: {selected_year}")

        self.ghostText.setEnabled(True)

    def update_ghostTextSize(self):
        doc_size = self.ghostText.document().size()
        
        parent_size = self.size()
        max_width = parent_size.width() - 100
        max_height = parent_size.height() - 300 
        
        desired_width = min(int(doc_size.width()) + 40, max_width)
        desired_height = min(int(doc_size.height()) + 40, max_height)
        
        # Ensure minimum size
        min_width = 300
        min_height = 100
        
        self.ghostText.setMinimumWidth(max(desired_width, min_width))
        self.ghostText.setMaximumWidth(max_width)
        self.ghostText.setMinimumHeight(max(desired_height, min_height))
        self.ghostText.setMaximumHeight(max_height)

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