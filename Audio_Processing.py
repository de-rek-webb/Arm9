## Program: Audio Processing
## Project: Junior Design ARM 09
## Author: Calder Wilson


import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
from scipy.io.wavfile import write
from math import log10

def record_audio(duration,fs):
    """Take a recording of sound.
    - duration = number of seconds
    - fs = sampling frequency"""

    print("Start Recording")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1) # Take recording
    sd.wait()  # Wait until recording is finished
    print("Stop Recording")
    return recording

def plot_signal(audio,filename):
    """Plot the signal."""
    plt.figure(figsize=(11,8))  # Create plot and set size in inches
    plt.plot(audio, color='black')  # Create a plot of the soundwave
    #plt.axis('off')  # Remove axes to leave only waveform for arm to draw
    plt.savefig('{}.png'.format(filename), transparent=True, bbox_inches=0, pad_inches=0)  # Save plot as png
    #plt.savefig('{}.svg'.format(filename), transparent=True, bbox_inches=0, pad_inches=0)  # Save plot as svg

def dB_calculate(audio):
    """Calculate the decibel level with maximum audio as reference"""
    max = np.amax(audio);  # Find the maximum value
    dB = audio  # Make copy of audio array for processing
    for index in range(len(audio)):
        dB[index] = 20*log10(audio[index]) # Calculate decibel with max as ref
    return dB

def simplify_signal(inputSignal):
    """Remove data points to simplify signal"""
    simpleAudio = np.array(inputSignal[0])  # Array to hold simplified signal
    x = 0
    x_vals = np.array((x))  # Array to hold x values to be plotted

    #Take one data point for every 0.1 seconds
    for i in range(1,len(inputSignal)):
        if i % 441 == 0:
            simpleAudio = np.append(simpleAudio,inputSignal[i])
            x+=1
            x_vals = np.append(x_vals,x)

    # # Scale amplitude by a factor of 5 so that graph will be at least 5in high
    # max = np.amax(simpleAudio)
    # scaling = 5/max
    # simpleAudio = simpleAudio*scaling
    # simpleAudio += 2

    outputSignal = np.column_stack((x_vals,simpleAudio)) # Concatenate x and y values
    return outputSignal

def running_mean(x, N):
    """Function to caluclate the running mean of a signal"""
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)

def peak_detection (inputSignal):
    """Retrieve the envelope of positive half of signal"""
    intervalLength = 100  # Interval over which peak is calculated
    outputSignal = np.zeros(inputSignal.size)  # Array to store procesed signal

    # Function to calculate local peaks of signal
    for baseIndex in range (intervalLength, inputSignal.size):
        maximum = 0
        for lookbackIndex in range (intervalLength):
            maximum = max (inputSignal[baseIndex - lookbackIndex], maximum)
        outputSignal[baseIndex] = maximum
    return outputSignal

# MAIN
def audio_main():
    """Main function that encompasses all audio processing"""
    audio = record_audio(2,4410)  #  Record two seconds of audio at 4410 Hz
    abs = np.absolute(audio)  # Take abosulte value of each element
    envelope = peak_detection(abs)  # Running peak detection to obtain envelope
    processed_audio = simplify_signal(envelope)  # Simplify signal by removing data points

    plot_signal(audio,'original_sound')

    return processed_audio
