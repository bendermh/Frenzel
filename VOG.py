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
from multiprocessing.dummy import Pool as ThreadPool
from tkinter import messagebox

MYNAME = "Digital Stereo Video-Oculographer"
pool = ThreadPool()
actualFPS = 0
limitFPS = 20
camRight = None
camLeft = None


def initialCheck():  
    global camRight, camLeft
    config = configparser.ConfigParser()    
    try:
        config.read_file(open("CameraConfig.ini", mode = "r"))
    except:
        print("No config file was found,a new one will be created")
        config.add_section("CAMERA")
        config.set("CAMERA","right_camera","0")
        config.set("CAMERA","left_camera","1")
        config.set("CAMERA","help! ","You must set cammera device allways as a number, the number 0 is the first value")
        try:
            with open("CameraConfig.ini",mode = "w") as newfile:
                config.write(newfile)
                config.clear()
        except:
            print("Config file fatal error: It was not possible to write file")
            return
    
    config.read("CameraConfig.ini")
    try:
        defaultR= int(config.get("CAMERA","right_camera"))
        defaultL= int(config.get("CAMERA","left_camera"))
    except:
        print("Config file fatal error: Not Camera info were found!, you can erase 'CameraCongfig.ini' file")    
        return          
    
    def cameraError(errorCamera,defaultR= 0,defaultL= 1):
        global camRight, camLeft
        del camRight
        del camLeft
        
        def launchCameraSelector():
            camerasWindow.destroy()
            cameraSelector(True)
            
        if errorCamera == 0:
            errorText = "There was an error at least on Right cammera, "
        elif errorCamera == 1:
            errorText = "There was an error on Left cammera, "
        else:
            errorText = "There was an error on Right and Left cammeras, "
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
        
    error = [True,True]
    try:
        camRight = vCamera.videoCamera(defaultR, inGray= True)
        error[0] = False
    except:  
        error[0] = True
    try:
        camLeft = vCamera.videoCamera(defaultL, inGray = True)
        error[1] = False
    except:
        error[1] = True
        
    if not error[0] and not error[1]:
        global mainWindowObj
        appVOG()
        
    elif error[0] and not error[1]:
        cameraError(0,defaultR, defaultL)
        
    elif not error[0] and error[1]:
        cameraError(1, defaultR, defaultL)
        
    else:
        cameraError(2, defaultR, defaultL)



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
        candidateR = rSelection.get()
        candidateL = lSelection.get()
        if candidateR == candidateL:
            labelValidation.config(text= "Right and Left cams could not be the same !")    
        else:
            global camRight, camLeft
            try:
                camRight = vCamera.videoCamera(candidateR, inGray= True)
                camLeft = vCamera.videoCamera(candidateL, inGray= True)
            except:
                messagebox.showwarning("Config file fatal error: It was not possible to set cammeras. Exit to system")
                selectionWindow.destroy()
            if messagebox.askyesno("ErrorConfiguration success","Do you want to save the new configuration?"):
                try:
                        configNew = configparser.ConfigParser()
                        configNew.add_section("CAMERA")
                        configNew.set("CAMERA","right_camera",str(candidateR))
                        configNew.set("CAMERA","left_camera",str(candidateL))
                        configNew.set("CAMERA","help! ","You must set cammera device allways as a number, the number 0 is the first value")
                        with open("CameraConfig.ini", mode = "w") as writingFile:
                            configNew.write(writingFile)
                            writingFile.close()
                        
                except:
                        messagebox.showwarning("It was not possible to save the new configuration!")
            selectionWindow.after(100, selectionWindow.destroy())
            appVOG()
            
            
            
    selectionWindow= tkinter.Tk()
    selectionWindow.title("Cameras manual configuration")
    selectionWindow.geometry("+20+20")
    selectionWindow.focus_set()
    labelInfo = tkinter.Label(selectionWindow, text= "Please, select cammeras", pady=10)
    labelInfo.grid(column= 0, row= 0,columnspan= 2)
    labelTitleR = tkinter.Label(selectionWindow, text= "Rigt Cammera")
    labelTitleR.grid(column= 0, row= 1)
    labelTitleL = tkinter.Label(selectionWindow, text= "Left Cammera")
    labelTitleL.grid(column= 1, row= 1)
    labelValidation = tkinter.Label(selectionWindow, text= "Click Validate to check configuration...", width= 50, pady= 20)
    labelValidation.grid(column= 0, row= 3, columnspan= 2)
    buttonExit = tkinter.Button(selectionWindow, text="Dismiss", command= selectionWindow.destroy)
    buttonExit.grid(column= 1, row= 4)
    buttonValidate = tkinter.Button(selectionWindow, text="Validate", command= cameraValidation)
    buttonValidate.grid(column= 0, row= 4)
    #Radiobuttons for cammera
    frameRightCam = tkinter.Frame(selectionWindow)
    frameLeftCam = tkinter.Frame(selectionWindow)
    frameRightCam.grid(column= 0,row=2)
    frameLeftCam.grid(column= 1,row=2)
    rSelection = tkinter.IntVar()
    lSelection = tkinter.IntVar()
    for camNum in availCameras:
        tkinter.Radiobutton(frameRightCam,text = str("Cammera: "+ str(camNum)), value = camNum, variable = rSelection).pack()
        tkinter.Radiobutton(frameLeftCam,text = str("Cammera: " + str(camNum)), value = camNum, variable = lSelection).pack()
            
    if len(availCameras) < 2:
        if len(availCameras) == 1:
            messagebox.showwarning("Warning","One camera is not enought!")
        else:
            messagebox.showwarning("Warning","No cameras where found!")
    else:
        pass #nothing to do now... but who knows?
            
    selectionWindow.mainloop()        




class appVOG:
    global camRight, camLeft
    
    def __init__(self):
      ########## WIDOW DRAW ##########
      self.ventana = tkinter.Tk()
      self.ventana.title(MYNAME)
      self.ventana.geometry("+0+0")
      self.ventana.resizable(False, False)
            
      #UPP FRAME FOR CAMERAS
      self.frameUp = tkinter.Frame(self.ventana)
      self.frameUp.config(width= 1300, height= 600)
      self.frameUp.grid(column=0, row=0)
      self.titCamL= tkinter.Label(self.frameUp, text="LEFT")
      self.titCamL.grid(column=1, row=0)
      self.canvasL= tkinter.Canvas(self.frameUp,width=640,height=480)
      self.canvasL.grid(column=1, row=1)
      self.titCamR= tkinter.Label(self.frameUp, text="RIGHT")
      self.titCamR.grid(column=0, row=0)
      self.canvasR= tkinter.Canvas(self.frameUp,width=640,height=480)
      self.canvasR.grid(column=0, row=1)
      #DOWN FRAME FOR CONTROLS AND INFO
      self.frameDown = tkinter.Frame(self.ventana)
      self.frameDown.config(width= 1300, height= 400)
      self.frameDown.grid(column=0, row=1)
      
      self.frameFPS = tkinter.Frame(self.frameDown)
      self.frameFPS.config(width= 600, height= 35)
      self.frameFPS.grid(column=0, row=0)
      self.titFPS= tkinter.Label(self.frameFPS, text="APP_FPS: XXXXXX", fg= "red", anchor="w", width = 78)
      self.titFPS.grid(column=0, row= 0)
            
      self.frameDownR = tkinter.Frame(self.frameDown)
      self.frameDownR.config(width= 650, height= 200,)
      self.frameDownR.grid(column= 0, row= 1)
      self.frameDownL = tkinter.Frame(self.frameDown)
      self.frameDownL.config(width= 650, height= 200)
      self.frameDownL.grid(column= 1, row= 1)
            
      self.scaleCameraRgBright= tkinter.Scale(self.frameDownR, from_= 0.0, to= 1.0,resolution=0.01, orient="horizontal", label = "Right Camera Brightness", length = 325, command=self.setRgBr)        
      self.scaleCameraRgBright.grid(column=0,row=0)
      self.scaleCameraRgContrast= tkinter.Scale(self.frameDownR, from_= 0.0, to= 1.0,resolution=0.01, orient="horizontal", label = "Right Camera Contrast", length = 325, command=self.setRgCn)        
      self.scaleCameraRgContrast.grid(column=1,row=0)      
      self.scaleCameraLfBright= tkinter.Scale(self.frameDownL, from_= 0.0, to= 1.0,resolution=0.01, orient="horizontal", label = "Right Camera Brightness", length = 325, command=self.setLfBr)      
      self.scaleCameraLfBright.grid(column=0,row=0)
      self.scaleCameraLfContrast= tkinter.Scale(self.frameDownL, from_= 0.0, to= 1.0,resolution=0.01, orient="horizontal", label = "Right Camera Contrast", length = 325, command=self.setLfCn)
      self.scaleCameraLfContrast.grid(column=1,row=0)
            
      self.buttonConfigure = tkinter.Button(self.ventana, text="Configure Cameras", command= self.loadCameraSelector)
      self.buttonConfigure.grid(column=0, row=2, columnspan=2)
      ########## WIDOW DRAW END ##########
                    
      self.scaleCameraRgBright.set(camRight.brightness)
      self.scaleCameraRgContrast.set(camRight.brightness)
      self.scaleCameraLfBright.set(camLeft.brightness)
      self.scaleCameraLfContrast.set(camLeft.brightness)
      self.counter = 1
      self.pstamp = time.localtime()[5]
      self.delay = 1  # This is a refresh timedelay
      
      self.ventana.after(self.delay, self.update)
      self.ventana.mainloop()    
    def loadCameraSelector(self):
        global camRight, camLeft
        try:
            del camRight
        except:
            pass
        try:
            del camLeft
        except:
            pass
        self.ventana.destroy()
        cameraSelector(False)
        
    def setRgBr(self,value):
        global camRight, camLeft
        camRight.vid.set(cv2.CAP_PROP_BRIGHTNESS,float(value))
    
    def setRgCn(self,value):
        global camRight, camLeft
        camRight.vid.set(cv2.CAP_PROP_CONTRAST,float(value))
        
    def setLfBr(self,value):
        global camRight, camLeft
        camLeft.vid.set(cv2.CAP_PROP_BRIGHTNESS,float(value))
    
    def setLfCn(self,value):
        global camRight, camLeft
        camLeft.vid.set(cv2.CAP_PROP_CONTRAST,float(value))
        
    def update(self):
        global camRight, camLeft
        #getFrame multithread or one thread
        #retRgt,frameRgt = self.camRight.get_frame()
        #retLft,frameLft = self.camLeft.get_frame()
        results = pool.map(vCamera.videoCamera.get_frame, [camRight, camLeft])
        retRgt,frameRgt = results[0]
        retLft,frameLft = results[1]
        if retRgt:
            # If it is needed to resize frame
            #frameRgt = cv2.resize(frameRgt,(480,480))
            self.imageRgt = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frameRgt))
            self.canvasR.create_image(0, 0, image = self.imageRgt, anchor = tkinter.NW)
            
        if retLft:
            # If it is needed to resize frame
            #frameLft = cv2.resize(frameLft,(480,480))
            self.imageLft = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frameLft))
            self.canvasL.create_image(0, 0, image = self.imageLft, anchor = tkinter.NW)
        
        if self.pstamp == time.localtime()[5]:
            self.counter += 1
        else:
            self.titFPS.config(text="APP_FPS: " + str(self.counter))
            actualFPS = self.counter
            self.counter = 1
            self.pstamp = time.localtime()[5]
            if actualFPS < limitFPS:
                self.titFPS.config(fg = "red")
            else:
                self.titFPS.config(fg = "black")
        
        self.ventana.after(self.delay, self.update)


    def __del__(self):
        global camRight, camLeft
        try:
            del camRight
        except:
            pass
        try:
            del camLeft
        except:
            pass
        
        print("Good Bye !!!")
        
#Start the app      
initialCheck()
    