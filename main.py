import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QPushButton, QLabel
from PyQt5 import uic
from graph_widget import GraphWidget
from main_window import Ui_MainWindow


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Window(QMainWindow, Ui_MainWindow):
    canvas: GraphWidget = None
    points_table: QTableWidget = None
    function_lbl: QLabel = None
    error_lbl: QLabel = None
    estimate_lbl: QLabel = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.canvas.set_parameters(self.canvas.geometry())
        self.points_table.setRowCount(1)
        self.points_table.setItem(0, 0, QTableWidgetItem(""))
        self.points_table.setItem(0, 1, QTableWidgetItem(""))
        self.points_table.cellChanged.connect(self.update_table)
        self.calculate_btn.clicked.connect(self.calculate)
        self.function_lbl.setText("")
        self.estimate_lbl.setText("")
        self.error_lbl.setText("")
        self.repaint()

    def update_table(self):
        self.points_table.blockSignals(True)
        row_count = self.points_table.rowCount()
        if self.points_table.item(row_count - 1, 0).text().strip() != "" or \
                self.points_table.item(row_count - 1, 1).text().strip() != "":
            self.points_table.setRowCount(row_count + 1)
            self.points_table.setItem(row_count, 0, QTableWidgetItem(""))
            self.points_table.setItem(row_count, 1, QTableWidgetItem(""))
            if self.points_table.item(row_count - 1, 0).text().strip() == "":
                self.points_table.item(row_count - 1, 0).setText("0")
            else:
                self.points_table.item(row_count - 1, 1).setText("0")
        for i in range(row_count - 2, -1, -1):
            if self.points_table.item(i, 0).text().strip() == "" and self.points_table.item(i, 1).text().strip() == "":
                self.points_table.removeRow(i)
        self.points_table.blockSignals(False)

    def calculate(self):
        self.function_lbl.setText("")
        self.estimate_lbl.setText("")
        try:
            points = self.get_points()
        except ValueError:
            self.error_lbl.setText("Ошибка при получении данных: некоторые данные не являются числами")
            return
        if len(points) < 3:
            self.error_lbl.setText("Ошибка при получении данных: для расчёта необходимо минимум три точки")
            return
        self.canvas.setDrawnPoints(points)
        self.repaint()
        self.error_lbl.setText("")
        self.function_lbl.setText(
            f"Предполагаемая зависимость: y = {self.canvas.result['a']}x + {self.canvas.result['b']}")
        if self.canvas.result["accuracy"] == 0:
            self.estimate_lbl.setText("")
        elif self.canvas.result["accuracy"] == 1:
            self.estimate_lbl.setText("Функция может быть определена неточно")
        elif self.canvas.result["accuracy"] == 2:
            self.estimate_lbl.setText("Слишком большой разброс значений: точно определить функцию невозможно")

    def get_points(self):
        row_count = self.points_table.rowCount()
        points = []
        for i in range(row_count - 1):
            point = (float(self.points_table.item(i, 0).text()), float(self.points_table.item(i, 1).text()))
            points.append(point)
        return points


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
