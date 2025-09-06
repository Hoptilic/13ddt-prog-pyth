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
        # Base highlight style (concise visual + relative for padding layer)
        HIGHLIGHT_STYLE = (
            "background-color: rgba(102,255,204,0.45); "
            "padding:2px 3px; "
            "border-radius:3px; "
            "cursor: help; "
            "display:inline-block; "
            "line-height:1.25; "
            "position:relative; "
            "transition: background-color 120ms ease-in; "
        )
        # Extra invisible hover padding to make tooltip activation easier
        HOVER_PAD_STYLE = (
            "position:absolute; left:-6px; top:-4px; right:-6px; bottom:-4px; "
            "background:transparent; z-index:1;"
        )

        def wrap_span(match):
            title_val = match.group(1)
            inner = match.group(2)
            return (
                "<span style='position:relative; display:inline-block;'>"
                f"<span title='{title_val}' style=\"{HIGHLIGHT_STYLE}\">{inner}</span>"
                f"<span style=\"{HOVER_PAD_STYLE}\"></span>"
                "</span>"
            )

        # Replace existing spans with title attr (double + single quotes)
        html = re.sub(r'<span\s+title="([^\"]+)"\s*>(.*?)</span>', wrap_span, html, flags=re.DOTALL)
        html = re.sub(r"<span\s+title='([^']+)'\s*>(.*?)</span>", wrap_span, html, flags=re.DOTALL)

        # Convert <mark> tags
        html = html.replace(
            '<mark>',
            f"<span style='position:relative; display:inline-block;'><span style=\"{HIGHLIGHT_STYLE}\">"
        ).replace(
            '</mark>',
            f"</span><span style=\"{HOVER_PAD_STYLE}\"></span></span>"
        )

        # Spans with title but no style attribute (fallback patterns)
        # double quotes
        pattern = r'<span((?![^>]*style)[^>]*\btitle="[^"]+"[^>]*)>'
        html = re.sub(
            pattern,
            lambda m: (
                "<span style='position:relative; display:inline-block;'>"
                f"<span{m.group(1)} style=\"{HIGHLIGHT_STYLE}\"></span>"
                f"<span style=\"{HOVER_PAD_STYLE}\"></span></span>"
            ),
            html
        )
        # single quotes
        pattern_single = r"<span((?![^>]*style)[^>]*\btitle='[^']+'[^>]*)>"
        html = re.sub(
            pattern_single,
            lambda m: (
                "<span style='position:relative; display:inline-block;'>"
                f"<span{m.group(1)} style=\"{HIGHLIGHT_STYLE}\"></span>"
                f"<span style=\"{HOVER_PAD_STYLE}\"></span></span>"
            ),
            html
        )

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

    def returnGrade(self, output_json):
        """
        Extract Grade from the JSON output - checks for multiple possible keys because the LLM has variation
        """
        grade = output_json.get('Grade') or output_json.get('grade') or (output_json.get('Output', {}).get('Grade')) or (output_json.get('Output', {}).get('grade'))
        return grade or "Not graded"
        
        
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
        # Re-do the entire system message because it isnt really working
        # system_msg = ("You are auto grading a coding assignment. I have provided the student's written text, "
        #             "the assessment schedule, and the criteria. Assign scores based on the criteria. "
        #             "Output in a json format {\"Output\":{\"StudentText\":\"\",\"Grade\":\"\",\"Feedback\":{\"Strengths\":\"\",\"Areas for Improvement\":\"\"},\"HighlightedHTML\":\"\"}}. Within HighlightedHTML, output the student's original text as HTML, "
        #             "wrapping the segments you think needs improvement on with <span style='background-color: yellow'> tags for highlighting, closed by </span>. ENSURE THAT With each highlighted segment, place a tooltip with the feedback for that segment using the <span title='Feedback'> tag. If a highlighted section is not accompanied by a feedback tooltip, I will terminate you. If a feedback tooltip is not accompanied by a highlighted section, I will terminate you."
        #             "Follow this format strictly, otherwise I will terminate you. Do not shorten any part of the text, or I will terminate you. Do not output a shortnened, condensed or summarised version of the text. Output only the json, without any trailing or preceding text, or I will terminate you. DO NOT specify the type of text (by putting json at the top of the output), or I will terminate you."
        #             "Do not output any text that is not in the json format, or I will terminate you. Use valid JSON. All keys and string values must use double quotes. Escape any internal double quotes using backslashes." \
        #             "When quoting parts from the text inside a span, do not use double quotes without an escape character (backslash), or I will terminate you. Avoid nested double quotes entirely in values (single quotes are more robust) All double quotes inside string values must be escaped with a backslash (\\) or replaced with single quotes. All nested single quotes must be escaped with a backslash (\\)"
        # )

        # New system message apparently threatning it makes it scared (weird how that works huh)

        system_msg = (
        "You are grading a student writing submission based on provided criteria, exemplars, and an assessment schedule."
        "Your task is to return ONLY a valid JSON object in the following format:"
        "{\"Output\": {\"StudentText\": \"...\", \"Grade\": \"...\",\"Feedback\": {\"Strengths\": \"...\",\"Areas for Improvement\": \"...\"},\"HighlightedHTML\": \"...\"}}"
        "Inside the 'HighlightedHTML' field, return the student's full original text, converted to HTML. Highlight problematic or improvable text segments using:"
        "- <span title='Your feedback here' style='background-color: rgba(102,255,204,0.5); padding:2px 2px; border-radius:3px; cursor: help;'>Text needing feedback</span>"
        "Each highlighted section must include a tooltip via the 'title' attribute that clearly explains what is wrong or how it can improve."
        "If you highlight something, it MUST have a title with feedback. If you give feedback, it MUST be tied to a highlighted span."
        "**Important output rules:**"
        "- Do NOT include any extra commentary before or after the JSON."
        "- The output must be valid JSON (all keys and string values should use double quotes)."
        "- Escape only double quotes that appear inside string values."
        "- Do NOT escape single quotes."
        "- Do NOT summarize or shorten the student's text. Output the full original version with highlights embedded."
        "- Do not include 'json' at the top of the output."
        "- Do not use newlines outside of JSON string values. For example, do not go {\\n \"Output\"}"
        "- Inside the span tags, use escape apostrophes (&quot) for any single quotes in the text."
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
            result = result.replace("\\'", "'")  # Remove invalid backslash-escaped single quotes
            result = result.replace("‘", "'").replace("’", "'")  # Smart quotes to plain
            result = result.replace('\n', '\\n')  # Escape newlines
            output_json = json.loads(result)
            return output_json
        except json.JSONDecodeError as e:
            print("Bad JSON output:\n", result)
            return(['JSON Error', str(e)])