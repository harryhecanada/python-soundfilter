from enum import Enum
from sys import exit
import pathlib
import pyWinhook
import sounddevice as sd
import soundfile as sf

'''
Window
Press button to start binding process:
Ask user to press key to select key to bind
After user press key its locked in and they can browse to a sound file to play, has to be WAV for now
Have a scroll box that lists the key binds currently loaded
Allow user to select and delete from scrollbox with button
Start button
Stop button
Save button
Reset button
Copy device selection from pysoundfilter
Volume Modification
Help button
About button
Version Strings
Minimize and Close buttons
'''

debug = True
output_devices = [16, 18]
callbacks = []

def play_concurrent(data, samplerate, devices):
    for device in devices:
        sd.play(data, samplerate, device=device)
        callbacks.append(sd._last_callback)
        sd._last_callback = None

def stop_all(ignore_errors=True):
    for callback in callbacks:
        callback.stream.stop(ignore_errors)
        callback.stream.close(ignore_errors)

class SoundBoardMap(dict):
    def preload(self):
        for key, item in self.items():
            if isinstance(item, str):
                path = pathlib.Path(item)
            else:
                path = pathlib.Path(item['path'])

            if isinstance(key, int):
                print("Preloading ASCII", key, "with", path.name)
            else:
                print("Preloading Key", key, "with", path.name)

            if path.suffix == "":
                #Assume control message and not a file
                self[key] = globals()[path.name]
            else:
                data, samplerate = sf.read(path.resolve(), dtype='float32')
                print(data.shape, sum(data), samplerate)

                # Change volume
                if float(item['volume']) > 0:
                    data *= float(item['volume'])
                else:
                    print("Volume setting must be greater than 0, e.g 0.5.")

                # Change duration
                if float(item['duration']) > 0 and float(item['duration']) <= 1:
                    data = data[0:int(len(data)*float(item['duration']))][:]
                else:
                    print("Duration setting must be greater than 0 and less than or equal to 1, e.g. 0.5.")
                print(data.shape, sum(data), samplerate)

                self[key] = {
                    "path":path,
                    "volume":float(item['volume']),
                    "duration":float(item['duration']),
                    "data":data,
                    "samplerate":samplerate
                }

sound_board_map = SoundBoardMap({
    3:"exit",
    "Numpad0":"stop_all",
    "Numpad1":{
        "path":"JohnCena.wav",
        "volume":"0.5",
        "duration":"0.5"
    },
    "Numpad2":{
        "path":"Fail_Recorder_Mission_Impossible_Themesong_online-audio-converter.com.wav",
        "volume":"0.5",
        "duration":"0.5"
    },
    "Numpad3":{
        "path":"Mortal_Kombat_X_Fatality_SOUND_EFFECT_online-audio-converter.com.wav",
        "volume":"0.5",
        "duration":"0.5"
    }
})
sound_board_map.preload()

def OnMouseEvent(event):
    if debug:
        print('MessageName: %s' % event.MessageName)
        print('Message: %s' % event.Message)
        print('Time: %s' % event.Time)
        print('Window: %s' % event.Window)
        print('WindowName: %s' % event.WindowName)
        print('Position: (%d, %d)' % event.Position)
        print('Wheel: %s' % event.Wheel)
        print('Injected: %s' % event.Injected)
        print('---')

    # return True to pass the event to other handlers
    # return False to stop the event from propagating
    return True

def OnKeyboardEvent(event):
    if debug:
        print('MessageName: %s' % event.MessageName)
        print('Message: %s' % event.Message)
        print('Time: %s' % event.Time)
        print('Window: %s' % event.Window)
        print('WindowName: %s' % event.WindowName)
        print('Ascii: ', event.Ascii)
        print('Key: %s' %  event.Key)
        print('KeyID: %s' %  event.KeyID)
        print('ScanCode: %s' %  event.ScanCode)
        print('Extended: %s' %  event.Extended)
        print('Injected: %s' %  event.Injected)
        print('Alt %s' %  event.Alt)
        print('Transition %s' %  event.Transition)
        print('---')

    # Ctrl + C exits, TODO: make configurable?
    if event.Ascii == 3:
        exit()

    if event.Key in sound_board_map or event.Ascii in sound_board_map:
        item = sound_board_map[event.Key]
        if callable(item):
            item()
        else:
            stop_all()
            play_concurrent(item["data"], item['samplerate'], output_devices)

    # return True to pass the event to other handlers
    # return False to stop the event from propagatingd
    return True

# create the hook mananger
hm = pyWinhook.HookManager()
# register two callbacks
hm.MouseAllButtonsDown = OnMouseEvent
hm.KeyDown = OnKeyboardEvent

# hook into the mouse and keyboard events
hm.HookMouse()
hm.HookKeyboard()

import pythoncom
pythoncom.PumpMessages()