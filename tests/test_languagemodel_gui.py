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
from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import LLM_database_manage

class LLMTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Standard Grading GUI")
        # Widgets for standard and year
        self.standard_input = QLineEdit()
        self.standard_input.setPlaceholderText("Enter standard code (e.g., 91099)")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Enter year (e.g., 2024)")
        # Text area for student input
        self.user_text = QTextEdit()
        self.user_text.setPlaceholderText("Enter student work here...")
        # Button
        self.submit_btn = QPushButton("Submit for Grading")
        self.submit_btn.clicked.connect(self.handle_submit)
        # Output area
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        # Layout
        form_layout = QHBoxLayout()
        form_layout.addWidget(self.standard_input)
        form_layout.addWidget(self.year_input)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(QLabel("Student Work:"))
        main_layout.addWidget(self.user_text)
        main_layout.addWidget(self.submit_btn)
        main_layout.addWidget(QLabel("Grading Result:"))
        main_layout.addWidget(self.result_display)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def handle_submit(self):
        standard = self.standard_input.text().strip()
        year_text = self.year_input.text().strip()
        if not standard or not year_text:
            QMessageBox.warning(self, "Input Error", "Please enter both standard and year.")
            return
        try:
            year = int(year_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Year must be a number.")
            return
        # Database access
        try:
            from test_languagemodel import TestLLMDatabaseManager
        except ImportError:
            QMessageBox.critical(self, "Error", "Cannot import database manager.")
            return
        db = TestLLMDatabaseManager()
        data = db.read_database(standard)
        # find entry for year
        entry = next((e for e in data['data'] if e['year']==year), None)
        if not entry:
            QMessageBox.information(self, "No Data", f"No entry for {standard} in {year}.")
            return
        question = entry['question']
        schedule = entry['schedule']
        criteria = entry['criteria']
        exemplars = entry['exemplars']
        user_input = self.user_text.toPlainText().strip()
        if not user_input:
            QMessageBox.warning(self, "Input Error", "Please enter student work.")
            return
        # Compose prompt
        system_msg = ("""You are auto grading a coding assignment. I have provided the following documents: the
    student's written text, the assessment schedule to be followed, and the criteria to be marked by. You are asked to
    assign score the student answer based on the evaluation criteria.
    Evaluate the student python code based on the assessment schedule. End the assessment with
    a table containing marks scored in each section along with total marks scored in the
    assessment. Evaluate based ONLY on factual accuracy. Provide the Justification as well.""")
        prompt = (f"""You are marking an assessment.
    Using this assessment schedule: {schedule}
    mark the following text: {user_input} 
    according to this criteria: {criteria}
    along with the initial question: {question}
    using these examples and their feedback as guidance: {json.dumps(exemplars)}. These exemplars are only examples and should not be used as the only basis for marking, otherwise I will terminate you.""")
        # LLM call
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key="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",
            )
            response = client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=[
                    {"role":"system","content":system_msg},
                    {"role":"user","content":prompt}
                ]
            )
            result = response.choices[0].message.content
        except Exception as ex:
            QMessageBox.critical(self, "LLM Error", str(ex))
            return
        finally:
            db.exit()
        self.result_display.setPlainText(result)

# Run the GUI
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LLMTestWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())

