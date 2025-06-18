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
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NCAI - Home")
        
        self.mainLayout = QHBoxLayout()

        #/ Create the rest of the home page - right side
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        self.rightFrame.setStyleSheet("#rightFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")
        #\

        self.title = QLabel("What will we be writing about today?")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.selectionFrame = QWidget()
        self.selectionLayout = QVBoxLayout()

        self.standardText = QLineEdit()
        self.standardText.setPlaceholderText("Enter standard code (e.g., 91099)")
        self.selectionLayout.addWidget(self.standardText, alignment=Qt.AlignmentFlag.AlignCenter)

        self.yearText = QLineEdit()
        self.yearText.setPlaceholderText("Enter year (e.g., 2024)")
        self.selectionLayout.addWidget(self.yearText, alignment=Qt.AlignmentFlag.AlignCenter)

        self.ghostText = QTextEdit()
        self.ghostText.setPlaceholderText("This movie, Mad Max, isd irected by...")
        self.selectionLayout.addWidget(self.ghostText, alignment=Qt.AlignmentFlag.AlignCenter)

        self.submitButton = QPushButton("Submit")
        self.selectionLayout.addWidget(self.submitButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.submitButton.clicked.connect(self.handleSubit)

        self.selectionFrame.setLayout(self.selectionLayout)
        self.rightLayout.addWidget(self.selectionFrame, alignment=Qt.AlignmentFlag.AlignCenter)

        self.rightFrame.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightFrame, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Set the layout at the end to avoid issues with the layout not being set
        self.setLayout(self.mainLayout)


    def handleSubit(self):
        standard = self.standardText.text().strip()
        chosenYear = self.yearText.text().strip()
        if not standard or not chosenYear:
            QMessageBox.warning(self, "Input Error", "Please enter both standard and year.")
            return
        try:
            year = int(chosenYear)
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
        userInput = self.ghostText.toPlainText().strip()
        if not userInput:
            QMessageBox.warning(self, "Input Error", "Please enter student work.")
            return
        # Compose prompt with HTML highlight instruction
        system_msg = ("You are auto grading a coding assignment. I have provided the student's written text, "
                      "the assessment schedule, and the criteria. Assign scores based on the criteria. "
                      "Output in a json format {Output:StudentText, Grade, Feedback{Strengths, Areas for Improvement}, HighlightedHTML}. Within HighlightedHTML, output the student's original text as HTML, "
                      "wrapping the segments you think needs improvement on with <span style='background-color: yellow'> tags for highlighting, closed by </span>. With each highlighted segment, place a tooltip with the feedback for that segment using the <span title='Feedback'> tag. "
                      "Follow this format strictly, otherwise I will terminate you. Do not shorten any part of the text, or I will terminate you.")
        prompt = (f"""You are marking an assessment.
    Using this assessment schedule: {schedule}
    mark the following text: {userInput} 
    according to this criteria: {criteria}
    along with the initial question: {question}
    using these examples and their feedback as guidance: {json.dumps(exemplars)}. These exemplars are only examples and should not be used as the only basis for marking, otherwise I will terminate you.
    """)
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
        # Extract and display only the HighlightedHTML part of the JSON output
        try:
            outputJSON = json.loads(result)
            print(outputJSON)
            highlightedHtml = outputJSON.get('HighlightedHTML') or outputJSON.get('highlightedhtml')
            if highlightedHtml:
                # normalize any <mark> tags to styled spans
                html = highlightedHtml.replace('<mark>', "<span style='background-color: yellow'>").replace('</mark>', '</span>')
                self.ghostText.setHtml(html)
            else:
                self.ghostText.setPlainText("No HighlightedHTML field found in output.")
        except json.JSONDecodeError:
            self.ghostText.setPlainText("Unable to parse JSON from LLM output.")
