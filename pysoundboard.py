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
TODO: proper stop with ctrl + c
'''
debug = True
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

    if event.Key == "Numpad0":
        sd.stop()

    if event.Key == "Numpad1":
        data, fs = sf.read("JohnCena.wav", dtype='float32')
        sd.play(data, fs, device=18)

    if event.Key == "Numpad2":
        data, fs = sf.read("Fail_Recorder_Mission_Impossible_Themesong_online-audio-converter.com.wav", dtype='float32')
        sd.play(data, fs, device=18)
    
    if event.Key == "Numpad3":
        data, fs = sf.read("Mortal_Kombat_X_Fatality_SOUND_EFFECT_online-audio-converter.com.wav", dtype='float32')
        sd.play(data, fs, device=18)
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