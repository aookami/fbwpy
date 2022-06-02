
from array import array
from operator import truediv
from random import randint
import threading
import time
import pyvjoy
import pygame
import socket
import winsound
from datetime import datetime


debug = False

gameData = ''
aayConst = 1
avyConst = 1
onOffState = False
joyValMem = 0.05


def thread_socket_listener():
    print("Socket listener thread starting")
    global gameData 
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(('localhost' , 8075))

    print("started listening on socket")
    while True:
        print ('dcs has connected to the socket ')
        while True:
            msg = udp.recvfrom(1024)
            print(str(msg))
            gameData = str(msg)
            if(msg==''):
                break
        print ('Ending connection', str(udp))
        udp.close()
        print("Socket listener thread finishing")

def thread_fbw_logic():
    print("Starting fbw logic thread")
    global gameData
    vJoy = pyvjoy.VJoyDevice(1)
    global joyValMem
    global onOffState
    pygame.display.init()
    pygame.joystick.init()
    twcsNumber = 0
    for x in range(0, pygame.joystick.get_count()):
        if pygame.joystick.Joystick(x).get_name().__eq__('Thrustmaster FFB Wheel'):
            twcsNumber = x
    print("wheel is " + str(twcsNumber))
    joyy = pygame.joystick.Joystick(twcsNumber)
    joyy.init()
    joy2number = 0
    for x in range(0, pygame.joystick.get_count()):
        if pygame.joystick.Joystick(x).get_name().__eq__('Throttle - HOTAS Warthog'):
            joy2number = x
    print("throttle is " + str(joy2number))
    joyy2 = pygame.joystick.Joystick(joy2number)
    joyy2.init()
    wheelAxisNumber = 1
    throttleButtonNumber = 31
    print ("Init Wheel name: ", joyy.get_name())
    print ("Init Throttle name: ", joyy2.get_name())
    while True:
        time.sleep(0.02)
        if gameData != "":
            if(joyy2.get_button(throttleButtonNumber)):
                onOffState = not onOffState
                time.sleep(0.3)
            gameInfoDict = dataStrToGameInfoDict(gameData)
            pygame.event.pump()
            if(onOffState):
                val = normalizeToHex(calculateJoyValToKillAvy(gameInfoDict, joyy.get_axis(wheelAxisNumber)))
            else:
                val = normalizeToHex(joyy.get_axis(wheelAxisNumber))
            if 0 < int(val) < 32750:
                vJoy.set_axis(pyvjoy.HID_USAGE_X, val)
            



#normalize -1 1 float value to 0x0000 0x8000
def normalizeToHex(floatValue):
    #print('fvalb = ' + str(floatValue)
    floatValue = floatValue + 1 # this will set the value between 0 and 2
    floatValue = (floatValue) * (float(32750)/float(2))
    #print('fval = ' + str(floatValue))
    if(floatValue > 32750):
        return int(32750)
    if(floatValue < 5):
        return int(5)

    return int(floatValue)


def dataStrToGameInfoDict(dataStr):
    gameInfoDict = {}
    dataStr = dataStr.replace("b'", "")
    dataStr = dataStr.replace("'", "")
    dataStr = dataStr.replace(" ", "")  
    gameInfo = dataStr.split(",")
    for info in gameInfo:
        if(info.split("=").__len__() == 2):
            name, val = info.split("=")
            gameInfoDict[name] = val
    return gameInfoDict

def calculateJoyValToKillAvy(gameInfoDict, joyVal):
    global avyConst
    global aayConst
    global joyValMem
    global onOffState

    if('avy' in gameInfoDict):
        avyCurrentVal = gameInfoDict['avy']
    else: 
        avyCurrentVal = 0
    if('aay' in gameInfoDict):
        aayCurrentVal = gameInfoDict['aay']
    else: aayCurrentVal = 0
    #joyVal =  float(avyConst)*float(avyCurrentVal) + float(aayConst)*float(aayCurrentVal)
    joyValKill = joyValMem
    
    if float(avyConst)*float(avyCurrentVal) + float(aayConst)*float(aayCurrentVal) > 0:
        if  -0.05 < joyVal < 0.05:
            joyValMem = joyValMem + 0.05
        joyValKill = joyValKill + 0.2
    elif float(avyConst)*float(avyCurrentVal) + float(aayConst)*float(aayCurrentVal) < 0:
        if  -0.05 < joyVal < 0.05:
            joyValMem = joyValMem - 0.05
        joyValKill = joyValKill - 0.2

    if(joyValMem > 1):
        joyValMem = 0.95
    if(joyValMem < -1):
        joyValMem = -0.95
    
    if(joyValKill > 1):
        joyValKill = 0.95
    if(joyValKill < -1):
        joyValKill = -0.95
    
    global debug
    if(debug):
        f = open("debug data.txt", "w")
        f.write("avy:" + str(avyCurrentVal) + "aay:" + str(aayCurrentVal) +"avyc:" + str(avyConst) + "aayc:" + str(aayConst) + " current joyVal: " + str(joyValMem)+  " jpos:" + str(joyVal))
        f.close()
    return joyValKill+joyVal*0.7



def main():
    print("starting...")
    global aayConst
    global avyConst

    datetime.now(tz=None)
    
    x = threading.Thread(target=thread_socket_listener, args=(), daemon=True)
    x.start()
    y = threading.Thread(target=thread_fbw_logic, args=(), daemon=True)
    y.start()
   
    while True:
        time.sleep(2)
        vals = input("current vals: avy:" + str(avyConst) + " aay:" + str(aayConst) + "e to exit /  new ones:")
        print(vals)
        if vals == "e": 
            print("end")
            x.join()
            y.join()
            break
        if(vals.split(",").__len__() > 0):
            avyConst = vals.split(",")[0]
            aayConst = vals.split(",")[1]
        
        
  

main()






    
