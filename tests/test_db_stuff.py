import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.LLM_database_manage import LLMDatabaseManager

DBMgr = LLMDatabaseManager()

DBMgr.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(DBMgr.cursor.fetchall())