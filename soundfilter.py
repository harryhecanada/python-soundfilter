#!/usr/bin/env python3
"""

"""
import argparse
import logging
import json

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

# Load from config.json
defaults = {
    "block_duration": 50, 
    "active-level": 10, 
    "start": 0,
    "end": 20, 
}

try:
    with open("config.json") as config:
        configs = json.load(config)
    defaults.update(configs)
except:
    print("Could not load configuration from config.json, using defaults for command line parameters...")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-i', '--input-device', type=int_or_str, default = defaults.get("input-device", None), help='input device ID or substring')
parser.add_argument('-o', '--output-device', type=int_or_str, default = defaults.get("output-device", None), help='output device ID or substring')
parser.add_argument('-b', '--block-duration', type=float, metavar='DURATION', default = defaults.get("block-duration", 0), help='block size (default %(default)s milliseconds)')
parser.add_argument('-a','--active-level', type=float, default = defaults.get("active-level", 10), help = "audio level required to activate your microphone within the activation frequency band")
parser.add_argument('-s','--start', type=int, default = defaults.get("start", 0), help = "activation filter starting frequency band")
parser.add_argument('-e','--end', type=int, default = defaults.get("end", 20), help = "activation filter ending frequncy band") 
args = parser.parse_args()
print("Arguments loaded:")
print(vars(args))

# Rename constants to be more verbose
active_start_freq = int(args.start)
active_end_freq = int(args.end)
active_start_mean = float(args.active_level)
active_count = 3

try:
    import sounddevice as sd
    import numpy as np # Make sure NumPy is loaded before it is used in the callback
    assert np  # avoid "imported but unused" message (W0611)

    datafile = None
    device_info = sd.query_devices(args.input_device, 'input')
    samplerate = device_info['default_samplerate']
    block_size = int(samplerate * args.block_duration / 1000)
    active_counter = 0

    def activation_function(data):
        global active_counter
        if np.mean(data[active_start_freq:active_end_freq]) > active_start_mean:
            active_counter = active_count
            return True
        elif active_counter > 0:
            active_counter -= 1
            return True
        else:
            return False

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)

        data = np.fft.rfft(indata[:, 0])
        data = np.abs(data)        

        if activation_function(data):
            outdata[:] = indata
        else:
            outdata[:] = 0

    with sd.Stream(device=(args.input_device, args.output_device),
                   samplerate=samplerate, blocksize=block_size, callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
        
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))