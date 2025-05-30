from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt

from ..widgets.left_nav import leftNav

class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NCAI - Home")
        
        self.mainLayout = QHBoxLayout()
        
        # Add the left navigation widget to the left side of the main layout
        self.mainLayout.addWidget(leftNav(), 1, alignment=Qt.AlignmentFlag.AlignLeft)

        #/ Create the rest of the home page - right side
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        self.rightFrame.setStyleSheet("#rightFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        self.title = QLabel("What will we be writing about today?")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.selectionFrame = QWidget()
        self.selectionLayout = QVBoxLayout()

        self.ghostText = QTextEdit()
        self.ghostText.setPlaceholderText("Today I will write about...")
        self.selectionLayout.addWidget(self.ghostText, alignment=Qt.AlignmentFlag.AlignCenter)

        self.submitButton = QPushButton("Submit")
        self.selectionLayout.addWidget(self.submitButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.selectionFrame.setLayout(self.selectionLayout)
        self.rightLayout.addWidget(self.selectionFrame, alignment=Qt.AlignmentFlag.AlignCenter)

        self.rightFrame.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightFrame, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        # Set the layout at the end to avoid issues with the layout not being set
        self.setLayout(self.mainLayout)