#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video OculoGrapher 
2 
Created on Mon Dec 30 17:46:03 2019

@author: Jorge Rey Martinez
"""
import vCamera
import cv2
import tkinter
import PIL.Image, PIL.ImageTk
import time
import configparser
from tkinter import messagebox
import pygubu
import pathlib
import sys
import numpy
from board import board

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "VOG_gui.ui"
limitFPS = 10 ##to change FPS into red
camCenter = None
boardControl = None
serialConect = False
camMaxBr = 65.0 # depends of cammera
camMaxCn = 65.0 # depends of cammera
camDefBr = 35.0 # depends of cammera
camDefCn = 35.0 # depends of cammera
guiDelay = 1  # This is GUI refresh timedelay in ms


def highpriority():
    try:
        sys.getwindowsversion()
    except AttributeError:
        isWindows = False
    else:
        isWindows = True

    if isWindows:
        import win32api,win32process,win32con

        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
    else:
        import os
        os.nice(17) #from 0 to 19 higher is best
        
def arduCheck():
        global mainWindowObj, boardControl, serialConect
        config = configparser.ConfigParser()
        serialConect = True
        try:
            config.read_file(open("CameraConfig.ini", mode = "r"))
            serialNumber= config.get("CAMERA","serial")
        except:
            serialConect = False
            print("No COM Port in config")
            
        if serialConect:
            boardControl = board(serialNumber)
            if not boardControl.status():
                serialConect = False
                print("Board connection COM error")
        appVOG()
    

def videoCheck():  
    global camCenter
    config = configparser.ConfigParser()    
    try:
        config.read_file(open("CameraConfig.ini", mode = "r"))
    except:
        print("No config file was found,a new one will be created")
        config.add_section("CAMERA")
        config.set("CAMERA","center_camera","0")
        config.set("CAMERA","serial","COM3")
        config.set("CAMERA","help! ","You must set cammera device allways as a number, the number 0 is the first value. COM number can be read in windows hardware com-serial devices")
        try:
            with open("CameraConfig.ini",mode = "w") as newfile:
                config.write(newfile)
                config.clear()
        except:
            print("Config file fatal error: It was not possible to write file")
            return
    
    config.read("CameraConfig.ini")
    try:
        defaultC= int(config.get("CAMERA","center_camera"))
    except:
        print("Config file fatal error: Not Camera info were found!, you can erase 'CameraCongfig.ini' file")    
        return          
    
    def cameraError(errorCamera, defaultC= 0):
        global camCenter
        del camCenter
        
        def launchCameraSelector():
            camerasWindow.destroy()
            cameraSelector(True)
            
        if errorCamera == 0:
            errorText = "There was an error at least on central cammera "
        else:
            errorText = "There was an error on any cammera "
            
        camerasWindow = tkinter.Tk()
        camerasWindow.title("Cameras configuration error")
        camerasWindow.geometry("+20+20")
        camerasWindow.focus_set()
        labelA = tkinter.Label(camerasWindow, text=errorText, anchor = "w", width= 49)
        labelA.grid(column= 0, row= 0)
        labelB = tkinter.Label(camerasWindow, text="Try to manually select the cammeras or press EXIT to QUIT", anchor="w", width= 49)
        labelB.grid(column= 0, row= 1)
        labelSpace = tkinter.Label(camerasWindow, text="", anchor="w", width= 49)
        labelSpace.grid(column= 0, row= 2)
        buttonExit = tkinter.Button(camerasWindow, text="EXIT to system", command= camerasWindow.destroy)
        buttonExit.grid(column= 1, row= 3)
        buttonExit = tkinter.Button(camerasWindow, text="Manual camera selection", command= launchCameraSelector)
        buttonExit.grid(column= 0, row= 3, sticky= "w")
        camerasWindow.mainloop()
        
    error = True
    try:
        camCenter = vCamera.videoCamera(defaultC, inGray= True)
        error = False  
    except:  
        error = True


    if not error:
        arduCheck()
    else:
        cameraError(0, defaultC)


def cameraSelector(isFromError= False):

    def cameraList():
        availableList=list()
        cam = 0
        while cam < 8:
            try:
                vCamera.videoCamera(cam)
                availableList.append(cam)
            except:
                print("Camera is not availabe on: ", cam)
            cam += 1
        return availableList
        
    availCameras= cameraList()
    
    def cameraValidation():
        labelValidation.config(text= "Checking new configuration, please wait...")
        candidateC = cSelection.get()
        global camCenter
        try:
            camCenter = vCamera.videoCamera(candidateC, inGray= True)
        except:
            messagebox.showwarning("Config file fatal error: It was not possible to set cammeras. Exit to system")
            selectionWindow.destroy()
        if messagebox.askyesno("ErrorConfiguration success","Do you want to save the new configuration?"):
            try:
                configNew = configparser.ConfigParser()
                configNew.add_section("CAMERA")
                configNew.set("CAMERA","center_camera","0")
                configNew.set("CAMERA","serial","COM3")
                configNew.set("CAMERA","help! ","You must set cammera device allways as a number, the number 0 is the first value. COM number can be read in windows hardware com-serial devices")
                with open("CameraConfig.ini", mode = "w") as writingFile:
                    configNew.write(writingFile)
                    writingFile.close()
                        
            except:
                messagebox.showwarning("It was not possible to save the new configuration!")
        selectionWindow.after(100, selectionWindow.destroy())
        if isFromError:
            arduCheck()
        else:
            appVOG()
            
            
            
    selectionWindow= tkinter.Tk()
    selectionWindow.title("Cameras manual configuration")
    selectionWindow.geometry("+20+20")
    selectionWindow.focus_set()
    labelInfo = tkinter.Label(selectionWindow, text= "Please, select cammera", pady=10)
    labelInfo.grid(column= 0, row= 0,columnspan= 1)
    labelTitleR = tkinter.Label(selectionWindow, text= "Center cammera")
    labelTitleR.grid(column= 0, row= 1)
    labelValidation = tkinter.Label(selectionWindow, text= "Click Validate to check configuration...", width= 50, pady= 20)
    labelValidation.grid(column= 0, row= 3, columnspan= 2)
    buttonExit = tkinter.Button(selectionWindow, text="Dismiss", command= selectionWindow.destroy)
    buttonExit.grid(column= 1, row= 4)
    buttonValidate = tkinter.Button(selectionWindow, text="Validate", command= cameraValidation)
    buttonValidate.grid(column= 0, row= 4)
    #Radiobuttons for cammera
    frameCenterCam = tkinter.Frame(selectionWindow)
    frameCenterCam.grid(column= 0,row=2)
    cSelection = tkinter.IntVar()
    for camNum in availCameras:
        tkinter.Radiobutton(frameCenterCam,text = str("Cammera: "+ str(camNum)), value = camNum, variable = cSelection).pack()
        
    if len(availCameras) < 1:
        messagebox.showwarning("Warning","No cameras were found!")
    else:
        pass #nothing to do now... but who knows?
            
    selectionWindow.mainloop()        


class appVOG:
    global camCenter, camMaxBr, camMaxCn, guiDelay, boardControl, serialConect
    
    def __init__(self,master=None):
        #image selection parameters
        self.selectRx = 20
        self.selectRy = 35
        self.selectLx = 140
        self.selectLy = 35
        self.selectWid = 100
        self.selectHigh = 80
        
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainVOG = builder.get_object("mainVOG", master)
        #self.CtrValue: tkinter.DoubleVar = None
        #self.BrnValue: tkinter.DoubleVar = None
        self.fixationControlText: tkinter.StringVar = None
        self.fixationControlState: tkinter.BooleanVar() = None
        builder.import_variables(self)
        callbacks = {
            "setcam": self.loadCameraSelector,
            "srUp": self.movRselUp,
            "srDn": self.movRselDn,
            "srRg": self.movRselRg,
            "srLf": self.movRselLf,
            "slUp": self.movLselUp,
            "slDn": self.movLselDn,
            "slRg": self.movLselRg,
            "slLf": self.movLselLf,
            "ctrChange": self.setCnCnt,
            "brgChange": self.setCnBr,
            "fixationChange": self.fixationChange,
        }
        builder.connect_callbacks(callbacks)
        
        self.miniR = builder.get_object("miniR")
        self.miniL = builder.get_object("miniL")
        self.fps = builder.get_object("fps")
        self.ctrControl = builder.get_object("ctrControl")
        self.brgControl = builder.get_object("brgControl")
        self.rightEye = builder.get_object("rightEye")
        self.leftEye = builder.get_object("leftEye")
        self.fixationControlButton = builder.get_object("fixationControl")
        self.controlStatusText = builder.get_object("controlStatus")
        self.logoCanvas = builder.get_object("logo")
        self.ctrControl.configure(to=camMaxCn);
        self.brgControl.configure(to=camMaxBr);
        self.ctrControl.set(camDefCn);
        self.brgControl.set(camDefBr);
        blank_image = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(numpy.zeros((144,256,3), numpy.uint8)))
        self.imageLitR = self.miniR.create_image(0, 0, image = blank_image, anchor = tkinter.NW)
        self.imageLitL = self.miniL.create_image(0, 0, image = blank_image, anchor = tkinter.NW)
        self.rightEyeImg = self.rightEye.create_image(0, 0, image = blank_image, anchor = tkinter.NW) 
        self.leftEyeImg = self.leftEye.create_image(0, 0, image = blank_image, anchor = tkinter.NW) 
        self.roiR = self.miniR.create_rectangle(self.selectRx,self.selectRy,(self.selectRx+self.selectWid),(self.selectRy+self.selectHigh),outline="red",width=2)
        self.roiL = self.miniL.create_rectangle(self.selectLx,self.selectLy,(self.selectLx+self.selectWid),(self.selectLy+self.selectHigh),outline="blue",width=2)
        camCenter.vid.set(cv2.CAP_PROP_BRIGHTNESS,camDefBr)
        camCenter.vid.set(cv2.CAP_PROP_CONTRAST,camDefCn)
        
        #logoLoad
        try: 
            logo = PIL.ImageTk.PhotoImage(image= PIL.Image.open("logo.png").resize((350,154)))
        except:
            print("No logo file image")
            logo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(numpy.zeros((154,350,3), numpy.uint8)))
        self.logoImg = self.logoCanvas.create_image(0, 0, image = logo, anchor = tkinter.NW)
        
        
        self.counterFPS = 1
        self.pstamp = time.localtime()[5]
        self.actualFPS = 0
        self.fixationControlText.set("OFF")
        if boardControl.status():
            boardControl.setIR(True)
            self.fixationControlButton.configure(state = "enabled")
            self.controlStatusText.configure(text= "Board conection OK")
            
        else:
            self.fixationControlButton.configure(state = "disabled")
            self.controlStatusText.configure(text= "Board conection ERROR")

        self.mainVOG.after(guiDelay, self.update)
        self.mainVOG.mainloop()    
    
    def loadCameraSelector(self):
        global camCenter
        try:
            del camCenter
        except:
            pass
        self.mainVOG.destroy()
        cameraSelector(False)
        
    def setCnBr(self, value):
        global camCenter
        camCenter.vid.set(cv2.CAP_PROP_BRIGHTNESS,float(value))
    
    def setCnCnt(self, value):
        global camCenter
        camCenter.vid.set(cv2.CAP_PROP_CONTRAST,float(value))
    
    def movRselUp(self):
        if self.selectRy > 2:
            self.selectRy -= 1
            self.miniR.move(self.roiR,0,-1)
    
    def movRselDn(self):
        if (self.selectRy+self.selectHigh) < 144:
            self.selectRy += 1
            self.miniR.move(self.roiR,0,1)

    def movRselRg(self):
        if self.selectRx > 2:
            self.selectRx -= 1
            self.miniR.move(self.roiR,-1,0)
    
    def movRselLf(self):
        if (self.selectRx+self.selectWid) < 256:
            self.selectRx += 1
            self.miniR.move(self.roiR,1,0)
    
    def movLselUp(self):
        if self.selectLy > 2:
            self.selectLy -= 1
            self.miniL.move(self.roiL,0,-1)
    
    def movLselDn(self):
        if (self.selectLy+self.selectHigh) < 144:
            self.selectLy += 1
            self.miniL.move(self.roiL,0,1)
    
    def movLselRg(self):
        if self.selectLx > 2:
            self.selectLx -= 1
            self.miniL.move(self.roiL,-1,0)
    
    def movLselLf(self):
        if (self.selectLx+self.selectWid) < 256:
            self.selectLx += 1
            self.miniL.move(self.roiL,1,0)
    
    def fixationChange(self):
        if self.fixationControlState.get():
            boardControl.setLed(True)
            self.fixationControlText.set("ON")
        else:
            boardControl.setLed(False)
            self.fixationControlText.set("OFF")
    
    def update(self):
        global camCenter,guiDelay
        ret,frame = camCenter.get_frame()
        
        if ret:
            self.scaleBat = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv2.resize(frame,(256,144))))
            self.scaleBi = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv2.resize(frame[self.selectRy*5:(self.selectRy+self.selectHigh)*5,self.selectRx*5:(self.selectRx+self.selectWid)*5],(900,720))))
            self.scaleIru = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv2.resize(frame[self.selectLy*5:(self.selectLy+self.selectHigh)*5,self.selectLx*5:(self.selectLx+self.selectWid)*5],(900,720)))) 
            self.miniL.itemconfig(self.imageLitL, image = self.scaleBat)
            self.miniR.itemconfig(self.imageLitR, image = self.scaleBat)
            self.rightEye.itemconfig(self.rightEyeImg, image =  self.scaleBi)
            self.leftEye.itemconfig(self.leftEyeImg, image = self.scaleIru)

        if self.pstamp == time.localtime()[5]:
            self.counterFPS += 1
        else:
            self.fps.config(text="APP_FPS: " + str(self.counterFPS))
            self.actualFPS = self.counterFPS
            self.counterFPS = 1
            self.pstamp = time.localtime()[5]
            if self.actualFPS < limitFPS:
                self.fps.config(foreground = "red")
            else:
                self.fps.config(foreground = "black")
        
        self.mainVOG.after(guiDelay, self.update)

    def __del__(self):
        global camCenter, boardControl
        try:
            del camCenter
            del boardControl
        except:
            pass
        
        print("Good Bye !!!")
        
#Start the app   
highpriority()   
videoCheck()
    