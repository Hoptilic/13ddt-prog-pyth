from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.socketing.handle import FeedbackModule
from database.LLM_database_manage import LLMDatabaseManager
from socketing.session import SessionFileManager
import gui.styles.sheets as sheets

import json

class NewSubmissionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.feedback_module = FeedbackModule()
        self.session_manager = SessionFileManager()
        self.current_submission_data = None  # Store current submission if viewing existing one
        self.is_viewing_mode = False  # Flag to track if we're viewing an existing submission

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

        # Button layout for submit and delete buttons
        self.buttonLayout = QHBoxLayout()
        
        self.submitButton = QPushButton("Submit")
        self.submitButton.clicked.connect(self.handleSubit)
        self.buttonLayout.addWidget(self.submitButton)
        
        self.deleteButton = QPushButton("🗑️ Delete Submission")
        self.deleteButton.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.deleteButton.clicked.connect(self.handleDelete)
        self.deleteButton.hide()  # Hidden by default
        self.buttonLayout.addWidget(self.deleteButton)
        
        self.newSubmissionButton = QPushButton("New Submission")
        self.newSubmissionButton.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.newSubmissionButton.clicked.connect(self.resetToNewSubmission)
        self.newSubmissionButton.hide()  # Hidden by default
        self.buttonLayout.addWidget(self.newSubmissionButton)
        
        self.submissionsHandlerLayout.addLayout(self.buttonLayout)

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
        # Check if user is logged in
        if not self.session_manager.currentUser:
            QMessageBox.warning(self, "Authentication Error", "Please log in to submit work.")
            return
            
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
                
            # Extract grade and highlighted HTML
            highlighted_html = ""
            grade = ""
            
            try:
                highlighted_html = self.feedback_module.returnHighlightedHTML(result)
                
                # Extract grade from result - check various possible keys
                if isinstance(result, dict):
                    grade = (result.get('Grade') or 
                            result.get('grade') or
                            result.get('Output', {}).get('Grade') if isinstance(result.get('Output'), dict) else None or
                            result.get('Output', {}).get('grade') if isinstance(result.get('Output'), dict) else None or
                            'Unknown')
                
                if highlighted_html and not highlighted_html.startswith("Error:"):
                    self.ghostText.setHtml(highlighted_html)
                else:
                    self.ghostText.setPlainText(highlighted_html or "No highlighted HTML available.")
                    
            except Exception as e:
                self.ghostText.setPlainText(f"Error extracting highlighted HTML: {str(e)}")
            
            # Save submission to database
            try:
                db_manager = LLMDatabaseManager()
                submission_id = db_manager.saveSubmission(
                    username=self.session_manager.currentUser,
                    standard=standard,
                    year=year,
                    submissionText=userInput,
                    feedback=result if isinstance(result, dict) else {},
                    highlightedHtml=highlighted_html,
                    grade=grade
                )
                db_manager.exit()
                
                QMessageBox.information(self, "Success", f"Submission saved successfully! (ID: {submission_id})")
                
            except Exception as e:
                QMessageBox.warning(self, "Database Error", f"Failed to save submission: {str(e)}")
                
        except Exception as ex:
            QMessageBox.critical(self, "Processing Error", str(ex))

    def handleStandardComboboxChange(self):
        selected_standard = self.standardText.currentText()
        print(f"Selected standard: {selected_standard}")

        # Only load years if we have a valid standard selected
        if selected_standard and selected_standard.strip():
            self.loadAvailableYears(selected_standard)
        else:
            # Clear the year dropdown if no valid standard is selected
            self.yearText.clear()

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
    
    def loadExistingSubmission(self, submission_data):
        """
        Load an existing submission for viewing/editing.
        """
        self.current_submission_data = submission_data
        self.is_viewing_mode = True
        
        # Update UI title
        self.title.setText(f"Viewing Submission - {submission_data.get('standard', 'N/A')} ({submission_data.get('year', 'N/A')})")
        
        # Set form fields
        standard = submission_data.get('standard', '')
        year = str(submission_data.get('year', ''))
        
        # Find and set standard
        standard_index = self.standardText.findText(standard)
        if standard_index >= 0:
            self.standardText.setCurrentIndex(standard_index)
            self.loadAvailableYears(standard)
            
            # Set year
            year_index = self.yearText.findText(year)
            if year_index >= 0:
                self.yearText.setCurrentIndex(year_index)
        
        # Load submission text and feedback
        highlighted_html = submission_data.get('highlightedHtml', '')
        if highlighted_html:
            self.ghostText.setHtml(highlighted_html)
        else:
            self.ghostText.setPlainText(submission_data.get('submissionText', ''))
        
        self.ghostText.setEnabled(False)  # Make read-only in viewing mode
        
        # Update button visibility
        self.submitButton.hide()
        self.deleteButton.show()
        self.newSubmissionButton.show()
        
        # Disable form controls in viewing mode
        self.standardText.setEnabled(False)
        self.yearText.setEnabled(False)
    
    def resetToNewSubmission(self):
        """
        Reset the form to create a new submission.
        """
        self.current_submission_data = None
        self.is_viewing_mode = False
        
        # Update UI title
        self.title.setText("Create a new submission")
        
        # Temporarily disconnect signals to prevent errors during reset
        self.standardText.currentIndexChanged.disconnect()
        self.yearText.currentIndexChanged.disconnect()
        
        # Clear form
        self.standardText.setCurrentIndex(-1)
        self.yearText.clear()
        self.ghostText.clear()
        self.ghostText.setPlaceholderText("This movie, Mad Max, isd irected by...")
        self.ghostText.setDisabled(True)
        
        # Reconnect signals
        self.standardText.currentIndexChanged.connect(self.handleStandardComboboxChange)
        self.yearText.currentIndexChanged.connect(self.handleYearComboboxChange)
        
        # Update button visibility
        self.submitButton.show()
        self.deleteButton.hide()
        self.newSubmissionButton.hide()
        
        # Re-enable form controls
        self.standardText.setEnabled(True)
        self.yearText.setEnabled(True)
        
        # Reload available standards
        self.loadAvailableStandards()
    
    def handleDelete(self):
        """
        Delete the current submission after confirmation.
        """
        if not self.current_submission_data:
            return
            
        submission_id = self.current_submission_data.get('id')
        standard = self.current_submission_data.get('standard', 'N/A')
        year = self.current_submission_data.get('year', 'N/A')
        timestamp = self.current_submission_data.get('timestamp', 'Unknown')
        
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete this submission?\n\n"
            f"Standard: {standard}\n"
            f"Year: {year}\n"
            f"Submitted: {timestamp}\n\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db_manager = LLMDatabaseManager()
                # Delete from database
                db_manager.cursor.execute("DELETE FROM submissions WHERE id = ?", (submission_id,))
                db_manager.connection.commit()
                db_manager.exit()
                
                QMessageBox.information(self, "Success", "Submission deleted successfully!")
                
                # Reset to new submission mode
                self.resetToNewSubmission()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete submission: {str(e)}")