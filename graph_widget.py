import math

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *


E = 10e-9


class GraphWidget(QWidget):
    def __init__(self, parent):
        super(GraphWidget, self).__init__(parent)
        self.x = 0
        self.y = 0
        self.w = 100
        self.h = 30
        self.axis_pen = QPen()
        self.axis_pen.setColor(Qt.black)
        self.axis_pen.setWidth(3)
        self.grid_pen = QPen()
        self.grid_pen.setColor(QColor(192, 192, 192))
        self.grid_pen.setWidth(1)
        self.grid_pen_dark = QPen()
        self.grid_pen_dark.setColor(QColor(128, 128, 128))
        self.grid_pen_dark.setWidth(1)
        self.points_pen = QPen()
        self.points_pen.setWidth(1)
        self.func_pen = QPen()
        self.func_pen.setColor(QColor(0, 0, 255))
        self.func_pen.setWidth(3)
        self.diff_pen = QPen()
        self.diff_pen.setColor(QColor(128, 0, 128))
        self.diff_pen.setWidth(3)
        self.min_x = -20
        self.max_x = 20
        self.min_y = -15
        self.max_y = 15
        self.axis_intersection = (0, 0)
        self.points = []
        self.result = {
            "a": 0,
            "b": 0,
            "accuracy": 0
        }

    def set_parameters(self, rect: QRect):
        self.x, self.y, self.w, self.h = rect.x(), rect.y(), rect.width(), rect.height()

    def paintEvent(self, paintEvent: QPaintEvent):
        qp = QPainter()
        qp.begin(self)
        if self.points:
            coords_x = list(map(lambda point: point[0], self.points))
            coords_y = list(map(lambda point: point[1], self.points))
            self.min_x = min(coords_x) - (max(coords_x) - min(coords_x)) / 6
            self.max_x = max(coords_x) + (max(coords_x) - min(coords_x)) / 6
            self.min_y = min(coords_y) - (max(coords_y) - min(coords_y)) / 4
            self.max_y = max(coords_y) + (max(coords_y) - min(coords_y)) / 4
        else:
            self.min_x = -20
            self.max_x = 20
            self.min_y = -15
            self.max_y = 15
        self.drawAxes(qp)
        self.drawGrid(qp)
        self.drawPoints(qp)
        if not self.points:
            return
        params = self.calculateResult()
        self.drawFunction(qp, *params)
        qp.end()

    def drawAxes(self, p: QPainter):
        p.setPen(self.axis_pen)
        if self.min_x < 0 and self.max_x < 0:
            p.drawLine(self.w, 0, self.w, self.h)
            x = self.w
        elif self.min_x > 0 and self.max_x > 0:
            p.drawLine(0, 0, 0, self.h)
            x = 0
        else:
            start_point = self.calculateCanvasCoords(0, self.min_y)
            end_point = self.calculateCanvasCoords(0, self.max_y)
            x = start_point[0]
            p.drawLine(start_point[0], start_point[1], end_point[0], end_point[1])
        if self.min_y < 0 and self.max_y < 0:
            p.drawLine(0, 0, self.w, 0)
            y = 0
        elif self.min_y > 0 and self.max_y > 0:
            p.drawLine(0, self.h, self.w, self.h)
            y = self.h
        else:
            start_point = self.calculateCanvasCoords(self.min_x, 0)
            end_point = self.calculateCanvasCoords(self.max_x, 0)
            y = start_point[1]
            p.drawLine(start_point[0], start_point[1], end_point[0], end_point[1])
        self.axis_intersection = (x, y)

    def drawGrid(self, p: QPainter):
        p.setPen(self.grid_pen)
        inter_x, inter_y = self.axis_intersection
        start_x = inter_x % 16
        start_y = inter_y % 16
        for x in range(start_x, self.w, 16):
            p.drawLine(x, 0, x, self.h)
        for y in range(start_y, self.h, 16):
            p.drawLine(0, y, self.w, y)
        p.setPen(self.grid_pen_dark)
        start_x = inter_x % 80
        start_y = inter_y % 80
        for x in range(start_x, self.w, 80):
            p.drawLine(x, 0, x, self.h)
            textRect = QRect(x + 2, inter_y + 2 if inter_y <= self.h // 8 * 7 else inter_y - 14, self.w, self.h)
            p.drawText(textRect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                       f"{self.calculateRealCoords(x, inter_y)[0]:.2f}")
        for y in range(start_y, self.h, 80):
            p.drawLine(0, y, self.w, y)
            coords = self.calculateRealCoords(inter_x, y)
            if coords[1] == 0:
                continue
            if inter_x <= self.w // 8 * 7:
                textRect = QRect(inter_x + 2, y + 2, self.w, self.h)
                p.drawText(textRect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, f"{coords[1]:.2f}")
            else:
                textRect = QRect(0, y + 2, inter_x - 2, self.h)
                p.drawText(textRect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop, f"{coords[1]:.2f}")

    def setDrawnPoints(self, points):
        self.points = points

    def drawPoints(self, p: QPainter):
        p.setPen(self.points_pen)
        p.setBrush(QColor(0, 0, 0))
        for point in self.points:
            x, y = point
            cx, cy = self.calculateCanvasCoords(x, y)
            p.drawEllipse(cx - 2, cy - 2, 5, 5)

    def calculateResult(self):
        digits_x = max(map(lambda x: len(str(x[0])) - str(x[0]).find("."), self.points))
        digits_y = max(map(lambda x: len(str(x[1])) - str(x[1]).find("."), self.points))
        max_digits = max(digits_x, digits_y)
        p1 = sum(map(lambda x: x[0], self.points))
        p2 = sum(map(lambda x: x[1], self.points))
        p3 = sum(map(lambda x: x[0] ** 2, self.points))
        p4 = sum(map(lambda x: x[0] * x[1], self.points))
        p5 = len(self.points)
        # p3*a + p1*b = p4
        # p1*a + p5*b = p2
        diff = p3 / p1
        p1_, p2_, p5_ = p1 * diff, p2 * diff, p5 * diff
        div = p5_ - p1
        prod = p2_ - p4
        b = prod / div
        a = (p4 - p1 * b) / p3
        a = round(a, max_digits)
        b = round(b, max_digits)
        return a, b

    def drawFunction(self, p: QPainter, a, b):
        x1 = self.min_x
        y1 = a * x1 + b
        x2 = self.max_x
        y2 = a * x2 + b
        x1, y1 = self.calculateCanvasCoords(x1, y1)
        x2, y2 = self.calculateCanvasCoords(x2, y2)
        p.setPen(self.func_pen)
        p.drawLine(x1, y1, x2, y2)
        p.setPen(self.diff_pen)
        avg_y = sum(map(lambda pt: pt[1], self.points)) / len(self.points)
        real_diffs = 0
        pred_diffs = 0
        for point in self.points:
            x, y = point
            xr, yr = self.calculateCanvasCoords(x, y)
            xt, yt = x, a * x + b
            xtr, ytr = self.calculateCanvasCoords(xt, yt)
            p.drawLine(xr, yr, xtr, ytr)
            real_diffs += (y - avg_y) ** 2
            pred_diffs += (yt - avg_y) ** 2
        accuracy = pred_diffs / real_diffs
        print(accuracy)
        if accuracy < 0.4:
            self.result["accuracy"] = 2
        elif accuracy < 0.7:
            self.result["accuracy"] = 1
        else:
            self.result["accuracy"] = 0
        self.result["a"] = a
        self.result["b"] = b

    def calculateCanvasCoords(self, rx: float, ry: float):
        canvas_x = int(self.w * ((rx - self.min_x) / (self.max_x - self.min_x)))
        canvas_y = int(self.h * ((self.max_y - ry) / (self.max_y - self.min_y)))
        return canvas_x, canvas_y

    def calculateRealCoords(self, cx: int, cy: int):
        real_x = self.min_x + (self.max_x - self.min_x) * (cx / self.w)
        real_y = self.max_y - (self.max_y - self.min_y) * (cy / self.h)
        return real_x, real_y
