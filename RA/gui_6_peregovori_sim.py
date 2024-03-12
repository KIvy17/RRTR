import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class SoundWaveSimulation(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.canvas = FigureCanvas(plt.figure(figsize=(8, 6)))
        self.layout.addWidget(self.canvas)

        self.x_data = np.linspace(0, 2 * np.pi, 1000)
        self.y_data = np.sin(self.x_data)
        self.line, = self.canvas.figure.subplots().plot(self.x_data, self.y_data, '-')
        self.animation = FuncAnimation(self.canvas.figure, self.update_plot, frames=200, interval=50)

    def update_plot(self, frame):
        # Generate synthetic audio data
        amplitude = 0.32 #np.random.rand()  # Random amplitude
        frequency = np.random.randint(25, 120)  # Random frequency
        phase = np.random.rand() * 2 * np.pi  # Random phase
        noise = np.random.normal(0, 0.1, len(self.x_data))  # Random noise
        audio_data = amplitude * np.sin(2 * np.pi * frequency * self.x_data + phase) + noise

        self.line.set_ydata(audio_data)
        return self.line,

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SoundWaveSimulation()
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle('Sound Wave Simulation')
    window.show()
    sys.exit(app.exec_())
