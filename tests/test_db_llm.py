"""
Debug script to check database structure and other stuff that i wasnt sure if it worked (it didnt)
"""

import sqlite3
import json

db_path = './database/LLM_testdatabase.db'
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Check what tables exist
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Available tables:', tables)

for table in tables:
    table_name = table[0]
    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    count = cursor.fetchone()[0]
    print(f'Table {table_name} has {count} rows')
    
    if count > 0:
        cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 1')
        row = cursor.fetchone()
        print(f'Sample row from {table_name}: {row}')
        if row and len(row) > 4 and row[4]:
            try:
                parsed = json.loads(row[4])
                print(f'Parsed exemplars: {parsed}')
                print(f'Type of parsed: {type(parsed)}')
                
                if 'exemplars' in parsed:
                    for i, exemplar in enumerate(parsed['exemplars']):
                        print(f'Exemplar {i+1} grade: {exemplar.get("Grade", "No grade")}')
                        
            except Exception as e:
                print(f'JSON parsing error: {e}')

connection.close()
