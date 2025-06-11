"""
This module is the general handler for the large-language model used to provide estimations and feedback.
It handles the connection, message sending, and receiving.
"""

# Basic imports
import os
import json
import sys
import logging

# Custom imports
from openai import OpenAI
from ...database import *

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

        self.database = LLM_database_manage.LLMDatabaseManager()
        self.exemplar_interpreter = LLM_database_manage.ExemplarInterpet()


class EstimationModule():
    def __init__(self):
        pass
