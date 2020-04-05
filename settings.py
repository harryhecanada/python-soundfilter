from PyQt5.QtCore import QSettings


class Settings(dict):
    __company__ = "python_soundfilter"
    __product__ = "python_soundfilter"
    __defaults = {
        "input-api": 0,
        "output-api": 0,
        "input-device": "microphone", 
        "output-device": "CABLE Input", 
        "block-duration": 50, 
        "active-level": 3, 
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

        results = {
            "input-api": settings.value("input-api", 0),
            "output-api": settings.value("output-api", 0),
            "input-device": settings.value("input-device", "microphone"),
            "output-device": settings.value("output-device", "CABLE Input"),
            "block-duration": settings.value("block-duration", 50.0),
            "active-level": settings.value("active-level", 3),
            "active-count": settings.value("active-count", 10),
            "start": settings.value("start", 0),
            "end": settings.value("end", 20),
        }
        self.update(results)

        print("Settings loaded:", self)
        return self

    def save(self, data:dict = {}, settings:QSettings=QSettings(__company__, __product__)):
        if not data:
            data = self
        for key, item in data:
            settings.setValue(key, item)

settings = Settings()