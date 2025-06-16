# This test gui just tests the LLM stuff on a GUI, focusing on figuring out how to highlight text and display it in a GUI
# All this has is:
# 1) Standard selection
# 2) Year selection
# 3) Rich text for input/highlighted feedback (hoverable for specific feedback)
# 4) Submit button to process the input and display feedback

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QMainWindow
from PyQt6.QtCore import Qt
import sys, os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import LLM_database_manage

