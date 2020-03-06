## Program: G-code Generator
## Project: Junior Design ARM 09
## Author: Calder Wilson

# List of G-Codes
# G00	Rapid positioning
# G01	Linear interpolation
# G90	Absolute programming
# G91	Incremental programming
# G20	Programming in inches
# G21	Programming in millimeters
# M02	End of program
# M06	Automatic tool change
# M72   Music

import matplotlib.pyplot as plt
import numpy as np

def choose_units():
    """Set units for program to be in mm or inches"""
    usrin = input("Type in or mm: ")
    if usrin == 'mm':
        return("G21")
    return("G20")

def choose_type():
    """Sets program to be in absolute or incremental"""
    usrin = input("Type a or i: ")
    if usrin == 'i':
        return("G91")
    return("G90")

def dot_image(array):
    """Generate g-code for a dot image from an array"""
    g_code = []
    for i in range(0,np.size(array,axis=0)):
        g_code.append('G00 X' + str(array[i,0]) + ' Y' + str(array[i,1]) + ' Z0.25')
        g_code.append('G00 X' + str(array[i,0]) + ' Y' + str(array[i,1]) + ' Z0.0')
    return g_code

def line_image(array):
    """Generate g-code for a line-image from an array"""
    g_code = ['G00 X' + str(array[0,0]) + ' Y' + str(array[0,1]) + ' Z1.0']
    for i in range(0,np.size(array,axis=0)):
        g_code.append('G01 X'+ str(array[i,0]) + ' Y' + str(array[i,1]) + ' Z0.0')
    return g_code

def scale_image(array,height,width):
    """Scale array to fit the page"""
    scaling = np.amax(array, axis=0)    # Get maximum x and y values
    scaling[0] = width/scaling[0]   # Scale by provided page width
    scaling[1] = height/scaling[1]  # Scale by provided page height
    array *= scaling    # Scale array
    array[:,1] +=2  # Shift y values by two to account for distance from arm to paper
    array[:,0] -= (width/2)

    return np.round(array,3)    # Round array to 3 decimal places

def plot_signal(signal,filename):
    """Plot the signal."""
    plt.figure(figsize=(11,8))  # Create plot and set size in inches
    if filename == 'face':
        plt.scatter(signal[:,0], signal[:,1], color='black')  # Create a plot of the signal
    elif filename == 'sound':
        plt.plot(signal[:,0], signal[:,1], color='black')  # Create a plot of the signal
    plt.savefig('{}.png'.format(filename), transparent=True, bbox_inches=0, pad_inches=0)  # Save plot as png

def main(mode,array=None):
    """Main function of the program.
    mode = 'sound', 'face', or 'demo'
    array = numpy array conatining x,y coordinates to be plotted"""
    g_code = []    # List to hold g-code commands
    g_code.append('G20')    # Inches
    g_code.append('G90')    # Absolute mode
    if mode == 'demo':
        with open('demo.txt') as f: # Read demo g_code from file, remove '\n'
            g_code += f.read().splitlines()
    elif mode == 'sound':
        array = scale_image(array,8,10)
        g_code += line_image(array)
    elif mode == 'face':
        array = scale_image(array,8.5,11)
        g_code += dot_image(array)
    g_code.append('M02')

    plot_signal(array,mode)

    # Print the g_code to a text file
    f = open('gcode.txt', 'w')  #
    for i in g_code:
        f.write(str(i) + '\n')
    f.close()
    return g_code
