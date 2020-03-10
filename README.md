"# Arm9"

Make sure you have python 3

Have a text editor; atom, viscose, notepad++, whatever

Have git installed or some graphical git application so you have interact with the repo. Look up tutorials on how to use it. For the most part, you just need to pull from what's there so you can use it.

You're gonna need to install the python libraries that are imported in the GUI.py file. Copy and paste this into your command line. You need a c++ compiler installed first.

pip install opencv-python
pip install pillow
pip install datetime
pip install argparse
pip install imutils
pip install numpy
pip install matplotlib
pip install pyserial
pip install scipy
pip install sounddevice
pip install cmake
pip install dlib

In the GUI.py file, there is a section of code surrounded by tildes, that's the serial communication code. It may be commented out... uncomment it if that's the case.
When you uncomment that code you need to have the Arduino plugged in to run it. Plug the Arduino in and check your device manager to figure out the COM number, and then change that number in the GUI file - it's towards the top
