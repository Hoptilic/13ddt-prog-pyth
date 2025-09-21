from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QTextBrowser, QComboBox, QMessageBox, QDialog, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject

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
        # Core state
        self.feedback_module = FeedbackModule()
        self.session_manager = SessionFileManager()
        self.current_submission_data = None
        self.is_viewing_mode = False
        # Threading helpers
        self._worker_thread = None
        self._worker = None
        self._processingDialog = None

        self.setWindowTitle("NCAI - New Submission")
        
        self.mainLayout = QHBoxLayout()
        
        #/ Create the rest of the submissions page - right side
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        self.title = QLabel("Create a new submission")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        # Grade display label (hidden until a grade is available)
        self.gradeLabel = QLabel("")
        self.gradeLabel.setObjectName("gradeLabel")
        self.gradeLabel.hide()
        self.rightLayout.addWidget(self.gradeLabel, alignment=Qt.AlignmentFlag.AlignCenter)
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
        # Hide year selection until a standard is chosen
        self.yearText.hide()

        # Main text area: QTextBrowser (allows rich HTML for feedback) but made editable pre‑submission.
        self.ghostText = QTextBrowser()
        self.ghostText.setOpenLinks(False)          # we'll control any link/click handling later
        self.ghostText.setOpenExternalLinks(False)
        self.ghostText.setAcceptRichText(False)     # user types plain text; model returns HTML later
        self.ghostText.setPlaceholderText("This movie, Mad Max, is directed by...")
        self.ghostText.setReadOnly(False)           # make it editable before processing
        self.ghostText.setDisabled(True)            # stays disabled until a year is chosen
        self.ghostText.document().documentLayout().documentSizeChanged.connect(self.update_ghostTextSize)
        self.submissionsHandlerLayout.addWidget(self.ghostText, alignment=Qt.AlignmentFlag.AlignCenter)
        # Hide text input until year chosen
        self.ghostText.hide()

        # Button layout for submit and delete buttons
        self.buttonLayout = QHBoxLayout()
        self.submitButton = QPushButton("Submit")
        self.submitButton.clicked.connect(self.handleSubit)
        self.buttonLayout.addWidget(self.submitButton)
        # Hide submit until text area is shown
        self.submitButton.hide()
        
        self.deleteButton = QPushButton("Delete Submission")
        self.deleteButton.setObjectName("deleteButton")
        self.deleteButton.clicked.connect(self.handleDelete)
        self.deleteButton.hide()  # hide by default
        self.buttonLayout.addWidget(self.deleteButton)
        
        self.newSubmissionButton = QPushButton("New Submission")
        self.newSubmissionButton.setObjectName("newSubmissionButton")
        self.newSubmissionButton.clicked.connect(self.resetToNewSubmission)
        self.newSubmissionButton.hide()  # hide default
        self.buttonLayout.addWidget(self.newSubmissionButton)

        self.submissionsHandlerLayout.addLayout(self.buttonLayout)
        self.submissionsHandlerFrame.setLayout(self.submissionsHandlerLayout)

        self.rightLayout.addWidget(self.submissionsHandlerFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.rightFrame.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightFrame, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.loadAvailableStandards()
        self.setLayout(self.mainLayout)

        # Stylesheet
        current_dir = os.path.dirname(__file__)
        assets = os.path.join(current_dir, '..', 'styles', 'sheets')

        page_ss = self.load_qss(os.path.join(assets, "submissions.qss"), "submissions.qss")

        self.setStyleSheet(page_ss)

    def loadAvailableStandards(self):
        """Populate standards combo with available standards from DB."""
        DBMgr = LLMDatabaseManager()
        aval_standard = DBMgr.returnAvailableStandards()
        self.standardText.clear()
        self.standardText.addItems(aval_standard)
        print("Available standards loaded:", aval_standard)

    def loadAvailableYears(self, standard):
        """Populate years combo once a standard is chosen."""
        DBMgr = LLMDatabaseManager()
        aval_years = DBMgr.returnAvailableYears(standard)
        self.yearText.clear()
        self.yearText.addItems([str(year) for year in aval_years])
        print("Available years loaded:", aval_years)

    def handleSubit(self):
        """Validate inputs then start background processing thread."""
        # Lazy-refresh the session in case user logged in after this page was constructed.
        if not self.session_manager.currentUser:
            try:
                self.session_manager.loadSession()
            except Exception:
                pass
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
        self._startProcessingThread(standard, year, yearText, userInput)

    def _startProcessingThread(self, standard, year, yearText, userInput):
        """Spin up a QThread + worker and show an indeterminate progress dialog."""
        if self._worker_thread and self._worker_thread.isRunning():
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Processing...")
        v = QVBoxLayout(dlg)
        msg = QLabel("Processing your submission... This may take a moment.")
        bar = QProgressBar()
        bar.setRange(0, 0)
        # Center contents within the dialog using wrapper layouts for consistent centering
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.setContentsMargins(24, 20, 24, 24)
        bar.setFixedWidth(320)
        # Message wrapper
        msgWrap = QWidget()
        msgHBox = QHBoxLayout(msgWrap)
        msgHBox.setContentsMargins(0, 0, 0, 0)
        msgHBox.addStretch(1)
        msgHBox.addWidget(msg)
        msgHBox.addStretch(1)
        v.addWidget(msgWrap)
        # Progress bar wrapper
        barWrap = QWidget()
        barHBox = QHBoxLayout(barWrap)
        barHBox.setContentsMargins(0, 0, 0, 0)
        barHBox.addStretch(1)
        barHBox.addWidget(bar)
        barHBox.addStretch(1)
        v.addWidget(barWrap)
        dlg.setMinimumWidth(420)
        dlg.setModal(True)
        self._processingDialog = dlg
        self._worker_thread = QThread()
        self._worker = _SubmissionWorker(self.feedback_module, standard, year, userInput)
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.finished.connect(lambda result: self._onSubmissionFinished(standard, yearText, year, userInput, result))
        self._worker.error.connect(self._onSubmissionError)
        self._worker.finished.connect(self._cleanupWorker)
        self._worker.error.connect(self._cleanupWorker)
        self._worker_thread.start()
        dlg.show()

    def _cleanupWorker(self, *args):
        """Close dialog, stop thread, release references."""
        try:
            if self._processingDialog:
                self._processingDialog.accept()
        except Exception:
            pass
        if self._worker_thread:
            self._worker_thread.quit()
            self._worker_thread.wait()
        self._worker_thread = None
        self._worker = None
        self._processingDialog = None

    def _onSubmissionError(self, message):
        """Display an error if background processing fails."""
        QMessageBox.critical(self, "Processing Error", message)

    def _onSubmissionFinished(self, standard, yearText, year, userInput, result):
        """Handle successful worker completion: update UI + save to DB."""
        print(result)
        if isinstance(result, list) and len(result) >= 2:
            QMessageBox.critical(self, result[0], result[1])
            return
        highlighted_html = ""
        grade = ""
        try:
            highlighted_html = self.feedback_module.returnHighlightedHTML(result)
            if isinstance(result, dict):
                grade = (result.get('Grade') or 
                        result.get('grade') or
                        result.get('Output', {}).get('Grade') if isinstance(result.get('Output'), dict) else None or
                        result.get('Output', {}).get('grade') if isinstance(result.get('Output'), dict) else None or
                        'Unknown')
            else:
                grade = 'Unknown'
            if highlighted_html and not highlighted_html.startswith("Error:"):
                self.ghostText.setHtml(highlighted_html)
                # Make text read-only but still allow selection + tooltips
                try:
                    self.ghostText.setReadOnly(True)
                except Exception:
                    # fallback to disable if readOnly fails
                    self.ghostText.setDisabled(True)
            else:
                self.ghostText.setPlainText(highlighted_html or "No highlighted HTML available.")
            self.gradeLabel.setText(f"Estimated Grade: {grade}")
            self.gradeLabel.show()
            self.showSubmittedMeta(standard, yearText)
        except Exception as e:
            self.ghostText.setPlainText(f"Error extracting highlighted HTML: {str(e)}")
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

    def showSubmittedMeta(self, standard: str, year: str):
        """Replace editable combos with static labels once submitted."""
        try:
            if hasattr(self, 'submittedMetaContainer'):
                self.standardValueLabel.setText(f"Standard: {standard}")
                self.yearValueLabel.setText(f"Year: {year}")
                self.submittedMetaContainer.show()
            else:
                self.submittedMetaContainer = QWidget()
                metaLayout = QHBoxLayout()
                metaLayout.setContentsMargins(0,0,0,0)
                metaLayout.setSpacing(12)
                self.standardValueLabel = QLabel(f"Standard: {standard}")
                self.yearValueLabel = QLabel(f"Year: {year}")
                self.standardValueLabel.setObjectName("standardLabelStatic")
                self.yearValueLabel.setObjectName("yearLabelStatic")
                metaLayout.addWidget(self.standardValueLabel)
                metaLayout.addWidget(self.yearValueLabel)
                self.submittedMetaContainer.setLayout(metaLayout)
                self.submissionsHandlerLayout.insertWidget(self.submissionsHandlerLayout.indexOf(self.ghostText), self.submittedMetaContainer, alignment=Qt.AlignmentFlag.AlignCenter)
            self.standardText.hide()
            self.yearText.hide()
        except Exception as e:
            print(f"Failed to show submitted meta labels: {e}")

    def handleStandardComboboxChange(self):
        """React to standard selection; show year choices or reset if cleared."""
        selected_standard = self.standardText.currentText()
        print(f"Selected standard: {selected_standard}")
        if selected_standard and selected_standard.strip():
            self.loadAvailableYears(selected_standard)
            self.yearText.show()
            self.yearText.setCurrentIndex(-1)
            self.ghostText.hide()
            self.submitButton.hide()
            self.ghostText.setDisabled(True)
        else:
            self.yearText.clear()
            self.yearText.hide()
            self.ghostText.hide()
            self.submitButton.hide()

    def handleYearComboboxChange(self):
        """Enable text editor & submit button once a year is chosen."""
        selected_year = self.yearText.currentText()
        print(f"Selected year: {selected_year}")
        if selected_year and selected_year.strip():
            self.ghostText.setEnabled(True)
            self.ghostText.show()
            self.submitButton.show()
            self.ghostText.setFocus()
        else:
            self.ghostText.hide()
            self.submitButton.hide()
            self.ghostText.setDisabled(True)

    def update_ghostTextSize(self):
        """Dynamically resize the text edit to fit content within bounds."""
        doc_size = self.ghostText.document().size()
        parent_size = self.size()
        max_width = parent_size.width() - 100
        max_height = parent_size.height() - 300
        desired_width = min(int(doc_size.width()) + 40, max_width)
        desired_height = min(int(doc_size.height()) + 40, max_height)
        min_width = 300
        min_height = 100
        self.ghostText.setMinimumWidth(max(desired_width, min_width))
        self.ghostText.setMaximumWidth(max_width)
        self.ghostText.setMinimumHeight(max(desired_height, min_height))
        self.ghostText.setMaximumHeight(max_height)

    def load_qss(self, path, name):
        """Safe QSS loader (returns empty string on failure)."""
        try:
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading QSS file {name}: {str(e)}")
            return ""

    def loadExistingSubmission(self, submission_data):
        """Populate UI with an existing submission in read‑only mode."""
        self.current_submission_data = submission_data
        self.is_viewing_mode = True
        self.title.setText(f"Viewing Submission - {submission_data.get('standard', 'N/A')} ({submission_data.get('year', 'N/A')})")
        standard = submission_data.get('standard', '')
        year = str(submission_data.get('year', ''))
        standard_index = self.standardText.findText(standard)
        if standard_index >= 0:
            self.standardText.setCurrentIndex(standard_index)
            self.loadAvailableYears(standard)
            year_index = self.yearText.findText(year)
            if year_index >= 0:
                self.yearText.setCurrentIndex(year_index)
        highlighted_html = submission_data.get('highlightedHtml', '')
        if highlighted_html:
            self.ghostText.setHtml(highlighted_html)
        else:
            self.ghostText.setPlainText(submission_data.get('submissionText', ''))
        grade = submission_data.get('grade') or submission_data.get('Grade') or 'Unknown'
        if grade:
            self.gradeLabel.setText(f"Estimated Grade: {grade}")
            self.gradeLabel.show()
        self.ghostText.setEnabled(False)
        self.submitButton.hide()
        self.deleteButton.show()
        self.newSubmissionButton.show()
        self.standardText.setEnabled(False)
        self.yearText.setEnabled(False)

    def resetToNewSubmission(self):
        """Return page to fresh submission state."""
        self.current_submission_data = None
        self.is_viewing_mode = False
        self.title.setText("Create a new submission")
        self.gradeLabel.hide()
        self.gradeLabel.clear()
        try:
            self.standardText.currentIndexChanged.disconnect()
            self.yearText.currentIndexChanged.disconnect()
        except Exception:
            pass
        self.standardText.setCurrentIndex(-1)
        self.yearText.clear()
        self.ghostText.clear()
        self.ghostText.setPlaceholderText("This movie, Mad Max, is directed by...")
        self.ghostText.setReadOnly(False)
        self.ghostText.setDisabled(True)
        self.yearText.hide()
        self.ghostText.hide()
        self.submitButton.hide()
        self.update_ghostTextSize()
        self.standardText.currentIndexChanged.connect(self.handleStandardComboboxChange)
        self.yearText.currentIndexChanged.connect(self.handleYearComboboxChange)
        self.submitButton.show()
        self.deleteButton.hide()
        self.newSubmissionButton.hide()
        self.standardText.setEnabled(True)
        self.yearText.setEnabled(True)
        self.loadAvailableStandards()

    def handleDelete(self):
        """Delete currently viewed submission after confirmation."""
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
                db_manager.cursor.execute("DELETE FROM submissions WHERE id = ?", (submission_id,))
                db_manager.connection.commit()
                db_manager.exit()
                QMessageBox.information(self, "Success", "Submission deleted successfully!")
                self.resetToNewSubmission()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete submission: {str(e)}")


# ---------------- Worker class (isolated) ---------------- #
class _SubmissionWorker(QObject):
    """Worker object moved to a QThread to run LLM submission processing."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, feedback_module, standard, year, userInput):
        super().__init__()
        self.feedback_module = feedback_module
        self.standard = standard
        self.year = year
        self.userInput = userInput

    def run(self):
        """Execute the heavy submission logic; emit result or error."""
        try:
            result = self.feedback_module.handleFullSubmission(
                standard=self.standard,
                year=self.year,
                userInput=self.userInput
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

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
            
        # Launch background worker so UI doesn't freeze
        self._startProcessingThread(standard, year, yearText, userInput)

    #  Threading helpers 
    def _startProcessingThread(self, standard, year, yearText, userInput):
        # Safety: prevent duplicate threads
        if self._worker_thread and self._worker_thread.isRunning():
            return

        # Busy dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Processing...")
        v = QVBoxLayout(dlg)
        msg = QLabel("Processing your submission... This may take a moment.")
        bar = QProgressBar()
        bar.setRange(0, 0)  # indeterminate
        v.addWidget(msg)
        v.addWidget(bar)
        dlg.setModal(True)
        self._processingDialog = dlg

        # Worker setup
        self._worker_thread = QThread()
        self._worker = _SubmissionWorker(self.feedback_module, standard, year, userInput)
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.finished.connect(lambda result: self._onSubmissionFinished(standard, yearText, year, userInput, result))
        self._worker.error.connect(self._onSubmissionError)
        # Cleanup
        self._worker.finished.connect(self._cleanupWorker)
        self._worker.error.connect(self._cleanupWorker)
        self._worker_thread.start()
        dlg.show()

    def _cleanupWorker(self, *args):
        try:
            if self._processingDialog:
                self._processingDialog.accept()
        except Exception:
            pass
        if self._worker_thread:
            self._worker_thread.quit()
            self._worker_thread.wait()
        self._worker_thread = None
        self._worker = None
        self._processingDialog = None

    def _onSubmissionError(self, message):
        QMessageBox.critical(self, "Processing Error", message)

    def _onSubmissionFinished(self, standard, yearText, year, userInput, result):
        print(result)
        # Check if result is an error list
        if isinstance(result, list) and len(result) >= 2:
            QMessageBox.critical(self, result[0], result[1])
            return

        highlighted_html = ""
        grade = ""
        try:
            highlighted_html = self.feedback_module.returnHighlightedHTML(result)
            if isinstance(result, dict):
                grade = (result.get('Grade') or 
                        result.get('grade') or
                        result.get('Output', {}).get('Grade') if isinstance(result.get('Output'), dict) else None or
                        result.get('Output', {}).get('grade') if isinstance(result.get('Output'), dict) else None or
                        'Unknown')
            else:
                grade = 'Unknown'

            if highlighted_html and not highlighted_html.startswith("Error:"):
                self.ghostText.setHtml(highlighted_html)
            else:
                self.ghostText.setPlainText(highlighted_html or "No highlighted HTML available.")
            self.gradeLabel.setText(f"Estimated Grade: {grade}")
            self.gradeLabel.show()
            self.showSubmittedMeta(standard, yearText)
        except Exception as e:
            self.ghostText.setPlainText(f"Error extracting highlighted HTML: {str(e)}")

        # Save submission to database (main thread)
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

    def showSubmittedMeta(self, standard: str, year: str):
        """Hide the dropdowns and show static labels with the submitted standard/year."""
        try:
            # If labels already exist, just update
            if hasattr(self, 'submittedMetaContainer'):
                self.standardValueLabel.setText(f"Standard: {standard}")
                self.yearValueLabel.setText(f"Year: {year}")
                self.submittedMetaContainer.show()
            else:
                self.submittedMetaContainer = QWidget()
                metaLayout = QHBoxLayout()
                metaLayout.setContentsMargins(0,0,0,0)
                metaLayout.setSpacing(12)
                self.standardValueLabel = QLabel(f"Standard: {standard}")
                self.yearValueLabel = QLabel(f"Year: {year}")
                self.standardValueLabel.setObjectName("standardLabelStatic")
                self.yearValueLabel.setObjectName("yearLabelStatic")
                metaLayout.addWidget(self.standardValueLabel)
                metaLayout.addWidget(self.yearValueLabel)
                self.submittedMetaContainer.setLayout(metaLayout)
                self.submissionsHandlerLayout.insertWidget(self.submissionsHandlerLayout.indexOf(self.ghostText), self.submittedMetaContainer, alignment=Qt.AlignmentFlag.AlignCenter)
            self.standardText.hide()
            self.yearText.hide()
        except Exception as e:
            print(f"Failed to show submitted meta labels: {e}")

    def handleStandardComboboxChange(self):
        selected_standard = self.standardText.currentText()
        print(f"Selected standard: {selected_standard}")

        # Only load years if we have a valid standard selected
        if selected_standard and selected_standard.strip():
            self.loadAvailableYears(selected_standard)
            self.yearText.show()
            self.yearText.setCurrentIndex(-1)
            # Hide downstream inputs until year picked
            self.ghostText.hide()
            self.submitButton.hide()
            self.ghostText.setDisabled(True)
        else:
            # Clear the year dropdown if no valid standard is selected
            self.yearText.clear()
            self.yearText.hide()
            self.ghostText.hide()
            self.submitButton.hide()

    def handleYearComboboxChange(self):
        selected_year = self.yearText.currentText()
        print(f"Selected year: {selected_year}")
        if selected_year and selected_year.strip():
            # Now reveal text area and submit button
            self.ghostText.setReadOnly(False)
            self.ghostText.setEnabled(True)
            self.ghostText.show()
            self.submitButton.show()
            self.ghostText.setFocus()
        else:
            self.ghostText.hide()
            self.submitButton.hide()
            self.ghostText.setDisabled(True)

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

        # Display stored grade if present
        grade = submission_data.get('grade') or submission_data.get('Grade') or 'Unknown'
        if grade:
            self.gradeLabel.setText(f"Estimated Grade: {grade}")
            self.gradeLabel.show()
        
        self.ghostText.setEnabled(False)  # Make read-only in vwieing mode
        
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
        self.gradeLabel.hide()
        self.gradeLabel.clear()
        
        # Temporarily disconnect signals to prevent errors during reset
        self.standardText.currentIndexChanged.disconnect()
        self.yearText.currentIndexChanged.disconnect()
        
        # Clear form
        self.standardText.setCurrentIndex(-1)
        self.yearText.clear()
        self.ghostText.clear()
        self.ghostText.setPlaceholderText("This movie, Mad Max, is directed by...")
        self.ghostText.setDisabled(True)
        self.yearText.hide()
        self.ghostText.hide()
        self.submitButton.hide()
        
        # Reset the size of the text edit to default
        self.update_ghostTextSize()
        
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

# Worker class 
class _SubmissionWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, feedback_module, standard, year, userInput):
        super().__init__()
        self.feedback_module = feedback_module
        self.standard = standard
        self.year = year
        self.userInput = userInput

    def run(self):
        try:
            result = self.feedback_module.handleFullSubmission(
                standard=self.standard,
                year=self.year,
                userInput=self.userInput
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))