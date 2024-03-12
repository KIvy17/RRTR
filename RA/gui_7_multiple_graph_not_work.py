import sys
import random
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QLabel, QTextEdit, \
    QPushButton, QProgressBar, QDial
from PyQt5.QtCore import QTimer

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("РРТР")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Add tabs
        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, "РадиоАнализ")
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, "РадиоКонтроль")

        # Setup tab 1
        self.setup_tab1()

        # Setup tab 2
        self.setup_tab2()

    def setup_tab1(self):
        layout = QVBoxLayout()
        self.tab1.setLayout(layout)

        # Create dial slider
        self.dial = QDial()
        self.dial.setMinimum(20)
        self.dial.setMaximum(2000)
        self.dial.setSingleStep(10)
        self.dial.setValue(100)
        self.dial.valueChanged.connect(self.update_frequency)
        layout.addWidget(self.dial)

        # Create text label for showing frequency
        self.freq_label = QLabel("Frequency: 100 Hz")
        layout.addWidget(self.freq_label)

        # Create matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Animation setup
        self.x_data = np.linspace(0, 2 * np.pi, 100)
        self.line, = self.ax.plot(self.x_data, np.sin(self.x_data), '-')
        self.animation = FuncAnimation(self.figure, self.update_plot, frames=200, interval=50)

        # Create buttons for modulation (inactive for now)
        self.amplitude_button = QPushButton("Amplitude Modulation")
        self.amplitude_button.setEnabled(False)
        layout.addWidget(self.amplitude_button)

        self.phase_button = QPushButton("Phase Modulation")
        self.phase_button.setEnabled(False)
        layout.addWidget(self.phase_button)

        self.frequency_button = QPushButton("Frequency Modulation")
        self.frequency_button.setEnabled(False)
        layout.addWidget(self.frequency_button)

    def setup_tab2(self):
        layout = QVBoxLayout()
        self.tab2.setLayout(layout)

        # Create button for starting device setup
        self.setup_button = QPushButton("Начать настройку аппарата")
        self.setup_button.clicked.connect(self.start_setup)
        layout.addWidget(self.setup_button)

        # Create progress bar for device setup
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Create text edit for displaying random motto
        self.motto_edit = QTextEdit()
        self.motto_edit.setReadOnly(True)
        layout.addWidget(self.motto_edit)

        # Create button for restarting process
        self.restart_button = QPushButton("Начать заново")
        self.restart_button.clicked.connect(self.restart_process)
        layout.addWidget(self.restart_button)

    def update_frequency(self):
        freq = self.dial.value()
        self.freq_label.setText(f"Frequency: {freq} Hz")

    def update_plot(self, frame):
        self.line.set_ydata(np.sin(self.x_data + 0.1 * frame))
        return self.line,

    def start_setup(self):
        self.setup_button.setEnabled(False)
        self.progress_bar.setValue(0)
        for i in range(1, 11):
            self.progress_bar.setValue(i * 10)
            time.sleep(0.5)
        self.progress_bar.setValue(100)
        motto = " ".join(random.sample(["Доверяй, но проверяй", "Тише едешь – дальше будешь",
                                        "Глаза — зеркало души", "Без труда не выловишь и рыбку из пруда"], 4))
        self.motto_edit.setPlainText(motto)

    def restart_process(self):
        self.setup_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.motto_edit.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
