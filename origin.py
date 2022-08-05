import sys
from PyQt5.QtWidgets import QApplication, QWidget
# from Uiorc import *
from Ui_ankiaid import *


class MyWindow(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())