#!/usr/bin/env python3
"""

"""
import argparse
import logging

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-i', '--input-device', type=int_or_str,
                    help='input device ID or substring')
parser.add_argument('-o', '--output-device', type=int_or_str,
                    help='output device ID or substring')
parser.add_argument('-c', '--channels', type=int, default=2,
                    help='number of channels')
parser.add_argument('-b', '--block-duration', type=float, metavar='DURATION', default=50, help='block size (default %(default)s milliseconds)')
parser.add_argument('-l', '--latency', type=float, help='latency in seconds')
parser.add_argument('--start', type=int, default = 0)
parser.add_argument('--end', type=int, default = 20)
parser.add_argument('--active_level', type=float, default = 10)
parser.add_argument('--log', type=int, default = 0)
args = parser.parse_args()

# Rename constants to be more verbose
active_start_freq = int(args.start)
active_end_freq = int(args.end)
active_start_mean = float(args.active_level)
active_count = 3


try:
    import sounddevice as sd
    import numpy as np # Make sure NumPy is loaded before it is used in the callback
    assert np  # avoid "imported but unused" message (W0611)

    device_info = sd.query_devices(args.input_device, 'input')
    samplerate = device_info['default_samplerate']
    block_size = int(samplerate * args.block_duration / 1000)
    active_counter = 0

    if args.log:
        datafile = open('data.csv','ab')
        freq = np.fft.rfftfreq(block_size, d=1./samplerate)
        np.savetxt(datafile, freq[None,:], delimiter=',', fmt='%.4f')
    else:
        datafile = None

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

        if datafile:
            # TODO: figure out a more efficient way of doing this...
            np.savetxt(datafile, data[None,:], delimiter=',', fmt='%.4f')
            
        if activation_function(data):
            outdata[:] = indata
        else:
            outdata[:] = 0

    with sd.Stream(device=(args.input_device, args.output_device),
                   samplerate=samplerate, blocksize=block_size, latency=args.latency,
                   channels=args.channels, callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
        
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
finally:
    if datafile:
        datafile.close()