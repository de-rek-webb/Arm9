"# Arm9"

Make sure you have python 3

Have a text editor; atom, viscose, notepad++, whatever

Have git installed or some graphical git application so you have interact with the repo. Look up tutorials on how to use it. For the most part, you just need to pull from what's there so you can use it.

You're gonna need to install the python libraries that are imported in the GUI.py file. Here's how to install each one in windows command line.
  tkinter: already installed
  cv2: pip install opencv-python
  PIL.Image, PIL.ImageTk: pip install pillow
  time: already installed
  datetime: pip install datetime
  argparse: pip install argparse
  imutils: pip install imutils
  dlib:
    pip install cmake
    pip install dlib
    also need to have a c++ complier installed
  numpy: pip install numpy
  matplotlib.pyplot: pip install matplotlib
  serial: pip install pyserial
  os: already installed
  scipy: pip install scipy
  sounddevice: pip install sounddevice

In the GUI.py file, there is a section of code surrounded by tildes, that's the serial communication code. It may be commented out... uncomment it if that's the case.
When you uncomment that code you need to have the Arduino plugged in to run it. Plug the Arduino in and check your device manager to figure out the COM number, and then change that number in the GUI file - it's towards the top
