# For now I will have all of the feedback/estimation modules coded here in the same file so I can test them together and see if they work
# Because of that they will not be in separate files as intended 

import os
import json
import sys
import logging
from openai import OpenAI

import sqlite3
from database.LLM_database_manage import LLMDatabaseManager, ExemplarInterpet


# / Steal this code straight from the db testing suite
class TestLLMDatabaseManager(LLMDatabaseManager):
    def __init__(self):
        # force the test database incase i forget to set it to the test one 
        self.db_path = "./database/LLM_testdatabase.db"
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

def test_database_connection():
    """Test basic database connection and table listing"""
    print("Testing Database Connection")
    
    try:
        db_manager = TestLLMDatabaseManager()
        print("Database connection established")
        
        # Check what tables exist
        db_manager.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = db_manager.cursor.fetchall()
        print(f"Available tables: {tables}")

        if not tables:
            print("No tables found. Creating test")
            create_test_table(db_manager)
        
        db_manager.exit()
        return True
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def create_test_table(db_manager):
    """Create a test table with sample data"""
    print("Creating Test Table")
    
    # Create table for standard 91099
    db_manager.cursor.execute('''
        CREATE TABLE IF NOT EXISTS "91099" (
            year INTEGER,
            question TEXT,
            schedule TEXT,
            criteria TEXT,
            exemplars TEXT
        )
    ''')
    
    # Insert sample data
    sample_exemplars = {
        "exemplars": [
            {
                "Exemplar": "Sample student work showing basic understanding",
                "Grade": "A3",
                "Feedback": "Student demonstrates achieved level understanding with clear explanations"
            },
            {
                "Exemplar": "Advanced student work with detailed analysis",
                "Grade": "M5", 
                "Feedback": "Student shows merit level work with good analytical skills"
            },
            {
                "Exemplar": "Exceptional work with innovative solutions",
                "Grade": "E7",
                "Feedback": "Excellence shown through comprehensive understanding and creativity"
            }
        ]
    }
    
    db_manager.cursor.execute('''
        INSERT INTO "91099" (year, question, schedule, criteria, exemplars)
        VALUES (?, ?, ?, ?, ?)
    ''', (2024, "Test Question", "Test Schedule", "Test Criteria", json.dumps(sample_exemplars)))
    
    db_manager.connection.commit()
    print("Test table created with sample data")

def test_database_reading():
    """Test reading data from database"""
    print("Testing Database Reading")
    
    try:
        db_manager = TestLLMDatabaseManager()
        
        # reading entire standard
        data = db_manager.read_database("91099")
        print(f"Read standard 91099: {len(data['data'])} entries found")
        
        if data['data']:
            print(f"Sample entry: Year {data['data'][0]['year']}")
            print(f"Question: {data['data'][0]['question']}")
            
        # Test reading by year
        year_data = db_manager.read_standard_by_year("91099", 2024)
        print(f"Read standard 91099 for year 2024: {len(year_data['data'])} entries found")
        
        db_manager.exit()
        return data
        
    except Exception as e:
        print(f"Database reading failed: {e}")
        return None
    
# \ End of self-stolen code

def test_standard_with_llm_interpretation():
    db_manager = TestLLMDatabaseManager()

    data = db_manager.read_database("91099")
    print(f"Read standard 91099: {len(data['data'])} entries found")

    if data['data']:
        question = data['data'][0]['question']
        exemplars = data['data'][0]['exemplars']
        schedule = data['data'][0]['schedule']
        criteria = data['data'][0]['criteria']
        year = data['data'][0]['year']
    else:
        print("No data found for standard 91099")
        return
    
    userInput = input("etner ur work\n")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )

    system = """You are auto grading a coding assignment. I have provided the following documents: the
student's written text, the assessment schedule to be followed, and the criteria to be marked by. You are asked to
assign score the student answer based on the evaluation criteria.
Evaluate the student python code based on the assessment schedule. End the assessment with
a table containing marks scored in each section along with total marks scored in the
assessment. Evaluate based ONLY on factual accuracy. Provide the Justification as well."""

    prompt = f"""You are marking an assessment.
Using this assessment schedule: {schedule}
mark the following text: {userInput} 
according to this criteria: {criteria}
along with the initial question: {question}
using these exemplars and their feedback as guidance: {json.dumps(exemplars)}
"""

    completion = client.chat.completions.create(
    model="deepseek/deepseek-r1:free",
    messages=[
        {
            "role": "system",
            "content" : system
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    )
    print(completion.choices[0].message.content)



if not test_database_connection():
    print("Database connection failed. Exiting.")
    exit()

# Test database reading
data = test_database_reading()
if not data:
    print("Database reading failed. Exiting.")
    exit()

test_standard_with_llm_interpretation()