# For now I will have all of the feedback/estimation modules coded here in the same file so I can test them together and see if they work
# Because of that they will not be in separate files as intended 

import os
import json
import sys
import logging
from openai import OpenAI
from database.LLM_database_manage import LLMDatabaseManager, ExemplarInterpet