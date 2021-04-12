#!/usr/bin/env python3
"""

"""
import json
import sounddevice as sd
import numpy as np 
import torch
model = torch.jit.load('model_micro.jit')
model.eval()
class SoundFilter(object):
    def __init__(self, input_device='microphone', output_device='CABLE Input', active_level=3, active_count = 10, start_freq=0, end_freq=20, block_duration = 250):
        self._input_id, self._input_device = self.get_device(input_device, 'input')
        self._output_id, self._output_device = self.get_device(output_device, 'output')

        # If input device cannot be found, try other names
        input_names = ['cam', 'web', 'phone']
        if not self._input_device:
            for name in input_names:
                self._input_id, self._input_device = self.get_device(name, 'input')
                if input_device:
                    break

        if not input_device:
            input_device = sd.query_devices(kind='input')
        
        if not input_device:
            raise ValueError("Unable to find any input device for sound filter to function.")

        print("Input device info:")
        print(json.dumps(sd.query_devices(self._input_id), indent = 4))

        print("Output device info:")
        print(json.dumps(sd.query_devices(self._output_id), indent = 4))

        self.active_counter = 0
        self.start_freq = start_freq
        self.end_freq = end_freq
        self.active_level = active_level
        self.active_count = active_count
        self.samplerate = self._input_device['default_samplerate']
        self.block_size = int(self.samplerate * block_duration / 1000)
        self.stream = None

        import atexit
        atexit.register(self.stop)

    def _new_stream(self):
        if self.stream:
            self.stream.stop()
            self.stream = None
        self.stream = sd.Stream(device=(self._input_id, self._output_id), samplerate=self.samplerate, blocksize=self.block_size, callback=self.callback)

    @property
    def input(self):
        return self._input_device['name']

    @property
    def output(self):
        return self._output_device['name']

    def set_input(self, input_device, api = 'MME', block_duration = 50):
        self._input_id, self._input_device = self.get_device(input_device, 'input', api)
        self.samplerate = self._input_device['default_samplerate']
        self.block_size = int(self.samplerate * block_duration / 1000)
        if self.stream:
            self.start()
    
    def set_output(self, output_device, api = 'MME'):
        self._output_id, self._output_device = self.get_device(output_device, 'output', api)
        if self.stream:
            self.start()

    def start(self):
        self._new_stream()
        self.stream.start()
        return self
    
    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream = None
        return self

    def activation_function(self, data):
        if np.mean(data[self.start_freq:self.end_freq]) > self.active_level:
            self.active_counter = self.active_count
            return True
        elif self.active_counter > 0:
            self.active_counter -= 1
            return True
        else:
            return False

    def callback(self, indata, outdata, frames, time, status):
        # if status:
        #     print(status)
        data = np.fft.rfft(indata[:, 0])
        data = np.abs(data)
        
        if self.activation_function(data):
            outdata[:] = indata
        else:
            outdata[:] = 0

    @staticmethod
    def get_device(name = 'CABLE Input', kind = 'output', api = 0):       
        if isinstance(name, int):
            return name, sd.query_devices(name)

        devices = sd.query_devices()
        matching_devices = []
        for device_id in range(len(devices)):
            if name.lower() in devices[device_id].get('name').lower():
                try:
                    if kind == 'input':
                        sd.check_input_settings(device_id)
                    elif kind == 'output':
                        sd.check_output_settings(device_id)
                    else:
                        print('Invalid kind')
                        return None
                    matching_devices.append((device_id, devices[device_id]))
                except:
                    pass
        
        if not matching_devices:
            print("Unable to find device matching name", name, 'of kind', kind)
            return None

        found = False

        if isinstance(api, int):
            api = sd.query_hostapis(api).get('name')
        for device_id, device in matching_devices:
            if api in sd.query_hostapis(int(device.get('hostapi'))).get('name'):
                found = True
                break
        
        if not found:
            print("Unable to find device matching host api", api, 'using first available...')
            return matching_devices[0]
        else:
            return device_id, device

class SileroSoundFilter(SoundFilter):
    _samplerate = 16000
    _block_length = 250
    _active_count = 1
    def __init__(self, input_device='microphone', output_device='CABLE Input'):
        self._input_id, self._input_device = self.get_device(input_device, 'input')
        self._output_id, self._output_device = self.get_device(output_device, 'output')

        # If input device cannot be found, try other names
        input_names = ['cam', 'web', 'phone']
        if not self._input_device:
            for name in input_names:
                self._input_id, self._input_device = self.get_device(name, 'input')
                if input_device:
                    break

        if not input_device:
            input_device = sd.query_devices(kind='input')
        
        if not input_device:
            raise ValueError("Unable to find any input device for sound filter to function.")

        print("Input device info:")
        print(json.dumps(sd.query_devices(self._input_id), indent = 4))

        print("Output device info:")
        print(json.dumps(sd.query_devices(self._output_id), indent = 4))

        self.samplerate = self._samplerate
        # Hard coded block duration of 250ms
        self.block_size = int(self._samplerate * self._block_length / 1000)
        # Will crash if block size is not 4000, model is not trained for it
        assert(self.block_size == 4000)
        self.stream = None
        self.active_counter = 0

        import atexit
        atexit.register(self.stop)

    def set_input(self, input_device, block_duration = 250, api = 'MME'):
        self._input_id, self._input_device = self.get_device(input_device, 'input', api)
        self.samplerate = self._samplerate
        self.block_size = int(self._samplerate * self._block_length / 1000)
        assert(self.block_size == 4000)
        if self.stream:
            self.start()

    @classmethod
    def validate(cls, model, inputs: torch.Tensor):
        with torch.no_grad():
            outs = model(inputs)
        return outs

    def activation_function(self, data):
        chunks = torch.Tensor(data[:,1])
        out = self.validate(model, chunks)

        if out[0][1] > 0.5:
            self.active_counter = self._active_count
            return True
        elif self.active_counter > 0:
            self.active_counter -= 1
            return True
        else:
            return False

    def callback(self, indata, outdata, frames, time, status):
        if self.activation_function(indata):
            outdata[:] = indata
        else:
            outdata[:] = 0

if __name__ == "__main__":
    import argparse
    from settings import settings
    def parse_arguments():
        def int_or_str(text):
            """Helper function for argument parsing."""
            try:
                return int(text)
            except ValueError:
                return text

        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('-i', '--input-device', type=int_or_str, default = settings.get("input-device", 'microphone'), help='input device ID or substring')
        parser.add_argument('-o', '--output-device', type=int_or_str, default = settings.get("output-device", 'CABLE Input'), help='output device ID or substring')
        parser.add_argument('-b', '--block-duration', type=float, metavar='DURATION', default = settings.get("block-duration", 50), help='block size (default %(default)s milliseconds)')
        parser.add_argument('-a','--active-level', type=float, default = float(settings.get("active-level", 3)), help = "audio level required to activate your microphone within the activation frequency band")
        parser.add_argument('-c','--active-count', type=int, default = settings.get("active-count", 10), help = "number of blocks to continue recording after activation")
        parser.add_argument('-s','--start', type=int, default = settings.get("start", 0), help = "activation filter starting frequency band")
        parser.add_argument('-e','--end', type=int, default = settings.get("end", 20), help = "activation filter ending frequncy band")
        args = parser.parse_args()
        print("Arguments loaded:")
        print(json.dumps(vars(args), indent = 4))
        return parser
        
    parser = parse_arguments()
    args = parser.parse_args()

    #sf = SoundFilter(args.input_device, args.output_device, args.active_level, args.active_count, args.start, args.end, args.block_duration).start()
    sf = SileroSoundFilter(args.input_device, args.output_device).start()
    print('#' * 80)
    print('press Return to quit')
    print('#' * 80)
    input()