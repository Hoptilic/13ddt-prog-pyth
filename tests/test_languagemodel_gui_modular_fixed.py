# This test gui just tests the LLM stuff on a GUI, focusing on figuring out how to highlight text and display it in a GUI
# All this has is:
# 1) Standard selection
# 2) Year selection
# 3) Rich text for input/highlighted feedback (hoverable for specific feedback)
# 4) Submit button to process the input and display feedback

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QMainWindow, QTextEdit
from PyQt6.QtCore import Qt
import sys, os
import logging
import json
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.socketing.handle import FeedbackModule

class LLMTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Standard Grading GUI")
        self.feedback_module = FeedbackModule()
        
        # Widgets for standard and year
        self.standardInput = QLineEdit()
        self.standardInput.setPlaceholderText("Enter standard code (e.g., 91099)")
        self.yearInput = QLineEdit()
        self.yearInput.setPlaceholderText("Enter year (e.g., 2024)")
        # Text area for student input
        self.userText = QTextEdit()
        self.userText.setPlaceholderText("Enter student work here...")
        # Button
        self.submitBtn = QPushButton("Submit for Grading")
        self.submitBtn.clicked.connect(self.handleSubmit)
        # Output area for raw result
        self.resultDisplay = QTextEdit()
        self.resultDisplay.setReadOnly(True)
        # Highlighted student text with feedback
        self.highlightedDisplay = QTextEdit()
        self.highlightedDisplay.setReadOnly(True)
        
        # Layout
        form_layout = QHBoxLayout()
        form_layout.addWidget(self.standardInput)
        form_layout.addWidget(self.yearInput)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(QLabel("Student Work:"))
        main_layout.addWidget(self.userText)
        main_layout.addWidget(self.submitBtn)
        main_layout.addWidget(QLabel("Grading Result:"))
        main_layout.addWidget(self.resultDisplay)
        main_layout.addWidget(QLabel("Highlighted Input with Feedback:"))
        main_layout.addWidget(self.highlightedDisplay)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def handleSubmit(self):
        standard = self.standardInput.text().strip()
        yearText = self.yearInput.text().strip()
        userInput = self.userText.toPlainText().strip()
        
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
            
            # Check if result is an error list
            if isinstance(result, list) and len(result) >= 2:
                QMessageBox.critical(self, result[0], result[1])
                return
                
            # Display raw feedback
            self.resultDisplay.setPlainText(json.dumps(result, indent=2))
            
            # Extract and display highlighted HTML
            try:
                highlighted_html = self.feedback_module.returnHighlightedHTML(result)
                if highlighted_html and not highlighted_html.startswith("Error:"):
                    self.highlightedDisplay.setHtml(highlighted_html)
                else:
                    self.highlightedDisplay.setPlainText(highlighted_html or "No highlighted HTML available.")
            except Exception as e:
                self.highlightedDisplay.setPlainText(f"Error extracting highlighted HTML: {str(e)}")
                
        except Exception as ex:
            QMessageBox.critical(self, "Processing Error", str(ex))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LLMTestWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
