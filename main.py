import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt5 import uic
from graph_widget import GraphWidget


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Window(QMainWindow):
    canvas: GraphWidget = None

    def __init__(self):
        super().__init__()
        uic.loadUi("main_window.ui", self)
        self.canvas.set_parameters(self.canvas.geometry())
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
