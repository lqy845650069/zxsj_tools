# src/gui/windows/main_window.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class DBMWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBM 应用程序")
        self.setGeometry(300, 300, 400, 300) # 稍微调整窗口大小

        layout = QVBoxLayout()
        label = QLabel("欢迎使用 DBM!")
        layout.addWidget(label)
        self.setLayout(layout)