from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QPushButton, QTextEdit
)

from PyQt6.QtCore import Qt

class submissionIndividual(QWidget):
    def __init__(self):
        super().__init__()
        self.mainLayout = QVBoxLayout()

        self.title = QLabel("Placeholder Title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.shortDesc = QTextEdit()
        self.shortDesc.setPlaceholderText("Short description of the submission entry...")
        self.shortDesc.setReadOnly(True)
        self.mainLayout.addWidget(self.shortDesc, alignment=Qt.AlignmentFlag.AlignCenter)

        self.learnMoreButton = QPushButton("View Submission")
        self.learnMoreButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mainLayout.addWidget(self.learnMoreButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.mainLayout)