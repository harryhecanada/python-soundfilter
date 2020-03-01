import sounddevice
from PyQt5.QtWidgets import *


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super(FilterDialog, self).__init__(parent)

        self.originalPalette = QApplication.palette()

        top_layout = QHBoxLayout()
        top_layout.addWidget(QPushButton("Save"))
        top_layout.addWidget(QPushButton("Save To"))
        top_layout.addWidget(QPushButton("Load"))
        top_layout.addWidget(QLabel("active-level"))
        top_layout.addWidget(QSpinBox())
        top_layout.addWidget(QLabel("start"))
        top_layout.addWidget(QSpinBox())
        top_layout.addWidget(QLabel("end"))
        top_layout.addWidget(QSpinBox())

        input_layout = QVBoxLayout()
        output_layout = QVBoxLayout()
        devices = sounddevice.query_devices()
        for device in devices:
            if device.get("hostapi") == 0:
                if device.get("max_input_channels") > 0:
                    input_layout.addWidget(QRadioButton(device.get("name", "unknown")))
                elif device.get("max_output_channels") > 0:
                    output_layout.addWidget(QRadioButton(device.get("name", "unknown")))
        
        self.input_group_box = QGroupBox("Inputs")
        self.input_group_box.setLayout(input_layout)
        self.output_group_box = QGroupBox("Outputs")
        self.output_group_box.setLayout(output_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QPushButton("Start"))
        bottom_layout.addWidget(QPushButton("Stop"))

        main_layout = QGridLayout()
        main_layout.addLayout(top_layout, 0, 0, 1, 2)
        main_layout.addWidget(self.input_group_box, 1, 0)
        main_layout.addWidget(self.output_group_box, 1, 1)
        main_layout.addLayout(bottom_layout, 2, 0, 1, 2)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        self.setLayout(main_layout)

        self.setWindowTitle("Filter")
        self.change_style('Windows')

    def change_style(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

app = QApplication([])
filter_dialog = FilterDialog()
filter_dialog.show()
app.exec_()