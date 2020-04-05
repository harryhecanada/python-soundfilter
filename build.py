from PyInstaller.__main__ import run
import pathlib
import shutil

build_folder = pathlib.Path('build')
dist_folder = pathlib.Path('dist')
data_folder = pathlib.Path('data')
pa_dll = pathlib.Path('_sounddevice_data/portaudio-binaries/libportaudio64bit.dll')

if build_folder.exists():
    shutil.rmtree(build_folder)

if dist_folder.exists():
    shutil.rmtree(dist_folder)

run(['--onefile', '--noconsole', '--add-binary', str(data_folder/pa_dll)+";"+str(pa_dll.parent), 'pysoundfilter.pyw'])