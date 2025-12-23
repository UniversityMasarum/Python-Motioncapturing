import pytesseract as tess
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#from PIL import Image
import cv2 as cv 
#import matplotlib.pyplot as plt
import serial
#from time import sleep
import extcolors
import pyscreenshot as ImageGrab

import time
import threading


class triggerthread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        trigger = False
        index = 0
        percentagebefore = 7380 # Pixel/Menge der Punkte in der Leiste
        #Gameinput TIMECONSUMING AF DUDE
        while True:
            start = time.time()
            index = -1
            trigger = False
            #for x in range(0, 50):
            im = ImageGrab.grab(bbox=(755, 1032, 1165, 1050)) #gets healthbar
            #im.show()
            colors, pixel_count = extcolors.extract_from_image(im)
            
            rgbcolor = [x[0] for x in colors]
            percentage = [x[1] for x in colors]
            
            # gets though list of rgbcolor 
            for color in rgbcolor:
                index = index + 1
                #print(color, " ", percentage, " ", percentagebefore, " ", percentage[index])
                #if the color is contained & trigger is not true enter if condition
                if (color == (242, 242, 242) or color == (232, 91, 79) or color == (252, 230, 171)) and trigger == False:
                    #if the percentage of the last loop is higher then this time enter loop
                    if(percentagebefore > percentage[index] + 10):
                        print("true ", percentagebefore, " ", percentage[index])
                        trigger = True
                        percentagebefore = percentage[index]
                        #string for Arduino
                        triggerstr = "ON"
                    else:
                        #print("false ", percentagebefore, " ", percentage[index])
                        percentagebefore = percentage[index]
                        print("false ", percentagebefore, " ", percentage[index])
            
            triggerstr = "OFF"
                    
                        
            #if(trigger != True):
            #    triggerstr = "OFF"
      
            #else:
            #    triggerstr = "ON"
                
            
            end = time.time()
            print(f"Runtime of the program is {end - start}")


inWidth = 300
inHeight = 300
thr = 0.2

net = cv.dnn.readNetFromTensorflow("graph_opt.pb")
ser= serial.Serial('COM5', 115200)

try:
    ser.isOpen()
except:
    print("Error")
    
BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
                "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
            ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
            ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
            ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
            ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]


# perform for webcam
# Camera takes 78° in width  (90-78)/2 = 6° need to be dropped on the right and left maybe 7°
cap = cv.VideoCapture(0)

cap.set(cv.CAP_PROP_FPS, 15)
cap.set(3,1280);
cap.set(4,720);

x = 0
y = 0
triggerstr = "OFF"

# message for arduino: X = X coordinate, Y = Y coordinate, T = trigger 
msg = "X{}Y{}T{}\n"
incomingdegreeX = 90
incomingdegreeY = 90
lastX = 0
lastY = 0
inByte = ""

# checks arduino 
print(ser.readline().decode('utf-8'))

if not cap.isOpened():
    raise IOError("Change Webcam ID")
    raise IOError("Cannot open Webcam")

# Call my trigger Function
triggerhealth = triggerthread()
triggerhealth.start()
    
while cv.waitKey(1) < 0:
    
    hasFrame,frame=cap.read()
    if not hasFrame:
        cv.waitKey()
        break
        
        
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))

    out = net.forward()
    out = out[:, :19, :, :]  # MobileNet output [1, 57, -1, -1], we only need the first 19 elements
    
    assert(len(BODY_PARTS) == out.shape[1])

    points = []
    
    
    # Getting Points
    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponging body's part.
        heatMap = out[0, i, :, :]

        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]
        
        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > thr else None)
        
        
        # if point is [BODY_PARTS[1]] / Neck
        # spare in 3 parts turnright 0 - 550, middle 550-730, turnleft 730-1280
        if True:
            if i == 1:
                #checks if value of x is the same value as last time, It only works if camera is attatched
                #if lastX != x:
                #    lastX = x 
                if x < 550:
                    print("turnright")
                    incomingdegreeX = incomingdegreeX + 17
                    if incomingdegreeX > 180:
                        incomingdegreeX = 180
    
                    print(incomingdegreeX)
                elif x > 730:
                    print("turnleft")
                    incomingdegreeX = incomingdegreeX - 17
                    if incomingdegreeX <= 0:
                        incomingdegreeX = 0
    
                    print(incomingdegreeX)
                else:
                    print("middle")
                    print(incomingdegreeX)
                    
                #if lastY != y:
                #    lastY = y
                if y < 240:
                    print("down")
                    incomingdegreeY = incomingdegreeY + 3
                    if incomingdegreeY > 160:
                        incomingdegreeY = 160
    
                elif y > 480:
                    print("up")
                    incomingdegreeY = incomingdegreeY + 3
                    if incomingdegreeY > 160:
                        incomingdegreeY = 160
    
                else:
                    print("No Y movement")
    
    
    #if(trigger != True):
    #    triggerstr = "OFF"           
    #else:
    #    triggerstr = "ON"
    #    print(triggerstr)
            
    #Serial Communication
    if(ser.isOpen()):     
        #  transfers the X coordinate, Y coordinate and the trigger
        ser.write(msg.format(incomingdegreeX, incomingdegreeY, triggerstr).encode())

    #appending them together
    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
    
    t, _ = net.getPerfProfile()
    freq = cv.getTickFrequency() / 1000
    cv.putText(frame, '%.2fms' % (t / freq), (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
    
    cv.imshow('Pose estimation ', frame)
    
    