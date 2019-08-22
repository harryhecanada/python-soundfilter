#!/usr/bin/env python3
"""

"""
import argparse
import logging


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-i', '--input-device', type=int_or_str,
                    help='input device ID or substring')
parser.add_argument('-o', '--output-device', type=int_or_str,
                    help='output device ID or substring')
parser.add_argument('-c', '--channels', type=int, default=2,
                    help='number of channels')
parser.add_argument('-b', '--block-duration', type=float, metavar='DURATION', default=50, help='block size (default %(default)s milliseconds)')
parser.add_argument('-l', '--latency', type=float, help='latency in seconds')
args = parser.parse_args()

active_start_freq = 0
active_end_freq = 50
active_start_mean = 3.5
active_count = 3


try:
    import sounddevice as sd
    import numpy as np # Make sure NumPy is loaded before it is used in the callback
    assert np  # avoid "imported but unused" message (W0611)

    device_info = sd.query_devices(args.input_device, 'input')
    samplerate = device_info['default_samplerate']
    active_counter = 0

    def activation_function(data):
        global active_counter
        if sum(data[active_start_freq:active_end_freq]) > active_start_mean:
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
        data = np.abs(np.fft.rfft(indata[:, 0]))
        data = data/np.linalg.norm(data)
        if activation_function(data):
            outdata[:] = indata
        else:
            outdata[:] = 0

    with sd.Stream(device=(args.input_device, args.output_device),
                   samplerate=samplerate, blocksize=int(samplerate * args.block_duration / 1000), latency=args.latency,
                   channels=args.channels, callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
        
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))