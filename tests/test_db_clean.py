"""
Test script for LLM database and exemplar functionality
"""

import sys
import os
import sqlite3
import json
from database.LLM_database_manage import LLMDatabaseManager, ExemplarInterpet

# Patch the database path for testing
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
        
        # Test reading entire standard
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

def test_exemplar_interpretation(data):
    """Test exemplar interpretation functionality"""
    print("\nTesting Exemplar Interpretation")
    
    if not data or not data['data']:
        print("No data available for exemplar testing")
        return
    try:
        # Get first entry's exemplars
        first_entry = data['data'][0]
        exemplar_interpreter = ExemplarInterpet(first_entry['exemplars'])
        
        # Test getting all exemplars
        exemplars = exemplar_interpreter.get_exemplars()
        print(f"Found {len(exemplars)} exemplars")
          # Test by grdae
        for grade in ["A4", "M5", "E7"]:
            grade_exemplars = exemplar_interpreter.get_exemplars_by_grade(grade)
            print(f"Grade {grade}: {len(grade_exemplars)} exemplars found")
            
            if grade_exemplars:
                feedback = exemplar_interpreter.get_exemplar_feedback(grade_exemplars[0])
                # dont print the whole feedback just a piece so ik it works
                print(f" - Sample feedback: {feedback[:50]}...")
        
        # Test getting feedback by grade
        feedback_list = exemplar_interpreter.get_exemplar_feedback_by_grade("A4")
        print(f"Achieved feedback entries: {len(feedback_list)}")
        
        return True
        
    except Exception as e:
        print(f"Exemplar interpretation failed: {e}")
        return False

def test_grade_mapping():
    """Test the grade mapping functionality"""
    print("\nTesting Grade Mapping")
    
    # Create test data with various grades
    test_exemplars = {
        "exemplars": [
            {"Exemplar": "Test 1", "Grade": "N0", "Feedback": "Not achieved"},
            {"Exemplar": "Test 2", "Grade": "A3", "Feedback": "Achieved"},
            {"Exemplar": "Test 3", "Grade": "M5", "Feedback": "Merit"},
            {"Exemplar": "Test 4", "Grade": "E7", "Feedback": "Excellence"}
        ]
    }
    
    interpreter = ExemplarInterpet(test_exemplars)
    
    # Test each grade mapping
    grade_tests = [
        ("N0", "Not Achieved"),
        ("A3", "Achieved"), 
        ("M5", "Merit"),
        ("E7", "Excellence")
    ]
    
    for grade_code, expected_grade in grade_tests:
        exemplars = interpreter.get_exemplars_by_grade(grade_code)
        if exemplars:
            print(f"Grade {grade_code} correctly mapped to {expected_grade}")
        else:
            print(f"Grade {grade_code} mapping failed")

def main():
    """Run all tests"""
    print("Starting LLM Database and Exemplar Tests\n")
    
    # Test database connection
    if not test_database_connection():
        print("Database connection failed. Exiting.")
        return
    
    # Test database reading
    data = test_database_reading()
    if not data:
        print("Database reading failed. Exiting.")
        return
    
    # Test exemplar interpretation
    if not test_exemplar_interpretation(data):
        print("Exemplar interpretation failed.")
        return
    
    # Test grade mapping
    test_grade_mapping()
    
    print("\nAll Tests Completed we are so back")

if __name__ == "__main__":
    main()
