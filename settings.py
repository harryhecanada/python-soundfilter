from PyQt5.QtCore import QSettings


class Settings(dict):
    __ver__ = "0.0.1"
    __company__ = "python_soundfilter"
    __product__ = "python_soundfilter"
    __defaults = {
        "input-api": 0,
        "output-api": 0,
        "input-device": "microphone", 
        "output-device": "CABLE Input", 
        "block-duration": 50, 
        "active-level": 3.0, 
        "active-count": 10, 
        "start": 0,
        "end": 20
    }
    def __init__(self):
        super().__init__()
        self.load()

    def set_to_defaults(self):
        self.update(self.__defaults)
        return self

    def load(self, settings:QSettings=QSettings(__company__, __product__)):
        if not settings.contains('version'):
            self.set_to_defaults()
            self.save()

        self.clear()
        for key, value in self.__defaults.items():
            self.update({key:settings.value(key, value)})

        print("Settings loaded:", self)
        return self

    def save(self, data:dict = {}, settings:QSettings=QSettings(__company__, __product__)):
        if not data:
            data = self
        for key, item in data.items():
            settings.setValue(key, item)
        settings.setValue('version', self.__ver__)

settings = Settings()