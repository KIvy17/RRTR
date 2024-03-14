import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QPoint, QRectF, QTime

class Clock(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Clock')
        self.setGeometry(200, 200, 300, 350)
        self.setStyleSheet("background : black;")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(360)
        self.slider.setValue(0)
        self.slider.setTickInterval(30)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.update)

    def paintEvent(self, event):
        rec = min(self.width(), self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(rec / 200, rec / 200)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.gray))

        rotation = self.slider.value()
        pointer = [QPoint(6, 7), QPoint(-6, 7), QPoint(0, -70)]

        painter.save()
        painter.rotate(rotation)
        painter.drawConvexPolygon(*pointer)
        painter.restore()

        painter.setPen(QPen(Qt.gray))
        for i in range(0, 360, 15):
            painter.drawLine(87, 0, 97, 0)
            painter.rotate(15)

        painter.end()

        self.slider.setGeometry(50, 250, 200, 30)

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = Clock()
    clock.show()
    sys.exit(app.exec_())
