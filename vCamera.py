#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 11:06:08 2020

@author: jorge
"""
import cv2

#VideocameraClass
class videoCamera:
     def __init__(self, video_source=0, inGray=False):
         # Open the video source
         self.isGray = inGray
         self.video_origin= video_source
         self.vid = cv2.VideoCapture(video_source)
         if not self.vid.isOpened():
             del self
             raise ValueError("Unable to open video source", video_source)
         #Preconfigure specs
         self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
         self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
         self.vid.set(cv2.CAP_PROP_FPS,60)
         self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
         self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
         self.fps = self.vid.get(cv2.CAP_PROP_FPS)
         #original Br & Cn was 0.95
         self.brightness = self.vid.get(cv2.CAP_PROP_BRIGHTNESS)
         self.contrast = self.vid.get(cv2.CAP_PROP_CONTRAST)
         print("Cammera source: ",video_source)
         print("---------------")
         print(self.width,"x", self.height, " FPS: ", int(self.fps))
 
     def get_frame(self):
         if self.vid.isOpened():
             ret, frame = self.vid.read()
             if ret:
                 # Return a boolean success flag and the current frame converted to BGR
                 if self.isGray:
                     return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                 else:
                     return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
             else:
                 return (ret, None)
         else:
             return (ret, None)
        
     # Release the video source when the object is destroyed
     def __del__(self):
         if self.vid.isOpened():
             print("Video connection: ",self.video_origin," was deleted")
             self.vid.release()
             
