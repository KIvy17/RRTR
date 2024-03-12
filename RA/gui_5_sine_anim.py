import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class SinGraphAnimation(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.x_data = np.linspace(0, 2*np.pi, 100)
        self.line, = self.ax.plot(self.x_data, np.sin(self.x_data), '-')

        self.animation = FuncAnimation(self.figure, self.update_plot, frames=200, interval=50)

    def update_plot(self, frame):
        self.line.set_ydata(np.sin(self.x_data + 0.1 * frame))
        return self.line,

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SinGraphAnimation()
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle('Sine Graph Animation')
    window.show()
    sys.exit(app.exec_())
