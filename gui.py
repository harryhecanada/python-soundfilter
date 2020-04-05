import sounddevice
import PyQt5.QtWidgets as qw
from soundfilter import SoundFilter
from settings import settings


class FilterWindow(qw.QMainWindow):
    def __init__(self):
        super(FilterWindow, self).__init__()

        # Start a filter object
        self.filter = SoundFilter()

        self.originalPalette = qw.QApplication.palette()
        
        top_layout = qw.QHBoxLayout()
        self.save = qw.QPushButton("Save Settings")
        self.save.clicked.connect(self.save_settings)
        self.load = qw.QPushButton("Load Settings")
        self.load.clicked.connect(self.load_settings)
        self.default = qw.QPushButton("Load Defaults")
        self.default.clicked.connect(self.default_settings)
        top_layout.addWidget(self.save)
        top_layout.addWidget(self.load)
        top_layout.addWidget(self.default)
        config_layout = qw.QGridLayout()

        config_layout.addWidget(qw.QLabel("Active Voice Level"), 0, 0)
        self.active_voice_level = qw.QDoubleSpinBox()
        self.active_voice_level.setValue(settings['active-level'])
        self.active_voice_level.setMinimum(0.0)
        self.active_voice_level.valueChanged.connect(self.set_active_voice_level)
        config_layout.addWidget(self.active_voice_level, 1, 0)

        config_layout.addWidget(qw.QLabel("Active Count"), 0, 1)
        self.active_count = qw.QSpinBox()
        self.active_count.setValue(settings['active-count'])
        self.active_count.setMinimum(1)
        self.active_count.valueChanged.connect(self.set_active_count)
        config_layout.addWidget(self.active_count, 1, 1)

        config_layout.addWidget(qw.QLabel("Starting Voice Frequency"), 2, 0)
        self.start_freq = qw.QSpinBox()
        self.start_freq.setValue(settings['start'])
        self.start_freq.setMinimum(0)
        self.start_freq.setMaximum(20000)
        self.start_freq.valueChanged.connect(self.set_start_freq)
        config_layout.addWidget(self.start_freq, 3, 0)

        config_layout.addWidget(qw.QLabel("Ending Voice Frequency"), 2, 1)
        self.end_freq = qw.QSpinBox()
        self.end_freq.setValue(settings['end'])
        self.end_freq.setMinimum(0)
        self.end_freq.setMaximum(20000)
        self.end_freq.valueChanged.connect(self.set_end_freq)
        config_layout.addWidget(self.end_freq, 3, 1)

        # Add input APIs
        input_layout = qw.QVBoxLayout()
        input_layout.addWidget(qw.QLabel("API"))
        self.input_devices = qw.QComboBox()
        self.input_apis = qw.QComboBox()
        self.input_apis.setCurrentIndex(settings['input-api'])
        self.set_input_api(settings['input-api'])
        self.input_apis.activated.connect(self.set_input_api)
        for api in sounddevice.query_hostapis():
            self.input_apis.addItem(api.get('name'))
        input_layout.addWidget(self.input_apis)

        # Add output APIs
        output_layout = qw.QVBoxLayout()
        output_layout.addWidget(qw.QLabel("API"))
        self.output_devices = qw.QComboBox()
        self.output_apis = qw.QComboBox()
        self.output_apis.setCurrentIndex(settings['output-api'])
        self.set_output_api(settings['output-api'])
        self.output_apis.activated.connect(self.set_output_api)
        for api in sounddevice.query_hostapis():
            self.output_apis.addItem(api.get('name'))
        output_layout.addWidget(self.output_apis)

        # Add input and output devices
        self.set_input_device(settings['input-device'])
        self.input_devices.setCurrentText(self.filter.input)
        self.input_devices.textActivated.connect(self.set_input_device)

        
        self.set_output_device(settings['output-device'])
        self.output_devices.setCurrentText(self.filter.output)
        self.output_devices.textActivated.connect(self.set_output_device)

        input_layout.addWidget(qw.QLabel("Device"))
        input_layout.addWidget(self.input_devices)
        output_layout.addWidget(qw.QLabel("Device"))
        output_layout.addWidget(self.output_devices)
        
        self.input_group_box = qw.QGroupBox("Inputs")
        self.input_group_box.setLayout(input_layout)
        self.output_group_box = qw.QGroupBox("Outputs")
        self.output_group_box.setLayout(output_layout)

        # Add start stop buttons
        bottom_layout = qw.QHBoxLayout()
        start_button = qw.QPushButton("Start")
        start_button.clicked.connect(self.start)
        bottom_layout.addWidget(start_button)
        stop_button = qw.QPushButton("Stop")
        stop_button.clicked.connect(self.stop)
        bottom_layout.addWidget(stop_button)

        # Add everything together
        main_layout = qw.QGridLayout()
        main_layout.addLayout(top_layout, 0, 0, 1, 3)
        main_layout.addLayout(config_layout, 1, 0, 1, 3)
        main_layout.addWidget(self.input_group_box, 2, 0)
        main_layout.addWidget(self.output_group_box, 2, 1)
        main_layout.addLayout(bottom_layout, 3, 0, 1, 3)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)

        self.central_widget = qw.QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        self.setWindowTitle("Filter")
        self.change_style('Windows')

    def change_style(self, styleName):
        qw.QApplication.setStyle(qw.QStyleFactory.create(styleName))
    
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
    
    def set_input_api(self, index):
        self.update_devices('input', index)
        settings['input-api'] = index
        
    def set_output_api(self, index):
        self.update_devices('output', index)
        settings['output-api'] = index

    def set_input_device(self, input_device):
        self.filter.set_input(input_device, self.input_apis.currentIndex())
        settings['input-device'] = self.filter.input
    
    def set_output_device(self, output_device):
        self.filter.set_output(output_device, self.output_apis.currentIndex())
        settings['output-device'] = self.filter.output
    
    def set_active_voice_level(self, value):
        settings['active-level'] = value
        self.filter.active_level = value
        if self.filter.stream:
            self.start()

    def set_active_count(self, value):
        settings['active-count'] = value
        self.filter.active_count = value
        if self.filter.stream:
            self.start()

    def set_start_freq(self, value):
        settings['start'] = value
        self.filter.start_freq = value
        if self.filter.stream:
            self.start()
    
    def set_end_freq(self, value):
        settings['end'] = value
        self.filter.end_freq = value
        if self.filter.stream:
            self.start()

    def save_settings(self, path):
        settings.save()

    def load_settings(self, path):
        settings.load()

    def default_settings(self, path):
        settings.set_to_defaults()

if __name__ == "__main__":
    app = qw.QApplication([])
    fw = FilterWindow()
    fw.show()
    app.exec_()