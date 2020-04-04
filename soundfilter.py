#!/usr/bin/env python3
"""

"""
import argparse
import logging
import json

# Load from config.json
defaults = {
    "api": "MME",
    "input-device": "Mic",
    "output-device": "CABLE Input",
    "block-duration": 50,
    "active-level": 3,
    "active-count": 10,
    "start": 0,
    "end": 20,
}

try:
    with open("config.json") as config:
        configs = json.load(config)
    defaults.update(configs)
except:
    print("Could not load configuration from config.json, using defaults for command line parameters...")

def parse_arguments():
    def int_or_str(text):
        """Helper function for argument parsing."""
        try:
            return int(text)
        except ValueError:
            return text

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--input-device', type=int_or_str, default = defaults.get("input-device", 'Mic'), help='input device ID or substring')
    parser.add_argument('-o', '--output-device', type=int_or_str, default = defaults.get("output-device", 'CABLE Input'), help='output device ID or substring')
    parser.add_argument('--api', type=str, default = defaults.get("api", 'MME'), help='preferred API to use for audio')
    parser.add_argument('-b', '--block-duration', type=float, metavar='DURATION', default = defaults.get("block-duration", 50), help='block size (default %(default)s milliseconds)')
    parser.add_argument('-a','--active-level', type=float, default = defaults.get("active-level", 3), help = "audio level required to activate your microphone within the activation frequency band")
    parser.add_argument('-c','--active-count', type=float, default = defaults.get("active-count", 10), help = "number of blocks to continue recording after activation")
    parser.add_argument('-s','--start', type=int, default = defaults.get("start", 0), help = "activation filter starting frequency band")
    parser.add_argument('-e','--end', type=int, default = defaults.get("end", 20), help = "activation filter ending frequncy band") 
    args = parser.parse_args()
    print("Arguments loaded:")
    print(json.dumps(vars(args), indent = 4))
    return parser


parser = parse_arguments()
args = parser.parse_args()
# Rename constants to be more verbose
active_start_freq = int(args.start)
active_end_freq = int(args.end)
active_start_mean = float(args.active_level)
active_count = int(args.active_count)

try:
    import sounddevice as sd
    import numpy as np # Make sure NumPy is loaded before it is used in the callback
    #from scipy.signal import resample_poly

    def get_device(name = 'CABLE Input', kind = 'output', api = 'MME'):
        matching_devices = []
        devices = sd.query_devices(kind = kind)
        for device in devices:
            if name.lower() in device.get('name').lower():
                matching_devices.append(device)
        
        if not matching_devices:
            print("Unable to find device matching", name, 'of kind', kind)
            return None

        found = False
        for device in matching_devices:
            if api in sd.query_hostapis(int(device.get('hostapi'))).get('name'):
                found = True
                break
        
        if not found:
            print("Unable to find device matching host api", api, 'using first available...')
            return devices[0]
        else:
            return device
    
    input_names = ['mic', 'web', 'cam', 'phone']
    device_info = get_device(args.input_device, 'input', args.api)
    if not device_info:
        for name in input_names:
            device_info = get_device(name, 'input', args.api)
            if device_info:
                break
    
    if not device_info:
        print("Unable to find input device, exiting...")
        exit(1)

    print("Input device info:")
    print(json.dumps(device_info, indent = 4))
    print("Output device info:")
    print(json.dumps(get_device(args.output_device, 'output', args.api), indent = 4))
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
        # if status:
        #     print(status)

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