import random
import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTabWidget, QComboBox, QSlider, QLabel, QDoubleSpinBox
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class SinGraphAnimation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.freq_carrier = 20  # Частота несущего сигнала
        self.freq_modulator = 10  # Частота модулируемого сигнала
        self.Fs = 600  # Частота дискретизации (Гц)
        self.T = 3  # Длительность сигнала (секунды)
        self.N = self.Fs * self.T  # Количество отсчётов
        self.modulation_index = 1.0
        self.t = np.linspace(1, self.T, self.N, endpoint=False)

        self.modulating_signal = lambda t: np.cos(np.pi * t * self.freq_modulator)
        self.carrier_signal = lambda t: np.sin(np.pi * self.freq_carrier * t)
        self.am_modulated_signal = lambda t: (1 + 0.5 * self.modulating_signal(t)) * self.carrier_signal(t)
        self.fm_modulated_signal = self.frequency_modulation
        # self.pm_modulated_signal = lambda t: np.sin(2 * np.pi * (self.freq_carrier * t + 0.5 * np.trapz(self.modulating_signal(t), t)))
        self.pm_modulated_signal = self.phase_modulation

        self.setup_ui()

    def frequency_modulation(self, t):
        modulator = np.sin(2.0 * np.pi * self.freq_modulator * t) * self.modulation_index
        product = np.zeros_like(modulator)

        for i, t in enumerate(t):
            product[i] = np.sin(2. * np.pi * (self.freq_carrier * t + modulator[i]))

        return product

    def phase_modulation(self, t):
        return np.cos(self.freq_carrier * np.pi * t + self.modulation_index * self.modulating_signal(t))

    def setup_ui(self):
        self.setWindowTitle('App')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignCenter)  # Center align the layout

        self.start_button = QPushButton("Начать анимацию")
        self.start_button.clicked.connect(self.start_animation)
        self.layout.addWidget(self.start_button)

        self.figure1, self.ax1 = plt.subplots(figsize=(8, 3))
        self.canvas1 = FigureCanvas(self.figure1)

        self.figure2, self.ax2 = plt.subplots(figsize=(8, 3))
        self.canvas2 = FigureCanvas(self.figure2)

        self.figure3, self.ax3 = plt.subplots(figsize=(8, 3))
        self.canvas3 = FigureCanvas(self.figure3)

        self.main_tab_widget = QTabWidget()
        self.main_tab_widget.hide()
        self.layout.addWidget(self.main_tab_widget)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.main_tab_widget.addTab(self.tab1, "Радиоанализ")
        self.main_tab_widget.addTab(self.tab2, "Радиоконтроль")

        self.tab1_layout = QVBoxLayout(self.tab1)
        self.tab1_sub_tab_widget = QTabWidget()
        self.tab1_sub_tab_widget.hide()
        self.tab1_layout.addWidget(self.tab1_sub_tab_widget)

        self.dynamic_tab = QWidget()
        self.static_tab = QWidget()
        self.tab1_sub_tab_widget.addTab(self.dynamic_tab, "Модуляция")
        self.tab1_sub_tab_widget.addTab(self.static_tab, "Спектр")

        self.dynamic_layout = QVBoxLayout(self.dynamic_tab)

        self.animation_started = False
        self.random_parameter = random.randint(1, 5)

        self.static_layout = QVBoxLayout(self.static_tab)
        self.plot_static_graphs()

    def plot_static_graphs(self, modulation_type=None, modulated_signal=None):
        if not modulation_type:
            current_modulation_type = 'Амплитудная'
            current_modulated_signal = self.am_modulated_signal
        else:
            current_modulation_type = modulation_type
            current_modulated_signal = modulated_signal

        am_freq_spectrum = np.abs(np.fft.fft(current_modulated_signal(self.t)))
        frequencies = np.fft.fftfreq(len(current_modulated_signal(self.t)), 1 / self.Fs)

        # Filter frequencies and spectrum for t > 0
        positive_indices = frequencies != 0
        positive_frequencies = frequencies[positive_indices]
        positive_am_freq_spectrum = am_freq_spectrum[positive_indices]

        fig1, self.static_ax1 = plt.subplots()
        self.static_ax1.plot(self.t, current_modulated_signal(self.t))
        self.static_ax1.set_title(f'{current_modulation_type} модуляция')
        self.static_ax1.set_xlabel(f'Время')
        self.static_ax1.set_ylabel(f'Частота')

        fig2, self.static_ax2 = plt.subplots()
        self.static_ax2.plot(positive_frequencies, positive_am_freq_spectrum)
        self.static_ax2.set_title(f'Спектр сигнала')
        self.static_ax2.set_xlabel(f'Частота')
        self.static_ax2.set_ylabel(f'Амплитуда')
        plt.setp(self.static_ax2, xlim=[-50, 50])

        canvas1 = FigureCanvas(fig1)
        canvas2 = FigureCanvas(fig2)

        self.static_layout.addWidget(canvas1)
        self.static_layout.addWidget(canvas2)

        # Close the figures to avoid runtime warning
        plt.close(fig1)
        plt.close(fig2)

    def start_animation(self, carrier_signal=None, modulating_signal=None, modulated=None, modulation_type=None):

        if not self.animation_started:
            self.animation_started = True

            if hasattr(self, "start_button") and self.start_button is not None:
                self.layout.removeWidget(self.start_button)
                self.start_button.deleteLater()
                self.start_button = None

                # self.refresh_button = QPushButton("Refresh Parameter")
                # self.refresh_button.clicked.connect(self.refresh_parameter)
                # Slider for carrier frequency
                self.freq_carrier_slider = QSlider(Qt.Horizontal)
                self.freq_carrier_slider.setMinimum(0)
                self.freq_carrier_slider.setMaximum(50)
                self.freq_carrier_slider.setValue(int(self.freq_carrier))
                self.freq_carrier_slider.valueChanged.connect(self.update_freq_carrier)

                # Create a QLabel to display the current value of the carrier frequency slider
                self.carrier_frequency_label = QLabel(str(self.freq_carrier_slider.value()))
                self.freq_carrier_slider.valueChanged.connect(self.update_carrier_frequency_label)

                self.dynamic_layout.addWidget(QLabel("Частота несущего сигнала, Гц"))
                self.dynamic_layout.addWidget(self.freq_carrier_slider)
                self.dynamic_layout.addWidget(self.carrier_frequency_label)  # Add the label below the slider

                # Slider for modulator frequency
                self.freq_modulator_slider = QSlider(Qt.Horizontal)
                self.freq_modulator_slider.setMinimum(0)
                self.freq_modulator_slider.setMaximum(50)
                self.freq_modulator_slider.setValue(int(self.freq_modulator))
                self.freq_modulator_slider.valueChanged.connect(self.update_freq_modulator)

                # Create a QLabel to display the current value of the modulator frequency slider
                self.modulator_frequency_label = QLabel(str(self.freq_modulator_slider.value()))
                self.freq_modulator_slider.valueChanged.connect(self.update_modulator_frequency_label)


                self.dynamic_layout.addWidget(QLabel("Частота модулирующего сигнала, Гц"))
                self.dynamic_layout.addWidget(self.freq_modulator_slider)
                self.dynamic_layout.addWidget(self.modulator_frequency_label)

                # Slider for modulation index
                self.modulation_index_slider = QSlider(Qt.Horizontal)
                self.modulation_index_slider.setMinimum(0)
                self.modulation_index_slider.setMaximum(10)
                self.modulation_index_slider.setValue(int(self.modulation_index))
                self.modulation_index_slider.valueChanged.connect(self.update_modulation_index)

                # Create a QLabel to display the current value of the modulator frequency slider
                self.modulation_index_label = QLabel(str(self.modulation_index_slider.value()))
                self.modulation_index_slider.valueChanged.connect(self.update_modulator_frequency_label)

                self.dynamic_layout.addWidget(QLabel("Коэффициент модуляции"))
                self.dynamic_layout.addWidget(self.modulation_index_slider)
                self.dynamic_layout.addWidget(self.modulation_index_label)

                # Dropdown to select graph type
                self.graph_type_combo = QComboBox()
                self.graph_type_combo.addItem("Амплитудная модуляция")
                self.graph_type_combo.addItem("Фазовая модуляция")
                self.graph_type_combo.addItem("Частотная модуляция")
                self.graph_type_combo.currentIndexChanged.connect(self.refresh_graphs)
                # self.dynamic_layout.insertWidget(0, self.refresh_button)
                self.dynamic_layout.insertWidget(0, self.graph_type_combo)
                self.tab1_layout.addWidget(self.tab1_sub_tab_widget)
                self.dynamic_layout.addWidget(self.canvas1)
                self.dynamic_layout.addWidget(self.canvas2)
                self.dynamic_layout.addWidget(self.canvas3)

            self.main_tab_widget.show()
            self.tab1_sub_tab_widget.show()

            if not carrier_signal:
                self.current_carrier_signal = self.carrier_signal
                self.current_modulating_signal = self.modulating_signal
                self.current_modulated_signal = self.am_modulated_signal
                self.current_modulation_type = 'Амплитудная'
            else:
                self.current_carrier_signal = carrier_signal
                self.current_modulating_signal = modulating_signal
                self.current_modulated_signal = modulated
                self.current_modulation_type = modulation_type

            self.random_parameter = np.random.randint(1, 9)  # Random parameter from 1 to 5
            self.line1, = self.ax1.plot(self.t, self.current_carrier_signal(self.t), '-')
            self.line2, = self.ax2.plot(self.t, self.current_modulating_signal(self.t), '-')
            self.line3, = self.ax3.plot(self.t, self.current_modulated_signal(self.t), '-')
            self.ax1.autoscale(enable=True, axis='both', tight=None)
            self.ax2.autoscale(enable=True, axis='both', tight=None)
            self.ax3.autoscale(enable=True, axis='both', tight=None)
            self.ax1.set_title(f'Несущий сигнал')
            self.ax2.set_title(f'Модулирующий сигнал')
            self.ax3.set_title(f'Модулированный сигнал')

            self.ax1.set_xlabel('Время')
            self.ax2.set_xlabel('Время')
            self.ax3.set_xlabel('Время')

            # Add y-labels
            self.ax1.set_ylabel('Частота')
            self.ax2.set_ylabel('Частота')
            self.ax3.set_ylabel('Частота')

            self.animation1 = FuncAnimation(self.figure1, self.update_plot1, frames=200, interval=50)
            self.animation2 = FuncAnimation(self.figure2, self.update_plot2, frames=200, interval=50)
            self.animation3 = FuncAnimation(self.figure3, self.update_plot3, frames=200, interval=50)

            self.animation1._start()
            self.animation2._start()
            self.animation3._start()

    def refresh_parameter(self):
        self.static_layout.removeWidget(self.static_layout.itemAt(0).widget())
        self.static_layout.removeWidget(self.static_layout.itemAt(0).widget())
        self.plot_static_graphs()

    def refresh_graphs(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.animation1.event_source.stop()
        self.animation2.event_source.stop()
        self.animation3.event_source.stop()

        self.static_layout.removeWidget(self.static_layout.itemAt(0).widget())
        self.static_layout.removeWidget(self.static_layout.itemAt(0).widget())
        self.static_ax1.clear()
        self.static_ax2.clear()

        self.animation_started = False
        graph_type = self.graph_type_combo.currentText()
        # self.animation_started = False  # Stop the current animation
        if graph_type == "Амплитудная модуляция":
            modulation_type = 'Амплитудная'
            self.start_animation(self.carrier_signal, self.modulating_signal, self.am_modulated_signal, modulation_type)  # Start a new animation
            self.plot_static_graphs(modulation_type, self.am_modulated_signal)
        elif graph_type == "Фазовая модуляция":
            modulation_type = 'Фазовая'
            self.start_animation(self.carrier_signal, self.modulating_signal, self.pm_modulated_signal, modulation_type)  # Start a new animation
            self.plot_static_graphs(modulation_type, self.pm_modulated_signal)
        elif graph_type == "Частотная модуляция":
            modulation_type = 'Частотная'
            self.start_animation(self.carrier_signal, self.modulating_signal, self.fm_modulated_signal, modulation_type)  # Start a new animation
            self.plot_static_graphs(modulation_type, self.fm_modulated_signal)

    def update_plot1(self, frame):
        new_y_data = self.current_carrier_signal(self.t + 0.01 * frame)
        self.line1.set_ydata(new_y_data)
        self.canvas1.draw_idle()

    def update_plot2(self, frame):
        new_y_data = self.current_modulating_signal(self.t + 0.01 * frame)
        self.line2.set_ydata(new_y_data)
        self.canvas2.draw_idle()

    def update_plot3(self, frame):
        new_y_data = self.current_modulated_signal(self.t + 0.01 * frame)
        self.line3.set_ydata(new_y_data)
        self.canvas3.draw_idle()

    def update_freq_carrier(self, value):
        self.freq_carrier = value
        if self.animation_started:
            self.start_animation(self.carrier_signal, self.modulating_signal, self.current_modulated_signal)
            self.static_layout.removeWidget(self.static_layout.itemAt(0).widget())
            self.static_layout.removeWidget(self.static_layout.itemAt(0).widget())
            self.static_ax1.clear()
            self.static_ax2.clear()
            self.plot_static_graphs(self.current_modulation_type, self.current_modulated_signal)

    def update_freq_modulator(self, value):
        self.freq_modulator = value
        if self.animation_started:
            self.start_animation(self.carrier_signal, self.modulating_signal, self.current_modulated_signal)
            self.static_layout.removeWidget(self.static_layout.itemAt(0).widget())
            self.static_layout.removeWidget(self.static_layout.itemAt(0).widget())
            self.static_ax1.clear()
            self.static_ax2.clear()
            self.plot_static_graphs(self.current_modulation_type, self.current_modulated_signal)

    def update_modulation_index(self, value):
        self.modulation_index = value
        if self.animation_started:
            self.start_animation(self.carrier_signal, self.modulating_signal, self.current_modulated_signal)
            self.static_layout.removeWidget(self.static_layout.itemAt(0).widget())
            self.static_layout.removeWidget(self.static_layout.itemAt(0).widget())
            self.static_ax1.clear()
            self.static_ax2.clear()
            self.plot_static_graphs(self.current_modulation_type, self.current_modulated_signal)

    def update_carrier_frequency_label(self, value):
        self.carrier_frequency_label.setText(str(value))

    def update_modulator_frequency_label(self, value):
        self.modulation_index_label.setText(str(value))

    def update_modulation_index_label(self, value):
        self.mo.setText(str(value))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SinGraphAnimation()
    window.setGeometry(600, 100, 800, 1200)  # Adjusted height to accommodate the tab widget
    # window.showMaximized()
    window.show()
    sys.exit(app.exec_())
