import sys
from PySide2.QtWidgets import QApplication
from mainwindow import Mainwindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = Mainwindow()
    sys.exit(app.exec_())
