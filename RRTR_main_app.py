import random
import sys
from functools import partial

import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt, QTimer, QSize, QPoint
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTabWidget, QComboBox,
                             QSlider, QLabel, QDoubleSpinBox, QProgressBar, QLineEdit, QTextEdit,
                             QHBoxLayout, QSizePolicy, QRadioButton, QButtonGroup)
from PyQt5.QtGui import QPainter, QPen, QFont, QPixmap, QImage
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class CircularScale(QWidget):
    def __init__(self, parent=None):
        super(CircularScale, self).__init__(parent)
        self.angle = None
        self.rl_color = Qt.red
        self.peleng_value = None
        self.background_image = QPixmap("./img/map.jpg")  # Change to your image path
        self.setMinimumSize(self.background_image.size())
        self.distance_between = None

        # Initialize QTimer for blinking points
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_points)
        self.blink_state = True  # Initial state of blinking
        self.blink_timer.start(500)  # Adjust the interval as needed

    def toggle_points(self):
        # Toggle the state of blinking points
        self.blink_state = not self.blink_state
        self.update()

    def set_angle(self, angle):
        self.angle = angle
        self.update()  # Call update to trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the background image
        painter.drawPixmap(self.rect(), self.background_image)

        center = self.rect().center()
        if self.blink_state:
            painter.setPen(QPen(self.rl_color, 8))
            painter.drawPoint(center)
            if self.angle is not None:
                if self.distance_between is None:
                    self.distance_between = random.randint(150, 300)
                enemy_point = QPoint(
                    int(center.x() + self.distance_between * np.cos(self.angle * np.pi / 180)),
                    int(center.y() - self.distance_between * np.sin(self.angle * np.pi / 180))
                )

                painter.setPen(QPen(Qt.blue, 8))
                painter.drawPoint(enemy_point)

        else:
            painter.setPen(Qt.transparent)  # Make the point transparent

        # # Set viewport and window to encompass the background image and drawn items
        side = min(self.width() // 5, self.height() // 5)
        painter.setViewport((self.width() - side), (self.height() - side), side, side)
        painter.setWindow(-50, -50, 100, 100)

        # Draw circular scale
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
        self.harmonic_count = 1
        self.t = np.linspace(1, self.T, self.N, endpoint=False)

        self.modulating_signal = self.modulating_signal_func
        self.carrier_signal = lambda t, freq_carrier: np.sin(np.pi * freq_carrier * t)
        self.am_modulated_signal = self.amplitude_modulation
        self.fm_modulated_signal = self.frequency_modulation
        self.pm_modulated_signal = self.phase_modulation

        # WINDOW 2
        self.setMinimumSize(200, 200)
        self.angle = 0
        self.rl_angle = None  # Угол для отрисовки радиолинии
        self.rl_color = Qt.red  # Цвет для отрисовки радиолинии
        self.peleng_value = None  # Значение пеленга
        self.data_list = [
            {"Частота": 540, "Модуляция": "ЧМ", "Текст": "Ель, прием, я Ольха: сто двенадцать-двести двадцать четыре", "Пеленг": 120},
            {"Частота": 60, "Модуляция": "АМ", "Текст": "Ольха, прием, я Ель: сто пятьдесят один-сто тридцать два", "Пеленг": 90},
            {"Частота": 1200, "Модуляция": "ФМ", "Текст": "Олег, прием, я Молот: начинаю движение", "Пеленг": 225},
            {"Частота": 450, "Модуляция": "ЧМ", "Текст": "Roger roger, start operation immediately !", "Пеленг": 40}
            # Add other dictionaries as needed
        ]
        self.setup_ui()

    def modulating_signal_func(self, t, freq_modulator, harm_count=1):
        main_wave = np.cos(np.pi * t * freq_modulator)

        return main_wave + np.sum(0.5 ** k * np.cos(3 ** k * np.pi * t * freq_modulator) for k in range(1, harm_count))

    def amplitude_modulation(self, t, freq_carrier, freq_modulator, harm_count=1):
        return (1 + 0.5 * self.modulating_signal_func(t, freq_modulator, harm_count)) * self.carrier_signal(t, freq_carrier)

    def frequency_modulation(self, t, freq_carrier, freq_modulator, harm_count=1):
        modulator = self.modulating_signal_func(t, freq_modulator, harm_count)
        product = np.zeros_like(modulator)

        for i, t in enumerate(t):
            product[i] = np.sin(2. * np.pi * (freq_carrier * t + modulator[i]))

        return product

    def phase_modulation(self, t, freq_carrier, freq_modulator, harm_count=1):
        return np.cos(freq_carrier * np.pi * t + self.modulating_signal(t, freq_modulator, harm_count))

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

        self.control_tab = QWidget()

        self.tab2_layout = QVBoxLayout(self.tab2)
        self.tab2_sub_tab_widget = QTabWidget()
        self.tab2_sub_tab_widget.hide()
        self.tab2_layout.addWidget(self.tab2_sub_tab_widget)

        self.tab2_sub_tab_widget.addTab(self.control_tab, "Контроль")

        self.control_layer = QVBoxLayout(self.control_tab)

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

        # Create button for substituting 80% of characters
        self.supr_button = QPushButton("Подавление")
        self.supr_button.setEnabled(False)
        self.supr_button.clicked.connect(self.substitute_chars)
        self.control_layer.addWidget(self.supr_button)

        # Create text edit for displaying messages
        self.message_edit = QTextEdit()
        self.message_edit.setReadOnly(True)
        self.control_layer.addWidget(self.message_edit)

    def setup_test_tab(self):
        self.test_tab = QWidget()

        self.main_tab_widget.addTab(self.test_tab, "Тестирование")

        # Create start testing button
        self.start_testing_button = QPushButton("Начать тестирование")
        self.start_testing_button.clicked.connect(self.start_testing)

        # Add the button to the test tab
        self.test_tab_layout = QVBoxLayout(self.test_tab)
        self.test_tab_layout.addWidget(self.start_testing_button)

    def start_testing(self):

        self.tab1.setEnabled(False)
        self.tab2.setEnabled(False)

        if hasattr(self, "restart_button") and self.restart_button is not None:
            self.layout.removeWidget(self.restart_button)
            self.restart_button.deleteLater()
            self.restart_button = None
            self.result_label.deleteLater()
            self.current_question = 1
            self.user_answers = []
            self.correct_answer = []
            self.res = None

        if hasattr(self, "start_testing_button") and self.start_testing_button is not None:
            self.layout.removeWidget(self.start_testing_button)
            self.start_testing_button.deleteLater()
            self.start_testing_button = None
            self.current_question = 1
            self.user_answers = []
            self.correct_answer = []
            self.res = None

        if self.current_question == 1:
            # Create a figure for the plot
            fig_test_modulation, self.test_ax1 = plt.subplots(figsize=(5, 3))
            self.test_ax1.plot(self.t, self.am_modulated_signal(self.t, 20, 25, 3))
            self.test_ax1.set_xlabel(f'Время, с')
            self.test_ax1.set_ylabel(f'Амплитуда, дБ')
            # Add the figure to a canvas
            canvas_test = FigureCanvas(fig_test_modulation)
            self.test_tab_layout.addWidget(canvas_test)
            self.question_label = QLabel(
                f"Вопрос {self.current_question}: Получен сигнал, содержащий переговоры, перехваченный с \nпомощью SDRSharp. Определите используемый тип модуляции")
            self.answers = ["Амплитудная", "Частотная", "Фазовая"]  # Adjust as needed
            self.correct_answer.append("Амплитудная")
            self.radio_answers = True

        elif self.current_question in [2, 3]:
            am_freq_spectrum = np.abs(
                fft(self.am_modulated_signal(self.t, 20, 25, 3))
            )
            frequencies = fftfreq(self.N, 1 / self.Fs)
            fig_test_spectr, self.test_ax2 = plt.subplots()
            self.test_ax2.plot(frequencies * 3, am_freq_spectrum)
            self.test_ax2.set_title(f'Спектр сигнала')
            self.test_ax2.set_xlabel(f'Частота, МГц')
            self.test_ax2.set_ylabel(f'Амплитуда, дБ')
            plt.setp(self.test_ax2, xlim=[-100, 100])
            canvas_test = FigureCanvas(fig_test_spectr)
            self.test_tab_layout.addWidget(canvas_test)

            if self.current_question == 2:
                self.question_label = QLabel(
                    f"Вопрос {self.current_question}: Получен сигнал, содержащий переговоры, перехваченный с \nпомощью SDRSharp. "
                    f"Определите сколько гармоник в модулированном сигнале")
                self.answers = None
                self.correct_answer.append("3")
                self.radio_answers = False
            else:
                self.question_label = QLabel(
                    f"Вопрос {self.current_question}: Получен сигнал, содержащий переговоры, перехваченный с \nпомощью SDRSharp. "
                    f"Укажите частоту несущего сигнала")
                self.answers = ["10 МГц", "20 МГц", "45 МГц", "55 МГц", "90 МГц"]  # Adjust as needed
                self.correct_answer.append("20 МГц")
                self.radio_answers = True

        elif self.current_question == 4:
            self.question_label = QLabel(
                f"Вопрос {self.current_question}: Расположите в правильном порядке этапы технологии радиоразведки")
            self.answers = ["Обработка сигнала, Перехват сигнала, Восстановление информации",
                            "Перехват сигнала, Восстановление информации, Обработка сигнала",
                            "Перехват сигнала, Обработка сигнала, Восстановление информации",
                            "Нет правильного ответа"]  # Adjust as needed
            self.correct_answer.append("Перехват сигнала, Обработка сигнала, Восстановление информации")
            self.radio_answers = True

        elif self.current_question == 5:
            fig_test_modulation, self.test_ax3 = plt.subplots(figsize=(5, 3))
            self.test_ax3.plot(self.t, self.frequency_modulation(self.t, 15, 4, 1))
            self.test_ax3.set_xlabel(f'Время, с')
            self.test_ax3.set_ylabel(f'Амплитуда, дБ')
            canvas_test = FigureCanvas(fig_test_modulation)
            self.test_tab_layout.addWidget(canvas_test)
            self.question_label = QLabel(
                f"Вопрос {self.current_question}: Укажите тип модуляции")
            self.answers = None
            self.correct_answer.append("частотная")
            self.radio_answers = False

        elif self.current_question == 6:
            self.question_label = QLabel(
                f"Вопрос {self.current_question}: Укажите количество режимов работы РП-377 Л")
            self.answers = None
            self.correct_answer.append("3")
            self.radio_answers = False

        elif self.current_question == 7:
            self.question_label = QLabel(
                f"Вопрос {self.current_question}: Отметьте основные способы противодействия радиоразведке противника:")
            self.answers = [
                "Использование проводных каналов связи, Использование кодовых таблиц",
                "Использование ППРЧ, Использование УКВ радиостанций, Использование кодовых \n таблиц",
                "Использование ППРЧ, Использование проводных каналов связи",
                "Использование УКВ радиостанций, Использование кодовых \nтаблиц, Использование проводных каналов связи",
                "Использование проводных каналов связи"
            ]
            self.correct_answer.append("Использование проводных каналов связи, Использование кодовых таблиц")
            self.radio_answers = True

        elif self.current_question == 8:
            self.question_label = QLabel(
                f"Вопрос {self.current_question}: На каких частотах ведется поиск и обнаружение в комплексе РП-377 Л:")
            self.answers = [
                "от 20Мгц до 2000 МГц",
                "от 100 кГц до 100 ГГц",
                "от 1ГГц до 100 ГГц",
                "от 1кГц до 100 кГц",
            ]
            self.correct_answer.append("от 20Мгц до 2000 МГц")
            self.radio_answers = True

        elif self.current_question == 9:
            harm_count, self.test_ax4 = plt.subplots()
            self.test_ax4.plot(self.t, self.modulating_signal(self.t, 2, 3))
            self.test_ax4.set_title(f'Модулирующий сигнал')
            self.test_ax4.set_xlabel(f'Время, с')
            self.test_ax4.set_ylabel(f'Амплитуда, дБ')

            canvas_test = FigureCanvas(harm_count)
            self.test_tab_layout.addWidget(canvas_test)

            self.question_label = QLabel(
                f"Вопрос {self.current_question}: Сколько гармоник в модулирующем сигнале:")
            self.answers = None
            self.radio_answers = False
            self.correct_answer.append("3")

        elif self.current_question == 10:
            harm_count, self.test_ax4 = plt.subplots()
            self.test_ax4.plot(self.t, self.frequency_modulation(self.t, 20, 10, 1) + self.am_modulated_signal(self.t, 15, 4, 1))
            self.test_ax4.set_title(f'Модулированный сигнал')
            self.test_ax4.set_xlabel(f'Время, с')
            self.test_ax4.set_ylabel(f'Амплитуда, дБ')

            canvas_test = FigureCanvas(harm_count)
            self.test_tab_layout.addWidget(canvas_test)

            self.question_label = QLabel(
                f"Вопрос {self.current_question}: Какие модуляции применены к данному модулирующему сигналу")
            self.answers = ["Амплитудная, Фазовая", "Амплитудная, Частотная", "Частотная, Фазовая", "Амплитудная, Фазовая, Частотная"]
            self.radio_answers = True
            self.correct_answer.append("Амплитудная, Частотная")

        else:
            self.res = sum([user_answer == correct_answer for user_answer, correct_answer in zip(self.user_answers, self.correct_answer)])
            if self.res < 5:
                mark = 2
            elif 5 <= self.res < 7:
                mark = 3
            elif 7 <= self.res < 9:
                mark = 4
            else:
                mark = 5
            self.end_testing(mark, self.res)

        if self.res is None:
            # Create a layout for question and answers
            qa_layout = QVBoxLayout()
            self.test_tab_layout.addLayout(qa_layout)

            # Create question label
            qa_layout.addWidget(self.question_label)

            self.option_selected = False

            if self.radio_answers:
                # Create answer options
                for answer in self.answers:
                    self.answer_radio = QRadioButton(answer)
                    self.answer_radio.toggled.connect(self.update_option_selected)
                    qa_layout.addWidget(self.answer_radio)

            else:
                self.free_text_edit = QLineEdit()
                self.free_text_edit.setPlaceholderText("Введите ответ")
                self.free_text_edit.textChanged.connect(self.update_option_selected)
                qa_layout.addWidget(self.free_text_edit)

            # Set margins and spacing
            qa_layout.setContentsMargins(40, 100, 100, 100)  # Adjusted top margin to reduce gap
            qa_layout.setSpacing(30)  # Adjusted spacing between question and answers

            # Add submit button
            self.submit_button = QPushButton("Продолжить")
            self.submit_button.clicked.connect(self.submit_answer)
            self.test_tab_layout.addWidget(self.submit_button)
            self.submit_button.setEnabled(False)


    def update_option_selected(self, checked):
        if self.radio_answers:
            self.option_selected = any(radio.isChecked() for radio in self.findChildren(QRadioButton))
        else:
            self.option_selected = bool(self.free_text_edit.text())
        self.submit_button.setEnabled(self.option_selected)

    def store_answer(self, sender):
        if isinstance(sender, QRadioButton):
            if sender.isChecked():
                answer = sender.text()
                self.user_answers.append(answer)
        else:  # Assuming sender is QLineEdit for free text input
            answer = sender.text().strip().lower()
            self.user_answers.append(answer)

    def submit_answer(self):
        if self.radio_answers:
            for radio in self.findChildren(QRadioButton):
                self.store_answer(radio)
        else:
            self.store_answer(self.free_text_edit)

        self.current_question += 1
        print(f"Answer for question {self.current_question}: {self.user_answers}")
        self.clear_layout(self.test_tab_layout)
        self.start_testing()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def end_testing(self, mark, correct_answers):

        self.tab1.setEnabled(True)
        self.tab2.setEnabled(True)
        self.result_label = QLabel(f"{correct_answers}/10 правильных ответов. Ваш результат: {mark}.")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.test_tab_layout.addWidget(self.result_label)

        self.restart_button = QPushButton("Начать тестирование снова")
        self.restart_button.clicked.connect(self.start_testing)
        self.test_tab_layout.addWidget(self.restart_button)
        self.current_question = 1


    def setup_ui(self):
        self.setWindowTitle('App')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignCenter)  # Center align the layout

        self.setup_tab1()
        self.setup_tab2()
        self.setup_test_tab()

    def plot_static_graphs(self, modulation_type=None, modulated_signal=None):
        if not modulation_type:
            current_modulation_type = 'Амплитудная'
            current_modulated_signal = self.am_modulated_signal
        else:
            current_modulation_type = modulation_type
            current_modulated_signal = modulated_signal

        am_freq_spectrum = np.abs(fft(current_modulated_signal(self.t, self.freq_carrier, self.freq_modulator, self.harmonic_count)))
        frequencies = fftfreq(self.N, 1 / self.Fs)

        fig1, self.static_ax1 = plt.subplots()
        self.static_ax1.plot(self.t, current_modulated_signal(self.t, self.freq_carrier, self.freq_modulator, self.harmonic_count))
        self.static_ax1.set_title(f'{current_modulation_type} модуляция')
        self.static_ax1.set_xlabel(f'Время, с')
        self.static_ax1.set_ylabel(f'Амплитуда, дБ')

        fig2, self.static_ax2 = plt.subplots()
        self.static_ax2.plot(frequencies * 3, am_freq_spectrum)
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
                self.freq_carrier_slider.setMaximum(30)
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
                self.freq_modulator_slider.setMaximum(30)
                self.freq_modulator_slider.setValue(int(self.freq_modulator))
                self.freq_modulator_slider.valueChanged.connect(self.update_freq_modulator)

                # Create a QLabel to display the current value of the modulator frequency slider
                self.modulator_frequency_label = QLabel(str(self.freq_modulator_slider.value()))
                self.freq_modulator_slider.valueChanged.connect(self.update_modulator_frequency_label)

                self.dynamic_layout.addWidget(QLabel("Частота модулирующего сигнала, МГц"))
                self.dynamic_layout.addWidget(self.freq_modulator_slider)
                self.dynamic_layout.addWidget(self.modulator_frequency_label)

                # Slider for modulation index
                self.harmonic_count_slider = QSlider(Qt.Horizontal)
                self.harmonic_count_slider.setMinimum(1)
                self.harmonic_count_slider.setMaximum(5)
                self.harmonic_count_slider.setValue(int(self.harmonic_count))
                self.harmonic_count_slider.valueChanged.connect(self.update_harmonic_count)

                # Create a QLabel to display the current value of the modulator frequency slider
                self.harmonic_count_label = QLabel(str(self.harmonic_count_slider.value()))
                self.harmonic_count_slider.valueChanged.connect(self.update_harmonic_count_label)

                self.dynamic_layout.addWidget(QLabel("Количество гармоник"))
                self.dynamic_layout.addWidget(self.harmonic_count_slider)
                self.dynamic_layout.addWidget(self.harmonic_count_label)

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
            self.line1, = self.ax1.plot(self.t, self.current_carrier_signal(self.t, self.freq_carrier), '-')
            self.line2, = self.ax2.plot(self.t, self.current_modulating_signal(self.t, self.freq_modulator, self.harmonic_count), '-')
            self.line3, = self.ax3.plot(self.t, self.current_modulated_signal(self.t, self.freq_carrier, self.freq_modulator, self.harmonic_count), '-')
            self.ax1.autoscale(enable=True, axis='both', tight=None)
            self.ax2.autoscale(enable=True, axis='both', tight=None)
            self.ax3.autoscale(enable=True, axis='both', tight=None)
            plt.setp(self.ax2, ylim=[-2, 2])
            plt.setp(self.ax3, ylim=[-2, 2])
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
        new_y_data = self.current_carrier_signal(self.t + 0.01 * frame, self.freq_carrier)
        self.line1.set_ydata(new_y_data)
        self.canvas1.draw_idle()

    def update_plot2(self, frame):
        new_y_data = self.current_modulating_signal(self.t + 0.01 * frame, self.freq_modulator, self.harmonic_count)
        self.line2.set_ydata(new_y_data)
        self.canvas2.draw_idle()

    def update_plot3(self, frame):
        new_y_data = self.current_modulated_signal(self.t + 0.01 * frame, self.freq_carrier, self.freq_modulator, self.harmonic_count)
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

    def update_harmonic_count(self, value):
        self.harmonic_count = value
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

    def update_harmonic_count_label(self, value):
        self.harmonic_count_label.setText(str(value))

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
        if value < 20:
            value += 10
            self.progress_bar.setValue(value)
        else:
            self.setup_button.setEnabled(True)
            self.freq_slider.setEnabled(True)
            self.modulation_combo.setEnabled(True)
            self.search_button.setEnabled(True)
            self.search_2_button.setEnabled(True)
            self.supr_button.setEnabled(True)
            self.timer.stop()
            self.setup_button.hide()
            self.circular_scale.show()
            self.progress_bar.hide()

    def start_search(self):
        frequency = self.freq_slider.value()
        modulation = self.modulation_combo.currentText()
        self.message_edit.clear()

        message = "Информативного сигнала не обнаружено.\n"
        for data in self.data_list:
            if data["Частота"] == frequency and data["Модуляция"] == modulation:
                message = f"Частота: {data['Частота']} МГц\nТекст: {data['Текст']}\nПеленг: {data['Пеленг']} градусов\n"
                break

        self.message_edit.append(message)

    def start_search_2(self):
        modulation = self.modulation_combo.currentText()
        self.message_edit.clear()

        self.message_edit.append(f"Начинаю циклический поиск по заданному диапазону частот, по заданной модуляции.")
        messages = []
        found_frequency = None  # Переменная для хранения пойманной частоты
        for data in self.data_list:
            if data["Модуляция"] == modulation:
                message = f"Частота: {data['Частота']} МГц\nТекст: {data['Текст']}\nПеленг: {data['Пеленг']} градусов"
                self.circular_scale.set_angle(90 - data['Пеленг'])
                messages.append(message)
                found_frequency = data['Частота']  # Сохраняем пойманную частоту

        if messages:
            self.message_edit.append(f"Найдена ценная информация для модуляции {modulation}:\n")
            for msg in messages:
                QTimer.singleShot(1000, partial(self.message_edit.append, msg))
        else:
            self.message_edit.append(
                f"Шифрованные данные для {modulation} модуляции и частоты {found_frequency} не найдены.\n")

        if found_frequency is not None:
            QTimer.singleShot(1000, partial(self.freq_slider.setValue,
                                            found_frequency))  # Устанавливаем значение слайдера частоты на пойманную частоту

    def substitute_chars(self):
        frequency = self.freq_slider.value()
        modulation = self.modulation_combo.currentText()

        for data in self.data_list:
            if data["Частота"] == frequency and data["Модуляция"] == modulation:
                text = data["Текст"]
                length = len(text)
                num_chars_to_replace = int(length * 0.8)
                indices_to_replace = random.sample(range(length), num_chars_to_replace)
                new_text = ''.join(c if i not in indices_to_replace else '*' for i, c in enumerate(text))
                data["Текст"] = new_text
                self.message_edit.append(f" Подавление частоты {frequency} МГц и модуляции '{modulation}'")
                break

       
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SinGraphAnimation()
    window.setGeometry(600, 100, 800, 1200)  # Adjusted height to accommodate the tab widget
    window.setWindowTitle("РРТР")

    # window.showMaximized()
    window.show()
    sys.exit(app.exec_())
