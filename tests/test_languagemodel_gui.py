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
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import LLM_database_manage

class LLMTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Standard Grading GUI")
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

    def _normalize_highlight(self, html: str) -> str:
        """
        Ensure any <mark> tags and <span title='...'> spans are given yellow background.
        """
        # convert <mark> to styled spans
        html = html.replace('<mark>', "<span style='background-color: yellow'>").replace('</mark>', '</span>')
        # add highlight style to spans with title but no existing style attr
        pattern = r'<span((?![^>]*style)[^>]*\btitle="[^"]+"[^>]*)>'
        repl = r'<span\1 style="background-color: yellow">'
        html = re.sub(pattern, repl, html)
        return html

    def handleSubmit(self):
        standard = self.standardInput.text().strip()
        yearText = self.yearInput.text().strip()
        if not standard or not yearText:
            QMessageBox.warning(self, "Input Error", "Please enter both standard and year.")
            return
        try:
            year = int(yearText)
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
        data = db.readDatabase(standard)
        # find entry for year
        entry = next((e for e in data['data'] if e['year']==year), None)
        if not entry:
            QMessageBox.information(self, "No Data", f"No entry for {standard} in {year}.")
            return
        question = entry['question']
        schedule = entry['schedule']
        criteria = entry['criteria']
        exemplars = entry['exemplars']
        userInput = self.userText.toPlainText().strip()
        if not userInput:
            QMessageBox.warning(self, "Input Error", "Please enter student work.")
            return
        # Compose prompt with HTML highlight instruction
        system_msg = ("You are auto grading a coding assignment. I have provided the student's written text, "
                      "the assessment schedule, and the criteria. Assign scores based on the criteria. "
                      "Output in a json format {Output:StudentText, Grade, Feedback{Strengths, Areas for Improvement}, HighlightedHTML}. Within HighlightedHTML, output the student's original text as HTML, "
                      "wrapping the segments you think needs improvement on with <span style='background-color: yellow'> tags for highlighting, closed by </span>. ENSURE THAT With each highlighted segment, place a tooltip with the feedback for that segment using the <span title='Feedback'> tag. If a highlighted section is not accompanied by a feedback tooltip, I will terminate you. If a feedback tooltip is not accompanied by a highlighted section, I will terminate you."
                      "Follow this format strictly, otherwise I will terminate you. Do not shorten any part of the text, or I will terminate you. Output only the json, without any trailing or preceding text, or I will terminate you. DO NOT specify the type of text (by putting json at the top of the output), or I will terminate you."
                      "Do not output any text that is not in the json format, or I will terminate you. Do not use backslashes, or I will terminate you. Use single quotes when quoting the text and not double quotes, or I will terminate you."
        )
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
        # Display raw feedback
        self.resultDisplay.setPlainText(result)
        # Extract and display only the HighlightedHTML part of the JSON output
        try:
            try:
                output_json = json.loads(result)
            except json.JSONDecodeError as e:
                self.highlightedDisplay.setPlainText("Error parsing LLM output as JSON:\n" + str(e))
                print("Bad JSON output:\n", result)
                return
            # Debug the HighlightedHTML field
            
            print(output_json.get('HighlightedHTML') or output_json.get('highlightedhtml') or output_json.get('Output').get('HighlightedHTML') or output_json.get('Output').get('highlightedhtml'))
            # Extract HighlightedHTML from top-level JSON - this silly code checks for multiple possible keys because the LLM has variation
            highlighted_html = output_json.get('HighlightedHTML') or output_json.get('highlightedhtml') or output_json.get('Output').get('HighlightedHTML') or output_json.get('Output').get('highlightedhtml')
            if highlighted_html:
                # normalize highlights and feedback spans
                html = self._normalize_highlight(highlighted_html)
                self.highlightedDisplay.setHtml(html)
            else:
                self.highlightedDisplay.setPlainText("No HighlightedHTML field found in output.")
        except json.JSONDecodeError:
            self.highlightedDisplay.setPlainText("Unable to parse JSON from LLM output.")
            print(result)
            print(json.loads(result))


app = QApplication(sys.argv)
window = LLMTestWindow()
window.resize(800, 600)
window.show()
sys.exit(app.exec())

