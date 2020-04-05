### python-soundfilter
Quick and dirty spectrum analyzer and audio filter for Windows using the sounddevice library. Currently is able to be used to filter out noise, keyboard typing, and provide a sound level based activation filter for VoIP use. Future development may contain an AI algorithm for more advanced filtering.
### Prerequsites
Download and install https://www.vb-audio.com/Cable/ in order to create a virtual microphone to be used by VoIP applications to receive your filtered audio.
### Quick Start Guide
1) pip install .
2) double click to run gui.py or run python gui.py in the command line
3) Change target application's input device to CABLE Output
