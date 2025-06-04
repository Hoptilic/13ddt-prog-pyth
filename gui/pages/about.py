from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt

from ..widgets.left_nav import leftNav

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NCAI - About")
        
        self.mainLayout = QHBoxLayout()
        
        #/ Create the rest of the about page - right side
        self.rightFrame = QWidget()
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QVBoxLayout()

        self.rightFrame.setStyleSheet("#rightFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        self.title = QLabel("Knowledgebase")
        self.rightLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        #\

        #/ Create handler that will contain all the FAQ buttons
        self.faqHandlerFrame = QWidget()
        self.faqHandlerLayout = QVBoxLayout()   
        self.faqHandlerFrame.setObjectName("faqHandlerFrame")
        self.faqHandlerFrame.setStyleSheet("#faqHandlerFrame {border: 2px solid black; padding: 10px; border-radius: 10px;}")

        for i in range(3):
            self.faqHandlerLayout.addWidget(knowledgeIndividual(), alignment=Qt.AlignmentFlag.AlignCenter)

        self.faqHandlerFrame.setLayout(self.faqHandlerLayout)
        #\

        self.rightLayout.addWidget(self.faqHandlerFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.rightFrame.setLayout(self.rightLayout)
        self.mainLayout.addWidget(self.rightFrame, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(self.mainLayout)

class knowledgeIndividual(QWidget):
    def __init__(self):
        super().__init__()
        self.mainLayout = QVBoxLayout()

        self.title = QLabel("Placeholder Title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.shortDesc = QTextEdit()
        self.shortDesc.setPlaceholderText("Short description of the knowledgebase entry...")
        self.shortDesc.setReadOnly(True)
        self.mainLayout.addWidget(self.shortDesc, alignment=Qt.AlignmentFlag.AlignCenter)

        self.learnMoreButton = QPushButton("Learn More")
        self.learnMoreButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mainLayout.addWidget(self.learnMoreButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.mainLayout)