import random
import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTabWidget, QComboBox,
                             QSlider, QLabel, QDoubleSpinBox, QProgressBar, QLineEdit, QTextEdit,
                             QHBoxLayout, )
from PyQt5.QtGui import QPainter, QPen, QFont
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class CircularScale(QWidget):
    def __init__(self, parent=None):
        super(CircularScale, self).__init__(parent)
        self.setMinimumSize(200, 200)
        self.angle = None
        # self.rl_angle = None  # Угол для отрисовки радиолинии
        self.rl_color = Qt.red  # Цвет для отрисовки радиолинии
        self.peleng_value = None  # Значение пеленга

    def set_angle(self, angle):
        self.angle = angle
        self.update()  # Call update to trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        side = min(self.width(), self.height())
        painter.setViewport((self.width() - side) // 2, (self.height() - side) // 2, side, side)
        painter.setWindow(-50, -50, 100, 100)

        scale = 360 / 23  # 360 degrees divided into 24 segments (15 degrees each)
        step = 15
        painter.setPen(QPen(Qt.black, 2))
        font = QFont('Serif', 8)
        painter.setFont(font)
        for i in range(0, 360, step):
            painter.drawLine(40, 0, 45, 0)
            painter.rotate(step)

        if self.angle is not None:
            painter.save()
            painter.setPen(QPen(self.rl_color, 4))
            painter.rotate(360 - self.angle)
            painter.drawLine(0, 0, 25, 0)
            painter.restore()
        else:
            painter.setPen(QPen(Qt.black, 4))
            painter.drawLine(0, 0, 0, -30)


        # Отображение значения пеленга в круге
        if self.peleng_value is not None:
            painter.drawText(QRectF(-5, -55, 40, 20), Qt.AlignCenter, str(self.peleng_value))
            painter.drawText(QRectF(-15, -30, 60, 20), Qt.AlignCenter, "Пеленг")




class SinGraphAnimation(QMainWindow):
    def __init__(self):
        super().__init__()
        # WINDOW 1
        self.freq_carrier = 20  # Частота несущего сигнала
        self.freq_modulator = 10  # Частота модулируемого сигнала
        self.Fs = 1000  # Частота дискретизации (МГц)
        self.T = 3  # Длительность сигнала (секунды)
        self.N = self.Fs * self.T  # Количество отсчётов
        self.modulation_index = 1.0
        self.t = np.linspace(1, self.T, self.N, endpoint=False)

        self.modulating_signal = lambda t: np.cos(np.pi * t * self.freq_modulator)
        self.carrier_signal = lambda t: np.sin(np.pi * self.freq_carrier * t)
        self.am_modulated_signal = lambda t: (1 + 0.5 * self.modulating_signal(t)) * self.carrier_signal(t)
        self.fm_modulated_signal = self.frequency_modulation
        self.pm_modulated_signal = self.phase_modulation

        # WINDOW 2
        self.setMinimumSize(200, 200)
        self.angle = 0
        self.rl_angle = None  # Угол для отрисовки радиолинии
        self.rl_color = Qt.red  # Цвет для отрисовки радиолинии
        self.peleng_value = None  # Значение пеленга

        self.setup_ui()

    def frequency_modulation(self, t):
        modulator = np.sin(np.pi * self.freq_modulator * t) * self.modulation_index
        product = np.zeros_like(modulator)

        for i, t in enumerate(t):
            product[i] = np.sin(2. * np.pi * (self.freq_carrier * t + modulator[i]))

        return product

    def phase_modulation(self, t):
        return np.cos(self.freq_carrier * np.pi * t + self.modulation_index * self.modulating_signal(t))

    def setup_tab1(self):

        self.tab1 = QWidget()

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

        self.main_tab_widget.addTab(self.tab1, "Радиоанализ")

        self.dynamic_tab = QWidget()
        self.static_tab = QWidget()

        self.tab1_layout = QVBoxLayout(self.tab1)
        self.tab1_sub_tab_widget = QTabWidget()
        self.tab1_sub_tab_widget.hide()
        self.tab1_layout.addWidget(self.tab1_sub_tab_widget)

        self.tab1_sub_tab_widget.addTab(self.dynamic_tab, "Модуляция")
        self.tab1_sub_tab_widget.addTab(self.static_tab, "Спектр")

        self.dynamic_layout = QVBoxLayout(self.dynamic_tab)

        self.animation_started = False
        self.random_parameter = random.randint(1, 5)

        self.static_layout = QVBoxLayout(self.static_tab)
        self.plot_static_graphs()

    def setup_tab2(self):
        self.tab2 = QWidget()

        self.main_tab_widget.addTab(self.tab2, "Радиоконтроль")

        self.suppresion_tab = QWidget()
        self.control_tab = QWidget()

        self.tab2_layout = QVBoxLayout(self.tab2)
        self.tab2_sub_tab_widget = QTabWidget()
        self.tab2_sub_tab_widget.hide()
        self.tab2_layout.addWidget(self.tab2_sub_tab_widget)

        self.tab2_sub_tab_widget.addTab(self.control_tab, "Контроль")
        self.tab2_sub_tab_widget.addTab(self.suppresion_tab, "Подавление")


        self.control_layer = QVBoxLayout(self.control_tab)
        self.suppresion_layer = QVBoxLayout(self.suppresion_tab)

        # Create line edits for callsign and coordinates
        self.callsign_edit = QLineEdit()
        self.callsign_edit.setPlaceholderText("Введите позывной")

        self.control_layer.addWidget(self.callsign_edit)

        self.coordinates_edit = QLineEdit()
        self.coordinates_edit.setPlaceholderText("Введите координаты")
        self.control_layer.addWidget(self.coordinates_edit)

        # Create labels for displaying callsign and coordinates
        self.callsign_label = QLabel()
        self.coordinates_label = QLabel()

        # Add labels to layout
        self.control_layer.addWidget(self.callsign_label)
        self.control_layer.addWidget(self.coordinates_label)

        # Create button for starting device setup
        self.setup_button = QPushButton("Диагностика оборудования")
        self.setup_button.clicked.connect(self.start_setup)
        self.control_layer.addWidget(self.setup_button)

        # Create progress bar for device setup
        self.progress_bar = QProgressBar()
        self.control_layer.addWidget(self.progress_bar)

        # Create circular scale widget
        self.circular_scale = CircularScale()
        self.control_layer.addWidget(self.circular_scale)
        self.circular_scale.hide()

        # Create sliders for selecting frequency
        freq_slider_layout = QHBoxLayout()
        self.control_layer.addLayout(freq_slider_layout)

        self.freq_label = QLabel("Выбранная частота: 20 МГц")
        freq_slider_layout.addWidget(self.freq_label)

        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setMinimum(20)
        self.freq_slider.setMaximum(2000)
        self.freq_slider.setValue(20)
        self.freq_slider.setTickInterval(100)
        self.freq_slider.setTickPosition(QSlider.TicksBelow)
        self.freq_slider.valueChanged.connect(self.update_freq_label)
        freq_slider_layout.addWidget(self.freq_slider)

        # Create combo box for selecting modulation type
        self.modulation_combo = QComboBox()
        self.modulation_combo.addItem("АМ")
        self.modulation_combo.addItem("ЧМ")
        self.modulation_combo.addItem("ФМ")
        self.control_layer.addWidget(self.modulation_combo)

        # Create button for starting search
        self.search_button = QPushButton("Поиск")
        self.search_button.setEnabled(False)
        self.search_button.clicked.connect(self.start_search)
        self.control_layer.addWidget(self.search_button)

        # Create button for starting search 2
        self.search_2_button = QPushButton("Поиск 2")
        self.search_2_button.setEnabled(False)
        self.search_2_button.clicked.connect(self.start_search_2)
        self.control_layer.addWidget(self.search_2_button)

        # Create text edit for displaying messages
        self.message_edit = QTextEdit()
        self.message_edit.setReadOnly(True)
        self.control_layer.addWidget(self.message_edit)

        # Create buttons for suppression tab
        adaptive_button = QPushButton("Адаптивный режим")
        control_button = QPushButton("Контроль")
        reconnaissance_button = QPushButton("Доразведка")
        manual_button = QPushButton("Ручной режим")

        self.suppresion_layer.addWidget(adaptive_button)
        self.suppresion_layer.addWidget(control_button)
        self.suppresion_layer.addWidget(reconnaissance_button)
        self.suppresion_layer.addWidget(manual_button)

    def setup_ui(self):
        self.setWindowTitle('App')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignCenter)  # Center align the layout

        self.setup_tab1()
        self.setup_tab2()


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
        self.static_ax1.set_xlabel(f'Время, с')
        self.static_ax1.set_ylabel(f'Частота, МГц')

        fig2, self.static_ax2 = plt.subplots()
        self.static_ax2.plot(positive_frequencies, positive_am_freq_spectrum)
        self.static_ax2.set_title(f'Спектр сигнала')
        self.static_ax2.set_xlabel(f'Частота, МГц')
        self.static_ax2.set_ylabel(f'Амплитуда, дБ')
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

                self.freq_carrier_slider = QSlider(Qt.Horizontal)
                self.freq_carrier_slider.setMinimum(0)
                self.freq_carrier_slider.setMaximum(50)
                self.freq_carrier_slider.setValue(int(self.freq_carrier))
                self.freq_carrier_slider.valueChanged.connect(self.update_freq_carrier)

                # Create a QLabel to display the current value of the carrier frequency slider
                self.carrier_frequency_label = QLabel(str(self.freq_carrier_slider.value()))
                self.freq_carrier_slider.valueChanged.connect(self.update_carrier_frequency_label)

                self.dynamic_layout.addWidget(QLabel("Частота несущего сигнала, МГц"))
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

                self.dynamic_layout.addWidget(QLabel("Частота модулирующего сигнала, МГц"))
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
                self.modulation_index_slider.valueChanged.connect(self.update_modulation_index_label)

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
            self.tab2_sub_tab_widget.show()

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
            self.ax1.set_ylabel('Амплитуда, дБ')
            self.ax2.set_ylabel('Амплитуда, дБ')
            self.ax3.set_ylabel('Амплитуда, дБ')

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
        self.modulator_frequency_label.setText(str(value))

    def update_modulation_index_label(self, value):
        self.modulation_index_label.setText(str(value))

    def update_freq_label(self, value):
        self.freq_label.setText(f"Выбранная частота: {value} МГц")

    def start_setup(self):
        # Get callsign and coordinates entered by the user
        callsign = self.callsign_edit.text()
        coordinates = self.coordinates_edit.text()

        if callsign.strip() == "" or coordinates.strip() == "":
            self.message_edit.append("Введите позывной и координаты.")
            return

        # Display callsign and coordinates
        self.callsign_label.setText("Позывной: " + callsign)
        self.coordinates_label.setText("Координаты: " + coordinates)

        # Proceed with device setup
        self.setup_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(500)

    def update_progress(self):
        value = self.progress_bar.value()
        if value < 100:
            value += 10
            self.progress_bar.setValue(value)
        else:
            self.setup_button.setEnabled(True)
            self.freq_slider.setEnabled(True)
            self.modulation_combo.setEnabled(True)
            self.search_button.setEnabled(True)
            self.search_2_button.setEnabled(True)
            self.timer.stop()
            self.setup_button.hide()
            self.circular_scale.show()
            self.progress_bar.hide()

    def start_search(self):
        frequency = self.freq_slider.value()
        modulation = self.modulation_combo.currentText()

        # Список словарей с данными о частоте, модуляции, тексте и пеленге
        data_list = [
            {"Частота": 540, "Модуляция": "ЧМ", "Текст": "Ель, прием, я Ольха: сто двенадцать-двести двадцать четыре",
             "Пеленг": 120},
            {"Частота": 560, "Модуляция": "АM", "Текст": "Ольха, прием, я Ель: сто пятьдесят один-сто тридцать два",
             "Пеленг": 90},
            {"Частота": 1200, "Модуляция": "ФМ", "Текст": "Олег, прием, я Молот: начинаю движение", "Пеленг": 225}
            # Добавьте другие словари с данными, если необходимо
        ]

        # Поиск данных по частоте и модуляции в списке
        for data in data_list:
            if data["Частота"] == frequency and data["Модуляция"] == modulation:
                message = f"Найдена ценная информация!астота: {frequency} МГц\nМодуляция: {modulation}\nТекст: {data['Текст']}\nПеленг: {data['Пеленг']} градусов"
                break
        else:
            message = "Шифрованные данные для данной частоты и модуляции не найдены.\n"

        self.message_edit.append(message)

    def start_search_2(self):
        frequency = self.freq_slider.value()  # Получаем текущее значение частоты
        modulation = self.modulation_combo.currentText()
        # Список словарей с данными о частоте, модуляции, тексте и пеленге
        data_list = [
            {"Частота": 540, "Модуляция": "ЧМ", "Текст": "Ель, прием, я Ольха: сто двенадцать-двести двадцать четыре",
             "Пеленг": 120},
            {"Частота": 560, "Модуляция": "АМ", "Текст": "Ольха, прием, я Ель: сто пятьдесят один-сто тридцать два",
             "Пеленг": 90},
            {"Частота": 1200, "Модуляция": "ФМ", "Текст": "Олег, прием, я Молот: начинаю движение", "Пеленг": 225}
            # Добавьте другие словари с данными, если необходимо
        ]

        # Вывод сообщения о начале циклического поиска
        # self.message_edit.append(f"Начинаю циклический поиск по заданному диапазону частот, по заданной модуляции.")
        # QTimer.singleShot(7000)  # Задержка перед выводом результатов - 7 секунд
        messages = []
        for data in data_list:
            if data["Модуляция"] == modulation:
                message = f"Частота: {data['Частота']} МГц\nТекст: {data['Текст']}\nПеленг: {data['Пеленг']} градусов"
                self.circular_scale.set_angle(data['Пеленг'])
                # Need to change angle of CircularScale to ata['Пеленг'] angles
                messages.append(message)

        # Вывод всех найденных сообщений с задержкой

        if messages:
            self.message_edit.append(f"Найдена ценная информация для модуляции {modulation}:")
            for msg in messages:
                QTimer.singleShot(1000,
                                  lambda msg=msg: self.message_edit.append(msg))  # Добавление задержки 1000 мс (1 с)
        else:
            self.message_edit.append(f"Шифрованные данные для {modulation} модуляции и частоты {frequency} не найдены.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SinGraphAnimation()
    window.setGeometry(600, 100, 800, 1200)  # Adjusted height to accommodate the tab widget
    window.setWindowTitle("РРТР")
    # window.showMaximized()
    window.show()
    sys.exit(app.exec_())
