### python-soundfilter
Quick and dirty spectrum analyzer and audio filter for Windows using the sounddevice library. Currently is able to be used to filter out noise, keyboard typing, and provide a sound level based activation filter for VoIP use. Future development may contain an AI algorithm for more advanced filtering.
### Prerequsites
Download and install https://www.vb-audio.com/Cable/ in order to create a virtual microphone to be used by VoIP applications to receive your filtered audio.
### Quick Start Guide
1) pip install .
2) python spectrum_analyzer.py -l 
- This will list all of your sound devices by ID, note down the desired mic and virtual audio cable input
2) python spectrum_analyzer.py 
- Note that you may need to specify your recording device, default is used.
3) Speak to your microphone as you would normally, note the frequency range of your voice on the spectrum analyzer
4) Modify the following variables in soundfilter.py to match your voice:

- active_start_freq
- active_end_freq
- Note the start/end freq are integers denoting the starting x value and ending x value on the spectrum analyzer plot which matches your voice.

5) python soundfilter.py -i <mic #> -o <speaker #>
6) Repeat steps 4-5 until desired.



TODO: GUI interface    
TODO: Auto find vb audio device    
TODO: use https://people.csail.mit.edu/hubert/pyaudio/    
