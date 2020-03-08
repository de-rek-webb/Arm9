from tkinter import *
from tkinter import ttk
import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
import datetime as dt
import argparse
import imutils
from imutils import face_utils
import dlib
import numpy as np
from numpy import newaxis
import matplotlib.pyplot as plt
import Audio_Processing
import Face_Processing
import G_Code_Generator
import serial
import os

class App:
    def __init__(self, window, window_title, video_source=0):
#OpenCV/Dlib Initializations:
        self.video_source = video_source
        self.face_cascade = cv2.CascadeClassifier(os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir,'Machine_Learning_Files','haarcascade_frontalface_default.xml')))
        self.landmark_model = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir,'Machine_Learning_Files','shape_predictor_68_face_landmarks.dat'))
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.landmark_model)
        self.vid = VideoCapture( self.video_source) #Open Videosource - Default is webcam
#Tkinter Initializations:
        self.window = window
        self.window.title(window_title)
        self.G_Code = tk.StringVar()
        self.frame = tk.Frame(self.window)
        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height) # Create a canvas that can fit the above video source size
        self.canvas.pack()
#~~Buttons~~
    #Draw Button
        self.btn_capture=tk.Button(self.frame, text="Draw Me!", bg = "green",fg = "white",width = 25,height = 2, command=self.capture)
        self.btn_capture.pack(side=tk.LEFT)
    #Record Audio Button
        self.btn_record=tk.Button(self.frame, text="Listen",bg = "blue",fg = "white",width = 25, height = 2, command = self.audio_recording)
        self.btn_record.pack(side=tk.LEFT)
        self.frame.pack()
    #Quit button
        self.btn_quit=tk.Button(self.frame, text='QUIT',bg = "red",fg = "white",width = 25,height = 2, command=self.close)
        self.btn_quit.pack(side=tk.RIGHT)
    #Add another frame to pack additional buttons
        self.frame2 = tk.Frame(self.window)
        self.frame2.pack()
    #Label
        self.label1 = tk.Label(self.frame2,text="Manual G-Code: ")
        self.label1.pack(side = tk.LEFT)
    #Text Entry
        self.text_entry=ttk.Entry(self.frame2,textvariable = self.G_Code)
        self.text_entry.pack(side=tk.LEFT)
    #Demo Button
        self.btn_demo = tk.Button(self.frame2, text = 'DEMO', bg = "green", fg = "white", width = 25, height = 2, command = self.demo)
        self.btn_demo.pack(side = tk.RIGHT)
    #Send Button
        self.btn_send = tk.Button(self.frame2, text = 'SEND',bg = "purple",fg = 'white', width = 25, height = 2, command = self.manual)
        self.btn_send.pack(side = tk.RIGHT)


# Serial Communication
#~~~~~~~~~~~~~~
#        self.ser = serial.Serial('COM3', baudrate = 115200, timeout = 1)
#        time.sleep(3)
#        self.ser.reset_input_buffer()
        # ser.write(b'%')
        # time.sleep(1)
#        arduinoData = self.ser.readline().decode('ascii')
#        print(arduinoData)
#~~~~~~~~~~~~~~

    # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay=10
        self.update()

        self.window.mainloop()


    def close(self):
        self.ser.close()
        tk.quit()


    def send_code(self,g_code = None):
        """Send g-code line by line over serial port"""
        for i in g_code:
            self.ser.write((i + '\n').encode('utf-8'))
            time.sleep(0.5)
            while self.ser.in_waiting:
                print(self.ser.readline())

        return

    def demo(self):
        g_code = G_Code_Generator.main('demo')
        self.send_code(g_code)

    def audio_recording(self):
        my_audio = Audio_Processing.audio_main()
        g_code = G_Code_Generator.main('sound',my_audio)
        self.send_code(g_code)

    def clear_entry(self):
        self.text_entry.delete(0,'end')

    def manual(self):
        text = self.G_Code.get()
        print(text)
        text_array = [text]
        self.send_code(text_array)
        self.clear_entry()


    def show_info(self,msg):
        popup = tk.Tk()
        popup.wm_title("!")
        label = tk.Label(popup, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = tk.Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        print("Should be throwing error message")
        popup.mainloop()

    def find_rect(self,rect):
        x = rect.left()
        y = rect.top()
        w = rect.right() - x
        h = rect.bottom() - y
        return(x,y,w,h)

    def shape_to_np_jaw(self,shape,x1,y1,w,h,dtype = np.int32):
        coords = np.zeros((18,2), dtype = dtype)
        for i in range(0,18):
            if i == 0:
                coords[i][0] = x1
                coords[i][1] = y1
            elif i == 17:
                coords[i][0] = x1+w
                coords[i][1] = y1
            else:
                coords[i][0] = shape.part(i).x
                coords[i][1] = shape.part(i).y
        new_coords = coords.reshape(1,18,2)

        return new_coords

    def dodge(self,front,back):
        return cv2.divide(front, 255-back,scale=256)


    def sort_x(self, array):
        x_array = []
        for coord in range(len(array)):
            for j in range(len(array[coord])):
                if(j==0):
                    x_array = np.append(x_array,array[coord][j])
        return x_array

    def sort_y(self, array):
        y_array = []
        for coord in range(len(array)):
            for j in range(len(array[coord])):
                if(j==1):
                    y_array = np.append(y_array,array[coord][j])
        return y_array

    def thin_array(self, array):
        array[1::5]
        return array



    def capture(self):
        # Get a frame from the video source
        ret,frame=self.vid.get_frame()

        if ret:
            rects = self.detector(frame, 0)
            print("Rects: ",rects)
            if len(rects) == 0:
                self.show_info("No faces detected!")
            else:
                coords = Face_Processing.face_to_dotmap(frame,rects)
                x_array = self.sort_x(coords)
                y_array = self.sort_y(coords)

                x_array = [arr for i,arr in enumerate(x_array) if i % 5 == 0]
                y_array = [arr for i,arr in enumerate(y_array) if i % 5 == 0]
                coord_array = np.column_stack((x_array,y_array))

                plt.plot(x_array,y_array,"ro")
                plt.show()
                g_code = G_Code_Generator.main('face',coord_array)
                self.send_code(g_code)


    def update(self):

        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
        self.window.after(self.delay,self.update)


class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
#        check, frame = video.read()

        # Command Line Parser
        args=CommandLineParser().args


        #create videowriter

        # 1. Video Type
        VIDEO_TYPE = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            #'mp4': cv2.VideoWriter_fourcc(*'H264'),
            'mp4': cv2.VideoWriter_fourcc(*'XVID'),
        }

        # 2. Video Dimension
        STD_DIMENSIONS =  {
            '480p': (640, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '4k': (3840, 2160),
        }
        res=STD_DIMENSIONS[args.res[0]]


        #set video sourec width and height
        self.vid.set(3,res[0])
        self.vid.set(4,res[1])

        # Get video source width and height
        self.width,self.height=res


    # To get frames
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)
        else:
            return (ret, None)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

            cv2.destroyAllWindows()



class CommandLineParser:

    def __init__(self):

        parser=argparse.ArgumentParser(description='Script to record videos')


        parser.add_argument('--res', nargs=1, default=['480p'], type=str, help='Resolution of the video output: for now we have 480p, 720p, 1080p & 4k')

        self.args = parser.parse_args()



def main():

    App(tk.Tk(),'Canny GUI')

main()
