import sys
from PyQt5.QtWidgets import QApplication
from src.gui.windows.main_window import DBMWindow # 假设主窗口类在 main_window.py 中

def main():
    app = QApplication(sys.argv)
    main_win = DBMWindow() # 创建主窗口实例
    main_win.show()       # 显示主窗口
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()