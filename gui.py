import sounddevice
from PyQt5.QtWidgets import *
from soundfilter import SoundFilter

class FilterWindow(QMainWindow):
    def __init__(self):
        super(FilterWindow, self).__init__()

        # Start a filter object
        self.filter = SoundFilter()

        self.originalPalette = QApplication.palette()
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(QPushButton("Save"))
        top_layout.addWidget(QPushButton("Save To"))
        top_layout.addWidget(QPushButton("Load"))
        top_layout.addWidget(QPushButton("Load From"))
        config_layout = QGridLayout()
        config_layout.addWidget(QLabel("Active Voice Level"), 0, 0)
        config_layout.addWidget(QDoubleSpinBox(), 1, 0)
        config_layout.addWidget(QLabel("Active Count"), 0, 1)
        config_layout.addWidget(QSpinBox(), 1, 1)
        config_layout.addWidget(QLabel("Starting Voice Frequency"), 2, 0)
        config_layout.addWidget(QSpinBox(), 3, 0)
        config_layout.addWidget(QLabel("Ending Voice Frequency"), 2, 1)
        config_layout.addWidget(QSpinBox(), 3, 1)

        # Add input APIs
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel("API"))
        self.input_apis = QComboBox()
        self.input_apis.activated.connect(self.input_api)
        for api in sounddevice.query_hostapis():
            self.input_apis.addItem(api.get('name'))
        input_layout.addWidget(self.input_apis)

        # Add output APIs
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("API"))
        self.output_apis = QComboBox()
        self.output_apis.activated.connect(self.output_api)
        for api in sounddevice.query_hostapis():
            self.output_apis.addItem(api.get('name'))
        output_layout.addWidget(self.output_apis)

        # Add input and output devices
        devices = sounddevice.query_devices()
        self.input_devices = QComboBox()
        self.input_devices.textActivated.connect(self.input_device)
        self.output_devices = QComboBox()
        self.output_devices.textActivated.connect(self.output_device)
        self.update_devices('input', 0)
        self.update_devices('output', 0)

        input_layout.addWidget(QLabel("Device"))
        input_layout.addWidget(self.input_devices)
        output_layout.addWidget(QLabel("Device"))
        output_layout.addWidget(self.output_devices)
        
        self.input_group_box = QGroupBox("Inputs")
        self.input_group_box.setLayout(input_layout)
        self.output_group_box = QGroupBox("Outputs")
        self.output_group_box.setLayout(output_layout)

        # Add start stop buttons
        bottom_layout = QHBoxLayout()
        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start)
        bottom_layout.addWidget(start_button)
        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.stop)
        bottom_layout.addWidget(stop_button)

        # Add everything together
        main_layout = QGridLayout()
        main_layout.addLayout(top_layout, 0, 0, 1, 3)
        main_layout.addLayout(config_layout, 1, 0, 1, 3)
        main_layout.addWidget(self.input_group_box, 2, 0)
        main_layout.addWidget(self.output_group_box, 2, 1)
        main_layout.addLayout(bottom_layout, 3, 0, 1, 3)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)

        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        self.setWindowTitle("Filter")
        self.change_style('Windows')

    def change_style(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
    
    def update_devices(self, kind, api):
        if kind == 'input':
            self.input_devices.clear()
        elif kind == 'output':
            self.output_devices.clear()

        devices = sounddevice.query_devices()
        for device_id in range(len(devices)):
            device = devices[device_id]
            if device.get("hostapi") == api:
                try:
                    if kind == 'input':
                        sounddevice.check_input_settings(device_id)
                        self.input_devices.addItem(device['name'])
                    elif kind == 'output':
                        sounddevice.check_output_settings(device_id)
                        self.output_devices.addItem(device['name'])
                except:
                    pass

    def start(self):
        self.filter.start()
        self.setWindowTitle("Running")
        
    def stop(self):
        self.filter.stop()
        self.setWindowTitle("Stopped")
    
    def input_api(self, index):
        self.update_devices('input', index)
        
    def output_api(self, index):
        self.update_devices('output', index)

    def input_device(self, input_device):
        self.filter.set_input(input_device, self.input_apis.currentIndex())
    
    def output_device(self, output_device):
        self.filter.set_output(output_device, self.output_apis.currentIndex())
    
    def load(self, path):
        pass

    def save(self, path):
        pass

app = QApplication([])
fw = FilterWindow()
fw.show()
app.exec_()