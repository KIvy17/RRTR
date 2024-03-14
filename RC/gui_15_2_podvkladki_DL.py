import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTabWidget, QHBoxLayout, QComboBox, QTextEdit, QProgressBar, QSlider, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QFont

class CircularScale(QWidget):
    def __init__(self, parent=None):
        super(CircularScale, self).__init__(parent)
        self.setMinimumSize(200, 200)
        self.angle = 0
        self.rl_angle = None  # Угол для отрисовки радиолинии
        self.rl_color = Qt.red  # Цвет для отрисовки радиолинии
        self.peleng_value = None  # Значение пеленга

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

        painter.setPen(QPen(Qt.black, 4))
        painter.drawLine(0, 0, 30, 0)

        if self.rl_angle is not None:
            painter.setPen(QPen(Qt.black, 4))
            painter.save()
            painter.rotate(self.rl_angle)
            painter.drawLine(0, 0, 25, 0)
            painter.restore()

            # Отображение значения пеленга в круге
            if self.peleng_value is not None:
                painter.drawText(QRectF(-5, -55, 40, 20), Qt.AlignCenter, str(self.peleng_value))
                painter.drawText(QRectF(-15, -30, 60, 20), Qt.AlignCenter, "Пеленг")

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
        # Implementation of tab 1 setup
        pass

    def setup_tab2(self):
        layout = QVBoxLayout()
        self.tab2.setLayout(layout)

        # Create line edits for callsign and coordinates
        self.callsign_edit = QLineEdit()
        self.callsign_edit.setPlaceholderText("Введите позывной")
        layout.addWidget(self.callsign_edit)

        self.coordinates_edit = QLineEdit()
        self.coordinates_edit.setPlaceholderText("Введите координаты")
        layout.addWidget(self.coordinates_edit)

        # Create labels for displaying callsign and coordinates
        self.callsign_label = QLabel()
        self.coordinates_label = QLabel()

        # Add labels to layout
        layout.addWidget(self.callsign_label)
        layout.addWidget(self.coordinates_label)

        # Create button for starting device setup
        self.setup_button = QPushButton("Диагностика оборудования")
        self.setup_button.clicked.connect(self.start_setup)
        layout.addWidget(self.setup_button)

        # Create progress bar for device setup
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Create circular scale widget
        self.circular_scale = CircularScale()
        layout.addWidget(self.circular_scale)
        self.circular_scale.hide()

        # Create sliders for selecting frequency
        freq_slider_layout = QHBoxLayout()
        layout.addLayout(freq_slider_layout)

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
        self.modulation_combo.addItem("АM")
        self.modulation_combo.addItem("ФM")
        self.modulation_combo.addItem("ЧМ")
        layout.addWidget(self.modulation_combo)

        # Create button for starting search
        self.search_button = QPushButton("Поиск")
        self.search_button.setEnabled(False)
        self.search_button.clicked.connect(self.start_search)
        layout.addWidget(self.search_button)

        # Create button for starting search 2
        self.search_2_button = QPushButton("Поиск 2")
        self.search_2_button.setEnabled(False)
        self.search_2_button.clicked.connect(self.start_search_2)
        layout.addWidget(self.search_2_button)

        # Create text edit for displaying messages
        self.message_edit = QTextEdit()
        self.message_edit.setReadOnly(True)
        layout.addWidget(self.message_edit)

        # Add a new tab "Подавление" under "РадиоКонтроль"
        suppression_tab = QWidget()
        suppression_layout = QVBoxLayout(suppression_tab)
        suppression_tab.setLayout(suppression_layout)

        # Create buttons for suppression tab
        adaptive_button = QPushButton("Адаптивный режим")
        control_button = QPushButton("Контроль")
        reconnaissance_button = QPushButton("Доразведка")
        manual_button = QPushButton("Ручной режим")

        suppression_layout.addWidget(adaptive_button)
        suppression_layout.addWidget(control_button)
        suppression_layout.addWidget(reconnaissance_button)
        suppression_layout.addWidget(manual_button)

        self.tab_widget.addTab(suppression_tab, "Подавление")

    # Update start_setup method
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

    def update_freq_label(self, value):
        self.freq_label.setText(f"Выбранная частота: {value} МГц")

    def start_search(self):
        frequency = self.freq_slider.value()
        modulation = self.modulation_combo.currentText()

        # Список словарей с данными о частоте, модуляции, тексте и пеленге
        data_list = [
            {"Частота": 540, "Модуляция": "ЧМ", "Текст": "Ель, прием, я Ольха: сто двенадцать-двести двадцать четыре", "Пеленг": 120},
            {"Частота": 560, "Модуляция": "АM", "Текст": "Ольха, прием, я Ель: сто пятьдесят один-сто тридцать два", "Пеленг": 90},
            {"Частота": 1200, "Модуляция": "ФM", "Текст": "Олег, прием, я Молот: начинаю движение", "Пеленг": 225}
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
            {"Частота": 540, "Модуляция": "ЧМ", "Текст": "Ель, прием, я Ольха: сто двенадцать-двести двадцать четыре", "Пеленг": 120},
            {"Частота": 560, "Модуляция": "АM", "Текст": "Ольха, прием, я Ель: сто пятьдесят один-сто тридцать два", "Пеленг": 90},
            {"Частота": 1200, "Модуляция": "ФM", "Текст": "Олег, прием, я Молот: начинаю движение", "Пеленг": 225}
            # Добавьте другие словари с данными, если необходимо
        ]

        # Поиск данных для текущей модуляции в заданном диапазоне частот
        messages = []
        for data in data_list:
            if data["Модуляция"] == modulation:
                message = f"Частота: {data['Частота']} МГц\nТекст: {data['Текст']}\nПеленг: {data['Пеленг']} градусов"
                messages.append(message)

        # Вывод всех найденных сообщений
        if messages:
            self.message_edit.append(f"Найдена ценная информация для модуляции {modulation}:\n")
            for msg in messages:
                self.message_edit.append(msg)
        else:
            self.message_edit.append(f"Шифрованные данные для {modulation} модуляции и частоты {frequency} не найдены. \n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
