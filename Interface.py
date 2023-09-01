from PySide6.QtWidgets import *
from PySide6.QtGui import Qt


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 400, 200)
        self.img_path = QFileDialog().getOpenFileName()
        self.simulation_params = []

        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        self.times_per_one_pixel_spin = QSpinBox()
        self.times_per_one_pixel_spin.setRange(0, 1e6)
        self.times_per_one_pixel_spin.setValue(1250)
        times_per_one_pixel_label = QLabel("times_per_one_pixel")
        times_per_one_pixel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        times_per_one_pixel_layout = QHBoxLayout()
        times_per_one_pixel_layout.addWidget(times_per_one_pixel_label)
        times_per_one_pixel_layout.addWidget(self.times_per_one_pixel_spin)

        self.samples_per_nanosec_spin = QSpinBox()
        self.samples_per_nanosec_spin.setRange(0, 1e6)
        self.samples_per_nanosec_spin.setValue(5e3)
        samples_per_nanosec_label = QLabel("samples_per_nanosec")
        samples_per_nanosec_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        samples_per_nanosec_layout = QHBoxLayout()
        samples_per_nanosec_layout.addWidget(samples_per_nanosec_label)
        samples_per_nanosec_layout.addWidget(self.samples_per_nanosec_spin)

        self.ready_button = QPushButton("Ready")
        ready_layout = QHBoxLayout()
        ready_layout.addWidget(self.ready_button)

        main_layout.addLayout(times_per_one_pixel_layout)
        main_layout.addLayout(samples_per_nanosec_layout)
        main_layout.addLayout(ready_layout)


def set_parameters():
    app = QApplication()
    window = Window()
    window.show()
    window.ready_button.clicked.connect(app.quit)
    app.exec()

    return window.img_path[0], window.times_per_one_pixel_spin.value(), window.samples_per_nanosec_spin.value()


