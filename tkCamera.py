#!/usr/bin/env python

# author: Bartlomiej "furas" Burek (https://blog.furas.pl)
# date: 2021.01.26
import os
import threading
import tkinter as tk
import tkinter.font as font
import tkinter.filedialog
import PIL.ImageTk
from PIL import Image
from lobe import ImageModel
from videocapture import VideoCapture
from main import HOME,MY_FONT
import TkWidgets

'''
This moduel holds the TkCamera and all of its dependencies. This moduel is used 
in the main App class.
'''

class TkCamera(tk.Frame):

    def __init__(self, parent, width=None, height=None, xml_dict=None):
        '''
        The class TkCamera holds the object videocapture which is the live feed of the 
        RTSP stream. Also inside this class there are the methods that use a frame
        from the videocapture to predict using an AI model from MicrosoftLobe
        '''
        super().__init__(parent)
        self.root = parent
        self.xml_dict = xml_dict
        self.width  = width
        self.height = height
        self.recording = False
        self.connected = False
        self.label_name = None
        self.img_score = None
        self.onnx_model = ImageModel.load(self.xml_dict['ModelPath'])
        self.manager = None
        BUTTON_FONT = font.Font(family = MY_FONT)


        # Button that lets the user take a snapshot
        self.canvas = tkinter.Canvas(self, width=self.width, height=self.height,borderwidth = 0,highlightthickness = 0)
        self.canvas.grid(row = 0,column = 0)
        img_place_holder_name = "resources\\NoCameraBlue.png"
        camera_place_holder_path = os.path.join(HOME,img_place_holder_name)
        self.img = Image.open(camera_place_holder_path)
        self.holder_photo = PIL.ImageTk.PhotoImage(image=self.img)
        self.canvas.create_image(0, 0, image=self.holder_photo, anchor='nw')

        self.btn_frame = tk.Frame(self.root,bg ='black')
        self.btn_frame.grid(row = 1,column =0,pady = 10)

        self.btn_snapshot = TkWidgets.HoverButton(self.btn_frame,bg = '#00d6ff',width = 10,
                                                  height = 2, activebackground = 'white',
                                                  text="Start",font = BUTTON_FONT, 
                                                  command=lambda:threading.Thread(target = self.snapshot).start())
        self.btn_snapshot.grid(row = 1,column = 0,padx = 5)
       
        self.btn_stop = TkWidgets.HoverButton(self.btn_frame,bg = '#00d6ff',width = 10,
                                              height = 2,activebackground = 'white',
                                              text = 'Stop',command = self.stop,font = BUTTON_FONT)
        self.btn_stop.grid(row = 1,column = 1,padx = 5)
        
        self.connect_btn = TkWidgets.HoverButton(self.btn_frame,bg = '#00d6ff',width = 10,
                                                 height = 2,activebackground = 'white',
                                                 text = 'Connect',command = self.connect,font = BUTTON_FONT)
        self.connect_btn.grid(row = 1,column = 2,padx = 5)

        self.disconnect = TkWidgets.HoverButton(self.btn_frame,bg = '#00d6ff',width = 10,
                                                height = 2,activebackground = 'white',
                                                text = 'Disconnect',command = self.disconnect,font = BUTTON_FONT)  
        self.disconnect.grid(row = 1,column = 3,padx = 5)
        
    def connect(self):
        if self.connected == False:           
            self.vid = VideoCapture(self.xml_dict, self.width, self.height) 
            if self.vid.connected:         
                self.delay = int(1000/self.vid.fps)        

                print('[TkCamera] source:', self.xml_dict['IpAddress'])
                print('[TkCamera] fps:', self.vid.fps, 'delay:', self.delay)

                self.image = None
                self.dialog = None
                self.running = True
                self.connected = True
                self.update_frame()
            else:
                print("Camera Timeout")
        else:
            tk.messagebox.showwarning('Camera Connection','Camera Is Already Connected.')
    def disconnect(self):
        self.running = False
        self.connected = False
        try:
            self.vid.disconnect()

        except:
            tk.messagebox.showwarning('Camera Connection','Camera Is Already Disconnected.')

    def stop(self):
        self.recording = False

    def predict_image(self):       
        ret,frame = self.vid.get_frame()
      
        result = self.onnx_model.predict(frame)
        return result
                       
    def calculate_pass_fail(self,result):
        calcResult = result.labels[0]
        self.label_name = calcResult[0]
        self.img_score = calcResult[1]*100

        return f"{self.label_name} {self.img_score}%"                  

    def snapshot(self):
        """TODO: add docstring"""

        # Get a frame from the video source
        #ret, frame = self.vid.get_frame()
        #if ret:
        #    cv2.imwrite(time.strftime("frame-%d-%m-%Y-%H-%M-%S.jpg"), cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))

        # Save current frame in widget - not get new one from camera - so it can save correct image when it stoped
        #if self.image:
        #    self.image.save(time.strftime("frame-%d-%m-%Y-%H-%M-%S.jpg"))
        if self.recording:
            print('Prediction in progress')
            return
        if self.connected:
            self.recording = True
            while self.recording:
                try:
                    #filename = self.vid.snapshot()
                    result = self.predict_image()
                    output = self.calculate_pass_fail(result)
                    if self.manager:
                        self.manager.on_click(output)
                    else:
                        print('something')

                    #time.sleep(int(self.xml_dict['PredictionRate']))
                except AttributeError as err:
                    self.recording = False
                    tk.messagebox.showwarning('Camera Connection','No Camera Connected.')
        else:
             tk.messagebox.showwarning('Camera Connection','No Camera Connected.')    

    def update_frame(self):
        """TODO: add docstring"""

        # widgets in tkinter already have method `update()` so I have to use different name -

        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.image = frame
            self.image = self.image.resize((1280,720))
            self.photo = PIL.ImageTk.PhotoImage(image=self.image)
            self.canvas.create_image(0, 0, image=self.photo, anchor='nw')

        if self.running:
            self.after(self.delay, self.update_frame)
        else:
            self.canvas.create_image(0, 0, image=self.holder_photo, anchor='nw')
            del self.vid



