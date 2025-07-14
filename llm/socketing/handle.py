"""
This module is the general handler for the large-language model used to provide estimations and feedback.
It handles the connection, message sending, and receiving.
"""

# Basic imports
import os
import json
import sys
import logging
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Custom imports
from openai import OpenAI
from database import *


class FeedbackModule():
    def __init__(self):
        """
        This class does a lot of things:
        1) It retrieves the exemplars from the database
        2) It sanitizes the exemplars for use in the LLM
        3) It takes the user input and sends it to the LLM alongside the exemplars
        4) It receives the feedback from the LLM
        5) It returns the feedback to the user
        """

    def normalize_highlight(self, html: str):
        """
        Ensure any <mark> tags and <span title='...'> spans are given yellow background.
        """
        # convert <mark> to styled spans
        html = html.replace('<mark>', "<span style='background-color: yellow'>").replace('</mark>', '</span>')
        # add highlight style to spans with title but no existing highlight stuf
        pattern = r'<span((?![^>]*style)[^>]*\btitle="[^"]+"[^>]*)>'
        repl = r'<span\1 style="background-color: yellow">'
        html = re.sub(pattern, repl, html)
        return html
    

    def returnHighlightedHTML(self, output_json):
        """
        Extract HighlightedHTML from top-level JSON - this silly code checks for multiple possible keys because the LLM has variation
        """
        highlighted_html = output_json.get('HighlightedHTML') or output_json.get('highlightedhtml') or output_json.get('Output').get('HighlightedHTML') or output_json.get('Output').get('highlightedhtml')
        if highlighted_html:
            # normalize highlights and feedback spans
            html = self.normalize_highlight(highlighted_html)
            return html
        else:
            return("Error: No HighlightedHTML field found in output.")
        
        
    def handleFullSubmission(self, standard=None, year=None, userInput=None):

        self.standard = standard.strip() if isinstance(standard, str) else str(standard or "")
        self.yearText = str(year) if isinstance(year, int) else (year.strip() if isinstance(year, str) else "")
        if not self.standard or not self.yearText:
            return(['Input Error', 'Please enter both standard and year.'])
        try:
            year = int(self.yearText)
        except ValueError:
            return(['Input Error', 'Year must be a number.'])

        # Database access
        try:
            from tests.test_languagemodel import TestLLMDatabaseManager
        except ImportError:
            return(['Error', 'Cannot import database manager.'])
        db = TestLLMDatabaseManager()
        data = db.readDatabase(standard)

        # find entry for year
        entry = next((e for e in data['data'] if e['year']==year), None)
        if not entry:
            return(['No Data', f"No entry for {standard} in {year}."])
        self.question = entry['question']
        self.schedule = entry['schedule']
        self.criteria = entry['criteria']
        self.exemplars = entry['exemplars']
        self.userText = userInput.strip()
        if not self.userText:
            return(['Input Error', 'Please enter student work.'])
        # Compose prompt with HTML highlight instruction
        system_msg = ("You are auto grading a coding assignment. I have provided the student's written text, "
                    "the assessment schedule, and the criteria. Assign scores based on the criteria. "
                    "Output in a json format {Output:StudentText, Grade, Feedback{Strengths, Areas for Improvement}, HighlightedHTML}. Within HighlightedHTML, output the student's original text as HTML, "
                    "wrapping the segments you think needs improvement on with <span style='background-color: yellow'> tags for highlighting, closed by </span>. ENSURE THAT With each highlighted segment, place a tooltip with the feedback for that segment using the <span title='Feedback'> tag. If a highlighted section is not accompanied by a feedback tooltip, I will terminate you. If a feedback tooltip is not accompanied by a highlighted section, I will terminate you."
                    "Follow this format strictly, otherwise I will terminate you. Do not shorten any part of the text, or I will terminate you. Do not output a shortnened, condensed or summarised version of the text. Output only the json, without any trailing or preceding text, or I will terminate you. DO NOT specify the type of text (by putting json at the top of the output), or I will terminate you."
                    "Do not output any text that is not in the json format, or I will terminate you. Do not use backslashes, or I will terminate you. Use single quotes when quoting the text and not double quotes, or I will terminate you." \
                    "When quoting the text, do not use double quotes, or I will terminate you."
        )
        prompt = (f"""You are marking an assessment.
    Using this assessment schedule: {self.schedule}
    mark the following text: {self.userText}
    according to this criteria: {self.criteria}
    along with the initial question: {self.question}
    using these examples and their feedback as guidance: {json.dumps(self.exemplars)}. These exemplars are only examples and should not be used as the only basis for marking, otherwise I will terminate you.
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
            return(['LLM Error', str(ex)])
        finally:
            db.exit()
        
        # Return the result json
        try:
            output_json = json.loads(result)
            return output_json
        except json.JSONDecodeError as e:
            print("Bad JSON output:\n", result)
            return(['JSON Error', str(e)])