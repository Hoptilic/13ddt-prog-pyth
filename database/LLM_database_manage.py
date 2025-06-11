"""
Responsible for managing the LLM database, including reading the database.
Includes functions to read the database and return the data in a structured format.
The database is set out as follows:
Table for each standard (91099, 91100, etc.) with columns for:
- Year
- Question
- Schedule
- Criteria
- Exemplars
  - Json Format:
{ 
    "exemplars": [
        {
            "Exemplar": placeholder
            "Grade": placeholder
            "Feedback": placeholder
        }
    ]
}
"""

import json
import sqlite3

class LLMDatabaseManager:
    def __init__(self):
        """
        Initializes the LLMDatabaseManager with the path to the SQLite database.
        """        
        # Use a test db for testing purposes rn
        self.db_path = "./llm_testdatabase.db"
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def read_database(self, standard):
        """
        Reads the database for a specific standard and returns the data in a structured format.
        """
        query = f'SELECT * FROM "{standard}"'
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        data = {
            "standard": standard,
            "data": []
        }
        
        for row in rows:
            entry = {
                "year": row[0],
                "question": row[1],
                "schedule": row[2],
                "criteria": row[3],
                "exemplars": json.loads(row[4]) if row[4] else []
            }
            data["data"].append(entry)
        return data
    
    def read_standard_by_year(self, standard, year):
        """
        Reads the database for a specific standard and year, returning the data in a structured format.
        """
        query = f'SELECT * FROM "{standard}" WHERE year = ?'
        self.cursor.execute(query, (year,))
        rows = self.cursor.fetchall()
        
        data = {
            "standard": standard,
            "year": year,
            "data": []
        }
        
        for row in rows:
            entry = {
                "question": row[1],
                "schedule": row[2],
                "criteria": row[3],
                "exemplars": json.loads(row[4]) if row[4] else []
            }
            data["data"].append(entry)
        
        return data

    def exit(self):
        """
        Exits the database conection.
        """
        self.connection.close()

class ExemplarInterpet():
    """
    Class to interpret the exemplars from the database.
    """
    def __init__(self, exemplar_data):
        """
        Initializes ExemplarInterpet with the exemplar data.
        """
        self.exemplar_data = exemplar_data

    def get_exemplars(self):
        """
        Returns the list of exemplars.
        """
        return self.exemplar_data.get("exemplars", [])
    def get_exemplars_by_grade(self, grade):
        """
        Returns a list of exemplars for a specific grade (not achieved, achieved, merit, excellence).
        """

        # Because NCEA exemplars are grade on the extended NAME format (N0, N1, N2 etc.), we need to
        # interpret the grade to match achieved/merit/excellence.
        grade_mapping = {
            "N0": "Not Achieved",
            "N1": "Not Achieved",
            "N2": "Not Achieved",
            "A3": "Achieved",
            "A4": "Achieved",
            "M5": "Merit",
            "M6": "Merit",
            "E7": "Excellence",
            "E8": "Excellence"
        }

        # Returns the list of exemplars for the specified grade.
        exemplars = self.get_exemplars()
        target_grade_name = grade_mapping.get(grade, "")
        if not target_grade_name:
            return []
            
        # Find exemplars that start with the grade code or match the grade name
        result = []
        for exemplar in exemplars:
            exemplar_grade = exemplar.get("Grade", "")
            # Check if the exemplar grade starts with the grade code
            if exemplar_grade.startswith(grade):
                result.append(exemplar)
            # Also check if it matches the full grade name
            elif exemplar_grade == target_grade_name:
                result.append(exemplar)
        
        return result
    
    def get_exemplar_feedback(self, exemplar):
        """
        Returns the feedback for a specific exemplar.
        """
        return exemplar.get("Feedback", "")
    
    def get_exemplar_feedback_by_grade(self, grade):
        """
        Returns a list of the feedback for all exemplars of a specific grade.
        """
        # Returns the list of feedback for the specified grade.
        exemplars = self.get_exemplars_by_grade(grade)
        return [self.get_exemplar_feedback(exemplar) for exemplar in exemplars]