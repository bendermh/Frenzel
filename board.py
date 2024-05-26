# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 14:04:17 2024

@author: Usuario
"""

from serial import Serial #PIP module is pyserial !!!!!! not serial
import time

# boardControl class

class board:
     def __init__(self, serialPort="COM3"):
         self.error = True
         self.actionDelay = 0.05
         try: 
             self.conn = Serial(serialPort, 115200, timeout = 0.2)
             time.sleep(2)
         except:
             print("Board connection error")
         else:
             print("Board connection Ok")
             self.error = False
             
         
     def setLed(self,stateOn=True):
         if not self.error:
             if stateOn:
                 self.conn.write('N'.encode('utf-8'))
                 time.sleep(self.actionDelay)
             else:
                 self.conn.write('F'.encode('utf-8'))
                 time.sleep(self.actionDelay)
     
     def setIR(self,stateOn=True):
         if not self.error:
             if stateOn:
                 self.conn.write('E'.encode('utf-8'))
                 time.sleep(self.actionDelay)
             else:
                 self.conn.write('A'.encode('utf-8'))
                 time.sleep(self.actionDelay)
                 
     def status(self):
         if not self.error:
             self.conn.write('T'.encode('utf-8'))
             answer = self.conn.read(1).decode('utf-8')
             time.sleep(self.actionDelay)
             if answer == "1":
                 return(True)
             else:
                 return(False)
             
     def readIMU(self):
        if not self.error:
            self.conn.write('R'.encode('utf-8'))
            answer = (self.conn.read(55).decode('utf-8')).split(";")
            time.sleep(self.actionDelay)
            values = []
            for e in answer:
                values.append(float(e)) 
            return(values)
     
     def close(self):
         if not self.error:
             self.conn.close()
     
     def __del__(self):
         if self.error:
             print("Board conection not done")
         else:
             self.conn.close()
             print("Board conection END")
