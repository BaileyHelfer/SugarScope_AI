'''
python version: 3.9
author: Bailey Helfer
date: 08.26.2021
'''
import os,sys
import json
import datetime
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as st
from tkinter import messagebox
from PIL import Image,ImageTk
import time
from xml.etree import cElementTree as ElementTree
import winsound
from cryptography.fernet import Fernet
import tkCamera
from XMLHandler import XmlDictConfig
import threading


#Determines if script is running in debugger or as .exe
if getattr(sys,'frozen',False):

    HOME = os.path.dirname(sys.executable)
else:
    HOME = os.path.dirname(__file__)

LICENSE_NAME = 'license.json'
MY_FONT = "Segoe Ui Semibold"
license_path = os.path.join(HOME,LICENSE_NAME)
LONG_KEY = 'HIAvBtDmOHc7Gi9le_kK-Qa5dDA6eirRcpCxkjFVuhg='

def decrypt_message(encrypted_message):
    key = LONG_KEY
    f = Fernet(key)
    decrypted_message = f.decrypt((encrypted_message))

    return decrypted_message.decode()

def encrypt_message(message):
    key = LONG_KEY
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return str(encrypted_message)

def write_json(data, filename):
    '''
    Uses JSON data and filename to store that data in JSON file.
    '''
    with open(filename,"w") as f:
        json.dump(data,f)

def open_json():
    '''
    Opens JSON file aand return the content as a Python Dictionary.
    '''
    with open(license_path) as jsonfile:
        json_dict = json.load(jsonfile)
    return json_dict

def program_expiration(root):
    '''
    Checks if the programs license is expired
    Opens up the license file and gets the date the program started up.
    Checks if it is programs first time loading up, if so then set the start date to the current date.
    If not then get the date the program first started and comapre it to the expiration date to see
    program is expired.
    If program is expired then pop up the license registartion screen.
    '''
    json_dict = open_json()
    if json_dict['ace'] == "":
        now = datetime.datetime.now()
        start_time = now.strftime("%m-%d-%Y")
        start_time_encrypt = encrypt_message(start_time)
        json_dict['ace'] = start_time_encrypt
        write_json(json_dict,license_path)
    else:
        start_date_encrypt_setup = json_dict['ace'][1:]
        start_date_encrypt_setup = start_date_encrypt_setup.encode('utf-8')
        start_date_decrypt = decrypt_message(start_date_encrypt_setup)

        start_date = datetime.datetime.strptime(start_date_decrypt, "%m-%d-%Y")
        expire_date = start_date + datetime.timedelta(days = 31)
        if datetime.datetime.now() > expire_date:
            LicenseRegistration(root)
            return True      
        return False

class OutputManager(object):
    '''
    OutputManager is used to update the result textbox
    in the App clas with data from tkCamera class as 
    well as play a sound when failure condition is met.
    '''
    def __init__(self, gui,cam,xml_dict):
        self.gui = gui
        self.cam = cam
        self.gui.widget.manager = self
        self.xml_dict = xml_dict
        self.class_list = self.xml_dict['ClassToPass'].split(',')
        
    def on_click(self,output):
        '''
        Method that takes the score and result label from predicted image and determines if it is pass or fail.
        1.If image passes prediction then print out with green highlight.
        2.If image failes print out with red highlight and play_alarm.
        '''
        self.gui.result_box.config(state = 'normal')
        
        if self.cam.label_name in self.class_list and self.cam.img_score > float(self.xml_dict['ConfidenceThreshold']):
            self.gui.result_box.insert('1.0',output+"%\n",("Pass"))
            self.gui.live_result.delete('1.0',tk.END)
            self.gui.live_result.insert('1.0',output)
            t1 = threading.Thread(target = self.cam.vid.snapshot)
            t1.start()
        else:
            self.gui.result_box.insert('1.0',output+"%\n",("Fail"))
            self.gui.live_result.delete('1.0',tk.END)
            self.gui.live_result.insert('1.0',output)
            self.gui.result_box.config(state = 'disabled')
            s = self.xml_dict['SaveFails']
            if s.lower() in ['true','1','t','yes','y']:
                t1 = threading.Thread(target = self.cam.vid.snapshot)
                t1.start()
            #t1 = threading.Thread(target = self.play_alarm)
            #if not t1.is_alive():
            #    t1.start()            

    def play_alarm(self):
        '''
        Plays sound from config.xml when called.
        '''
        winsound.PlaySound(self.xml_dict['AlarmAudioPath'],winsound.SND_FILENAME)
        #playsound(self.xml_dict['AlarmAudioPath'])
        

class LicenseRegistration(tk.Toplevel):
    '''
    TopLevel window object that holds the license registration proccess.
    Window opens up if the license for program is expired.
    '''
    def __init__(self,parent):
        super().__init__(parent)
        
        self.parent = parent
        self.resizable(False,False)
        self.config(bg = '#a9a9a9')

        w = 300 # width for the Tk root
        h = 150 # height for the Tk root
        ws = self.parent.winfo_screenwidth() # width of the screen
        hs = self.parent.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)       
        self.geometry('%dx%d+%d+%d' % (w, h, x, y-25)) #Places the window in the middle of the parent window when spawned
        self.title("License Registration")

        now = datetime.datetime.now()
        month = now.strftime("%m")
        self.key = "ussvision"+str(month)

        self.pass_label = tk.Label(self,text = 'Enter in product key',bg = '#a9a9a9')#Title label of window
        self.pass_label.config(font = (MY_FONT,20))
        self.pass_label.grid(column = 0,row = 0,columnspan = 2)

        self.pass_entry = tk.Entry(self,text = 'Product Key',width = 20) #Entry box to enter in license
        self.pass_entry.grid(column  = 0,row = 1)
        self.pass_entry.config(font=(MY_FONT,10))

        self.enter_btn = tk.Button(self,text = "Register Key",command = self.check_key) #Button that checks to see if license entered is valid
        self.enter_btn.grid(column = 1,row = 1,sticky = 'w')
        self.enter_btn.config(font = (MY_FONT,10))
        self.bind('<Return>',lambda event:self.check_key())

        self.focus_force()
        self.grab_set()
        messagebox.showinfo('License Registration','No Valid License Key Found')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)       

    def check_key(self):
        json_dict = open_json()
        user_key = str(self.pass_entry.get())
        if user_key == self.key:
            month_user_key = user_key[-2:]
            date_encrypt_setup = json_dict['ace'][1:]
            date_encrypt_setup = date_encrypt_setup.encode('utf-8')
            date_decrypt = decrypt_message(date_encrypt_setup)
            date_decrypt = date_decrypt[:2]
            if month_user_key == date_decrypt:
                messagebox.showinfo("License Registration", "Key not active!")
                return
            current_date = datetime.datetime.now()
            newexpire_date = current_date + datetime.timedelta(days = 90)
            jsonexpire_date = newexpire_date.strftime("%m-%d-%Y")
            json_expire_encrypt = encrypt_message(jsonexpire_date)
            json_dict['ace'] = json_expire_encrypt
            write_json(json_dict,license_path)
            self.grab_release()
            messagebox.showinfo("License Registration",f"License Registered! Your program is now registered until:{jsonexpire_date}.")
            self.destroy()
        else:
            messagebox.showinfo("License Registration", "Incorrect License Key!")
    def on_closing(self):
        self.destroy()
        self.quit()

class Splash(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.config(bg = 'grey')
        self.columnconfigure(0,weight = 1)
        w = 350 # width for the Tk root
        h = 320 # height for the Tk root
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.img = Image.open(r'C:\Users\bailey\source\old_repo\repos\LiveStreamVideoAPP\LiveStreamVideoAPP\resources\splash.png')
        newsize = (300,250)
        self.img = self.img.resize(newsize)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y-25))
        label = tk.Label(self,image = self.tkimg)
        label.grid(row=0,column=0,pady = 3)
        self.prog_label = tk.Label(self,text = 'Loading...',bg = 'grey')
        self.prog_label.grid(row = 1,column = 0,pady = 2)
        self.progress = ttk.Progressbar(self,orient = tk.HORIZONTAL,length = 100,mode = 'determinate')
        self.progress.grid(column = 0,row = 2)
        self.overrideredirect(1)
        self.update()

    def bar(self):
        self.progress['value'] = 20
        self.update_idletasks()
        time.sleep(1)
  
        self.progress['value'] = 40
        self.prog_label.config(text = 'Checking License')
        self.update_idletasks()


        self.progress['value'] = 60
        self.update_idletasks()
        time.sleep(1)
  
        self.progress['value'] = 100
        self.update_idletasks()
        time.sleep(1)

class App:
    '''
    App is the main class for our GUI that holds everything in place.
    Inside this class we have all of the atributes that go inside of
    the GUI and call the other classes such as tkCamera and OutputManager.
    '''
    def __init__(self, parent, title, xml_dict):
        self.parent = parent
        self.xml_dict = xml_dict

   
        self.parent.config(bg = 'black')
        #self.parent.columnconfigure(1,weight = 1)
        #self.parent.columnconfigure(0,weight = 2)
        #self.parent.rowconfigure(0,weight = 2)
        #self.parent.rowconfigure(1,weight = 1)
        self.parent.title(title)
        width = 1280
        height = 720
        self.parent.withdraw()
        splash = Splash(self.parent)
        splash.bar()
        self.widget = tkCamera.TkCamera(self.parent, width, height, self.xml_dict)       
        self.widget.grid(row = 0,column = 0)

        self.frame = tk.Frame(self.parent,bg = 'black')
        self.frame.grid(row = 0,column = 1,sticky = 'nw',padx = 5)
        self.frame.rowconfigure(0,weight = 1)
        self.frame.rowconfigure(1,weight = 1)

        self.result_label = tk.Label(self.frame,text = 'Prediction Results',bg = 'black',fg = '#9d9d9d')
        self.result_label.grid(row = 0,column = 0,sticky = 'w')
        self.result_label.config(font = (MY_FONT,20,'bold'))

        self.result_box = st.ScrolledText(self.frame,height = 25,width = 40,bg ='#2b2b2b' )
        self.result_box.vbar.config(troughcolor = 'red')
        self.result_box.tag_add('Pass','current','end-1line')
        self.result_box.tag_config("Pass", background= "green", foreground= "white")
        self.result_box.tag_add('Fail','current','end-1line')
        self.result_box.tag_config("Fail", background= "red", foreground= "white")
        self.result_box.grid(row =1,column = 0)
        self.result_box.config(state = 'disabled',font = (MY_FONT,12))

        self.live_result_label = tk.Label(self.frame,text = 'Current Prediction: ',bg = 'black',fg ='#9d9d9d')
        self.live_result_label.grid(row = 2,column = 0,sticky = 'w')
        self.live_result_label.config(font = (MY_FONT,20 ,'bold'))

        self.live_result = tk.Text(self.frame,bg = '#2b2b2b',width =30,height = 1,fg = 'white',borderwidth = 0,highlightthickness = 0)
        self.live_result.config(font = (MY_FONT,17 ,'bold'))
        self.live_result.grid(row = 3,column = 0)
        
        
        OutputManager(self,self.widget,self.xml_dict)
        
        splash.destroy()
        splash.quit()

        self.parent.deiconify()
        self.parent.iconbitmap(self.xml_dict['LogoIconPath'])
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        '''
        When the program is closed stop thread running stream
        and close out window and program.
        '''

        print("[App] stoping threads")
        try:
            self.widget.recording = False
            self.widget.vid.running = False
            del self.widget.vid
        except:
            print('Video Not running no threads to stop')
        try:
            del self.widget
        except:
            print('test')
        

        print("[App] exit")
        
        self.parent.quit()
        self.parent.destroy()             

if __name__ == "__main__":
    tree = ElementTree.parse('config.xml')
    xmlRoot = tree.getroot()
    xml_dict = XmlDictConfig(xmlRoot)
    root = tk.Tk()
    w = 1700 # width for the Tk root
    h = 800 # height for the Tk root
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen
    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    # set the dimensions of the screen
    # and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, x, y-25))
    App(root, "SugarScopeAI", xml_dict)
    program_expiration(root)
    root.mainloop()
