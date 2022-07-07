import time
import threading
import cv2
import PIL.Image
from multiprocessing import Process
import os
'''
This moduel contains the VideoCapture class which is the
controller for handling the live feed of the RTSP camera
link.
'''

class VideoCapture:
    def __init__(self, xml_dict=None, width=None, height=None):
        '''
        VideoCapture is responsible for the processing of 
        the live feed of our RTSP camera from config.xml.

        This class is also responsible for grabbing frames
        from the stream and taking snapshots as well as.
        '''

        self.xml_dict = xml_dict
        self.width = width
        self.height = height
        self.fps = int(self.xml_dict['FPS'])
        self.running = False
        self.connected = False
        # Open the video source
        self.vid = None
        # self.vid = cv2.VideoCapture(self.xml_dict['IpAddress'])

        # Use multiprocess to timeout connection after 10 seconds
        p1 = Process(target=self.connect)
        p1.start()
        p1.join(10)
        if p1.is_alive():

            # Terminate - may not work if process is stuck for good
            p1.terminate()
            # OR Kill - will work for sure, no chance for process to finish nicely however
            # p.kill()

            p1.join()
        if not self.connected:
            pass
        else:
        
            # Get video source width and height
            if not self.width:
                self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))    # convert float to int
            if not self.height:
                self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))  # convert float to int
            if not self.fps:
                self.fps = int(self.vid.get(cv2.CAP_PROP_FPS))              # convert float to int

            # default value at start
            self.ret = False
            self.frame = None

            self.convert_color = cv2.COLOR_BGR2RGB
            #self.convert_color = cv2.COLOR_BGR2GRAY
            self.convert_pillow = True

            # start thread
            self.running = True
            print("Thread runnings")
            self.thread = threading.Thread(target=self.process)
            self.thread.start()


    def connect(self):
        try:
            print(os.getpid())
            self.vid = cv2.VideoCapture(self.xml_dict['IpAddress'])
            self.connect = True
        except:
            print("No connection")

    def snapshot(self, filename=None):
        """TODO: add docstring"""

        if not self.ret:
            print('[MyVideoCapture] no frame for snapshot')
        else:
            if not filename:
                filename = time.strftime(self.xml_dict['FailImgagePath'] + "/frame-%d-%m-%Y-%H-%M-%S.jpg")

            if not self.convert_pillow:
                cv2.imwrite(filename, self.frame)
                print('[MyVideoCapture] snapshot (using cv2):', filename)
                return filename
            else:
                self.frame.save(filename)
                print('[MyVideoCapture] snapshot (using pillow):', filename)
                return filename

    def process(self):
        """TODO: add docstring"""

        while self.running:

            ret, frame = self.vid.read()

            if ret:
                # process image
                #frame = cv2.resize(frame, (self.width, self.height))

                # it has to record before converting colors
                if self.convert_pillow:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = PIL.Image.fromarray(frame)
            else:
                print('[MyVideoCapture] stream end')
                self.running = False

            # assign new frame

            self.ret = ret
            self.frame = frame
            #time.sleep(1 / int(self.fps))

    def get_frame(self):

        return self.ret, self.frame

    def disconnect(self):
        self.vid.release()
        self.running = False

    # Release the video source when the object is destroyed
    def __del__(self):
        """TODO: add docstring"""

        # stop thread
        if self.running:
            self.running = False
            self.thread.join()

        # relase stream
        if self.connected:
            if self.vid.isOpened():
                self.vid.release()

