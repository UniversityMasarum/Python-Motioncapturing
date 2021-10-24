
import serial 
import cv2
import mediapipe as mp
import time
import threading
import extcolors
import pyscreenshot as ImageGrab



class triggerthread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global triggerstr
        under10percent = False
        trigger = False
        index = 0
        percentagebefore = 1230 # Pixel/Menge der Punkte in der Leiste
        #Gameinput TIMECONSUMING AF DUDE
        while True:
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
            index = -1
            trigger = False
            #for x in range(0, 50):
            im = ImageGrab.grab(bbox=(755, 1047, 1165, 1050)) #gets healthbar
            #im.show()
            colors, pixel_count = extcolors.extract_from_image(im)
            
            rgbcolor = [x[0] for x in colors]
            percentage = [x[1] for x in colors]
            
            # gets though list of rgbcolor 
            for color in rgbcolor:
                index = index + 1
                if "232" in color:
                    under10percent = True
                else:
                    under10percent = False
                #print(color, " ", percentage, " ", percentagebefore, " ", percentage[index])
                #if the color is contained & trigger is not true enter if condition
                if (color == (242, 242, 242) or color == (232, 91, 79) or color == (252, 230, 171)) or under10percent == True and trigger == False:
                    #if the percentage of the last loop is higher then this time enter loop
                    if(percentagebefore > percentage[index] + 10):
                        print("true ", percentagebefore, " ", percentage[index])
                        trigger = True
                        percentagebefore = percentage[index]
                        #string for Arduino
                        triggerstr = "ON"
                    else:
                        percentagebefore = percentage[index]
                        print("false ", percentagebefore, " ", percentage[index])
                        
            #triggers if u got hit
            if(triggerstr=="ON"):
                time.sleep(0.35)
            triggerstr = "OFF"
            #print(triggerstr)    
          
          

start = time.time()
x = 0
y = 0
triggerstr = "OFF"

msg = "X{}Y{}T{}\n"
incomingdegreeX = 90
incomingdegreeY = 95
firsttime= 1
inByte = ""

leftright = 1 #1 is for right 0 is for left
resetvalueturn = 0

middle = 5

ser= serial.Serial('COM5', 115200)
try:
    ser.isOpen()
except:
    print("Error")

# checks arduino 
print(ser.readline().decode('utf-8'))

# Call my trigger Function
triggerhealth = triggerthread()
triggerhealth.start()

#mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# For static images:
cap = cv2.VideoCapture(0)
cap.set(3,1280);
cap.set(4,720);

turretautomatation = True

if not cap.isOpened():
    raise IOError("Change Webcam ID")
    raise IOError("Cannot open Webcam")

end = time.time()
print(f"The compiling time is {end - start}")
## Setup mediapipe instance 0.7 is the confidence the program has in the detection
with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.6) as pose:
    while cap.isOpened():
        ret, frame = cap.read() 
        frameWidth = frame.shape[1]
        frameHeight = frame.shape[0]
            
            #if keyboard.on_press('alt'):
             #   print("hello")
                #manualcontrol(incomingdegreeX, incomingdegreeY)
            
            
            # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
          
            # Make detection
        results = pose.process(image)
        
            # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
             # Extract landmarks
        try: # if somebody is in sight
            landmarks = results.pose_landmarks.landmark
            x = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x + landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x) / 2
            y = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y + landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) / 2
            print("results")
            if x < 0.30:
                incomingdegreeX = incomingdegreeX + 5
            elif x < 0.38:
                incomingdegreeX = incomingdegreeX + 3
            elif x < 0.47:
                incomingdegreeX = incomingdegreeX + 1
                
            elif x > 0.7:
                incomingdegreeX = incomingdegreeX - 5
            elif x > 0.62:
                incomingdegreeX = incomingdegreeX - 3
            elif x > 0.53:
                incomingdegreeX = incomingdegreeX - 1
                                
                #print(x)
                            
            if incomingdegreeX <= 0:
                incomingdegreeX = 0
                print(incomingdegreeX)
                
            if incomingdegreeX > 180:
                incomingdegreeX = 180
                print(incomingdegreeX)
            
            if y < 0.40:
                incomingdegreeY = incomingdegreeY + 2
                
            elif y > 0.60:
                incomingdegreeY = incomingdegreeY - 2
                            
                
            resetvalueturn = 0
                #print("target in sight")
                #mystring = f"the value X: {x} / the value Y: {y}"
                #print(mystring)
                    
        except:
            if(incomingdegreeX == 180):
                leftright = 0
            if(incomingdegreeX == 0):
                leftright = 1
                            
            if(resetvalueturn != 15):
                resetvalueturn = resetvalueturn + 1
                
            if(resetvalueturn == 15):
                if(leftright == 1):
                    incomingdegreeX = incomingdegreeX + 1
                else:
                    incomingdegreeX = incomingdegreeX - 1
                                
            if(incomingdegreeY >= 85):
                incomingdegreeY = incomingdegreeY - 1
            else:
                incomingdegreeY = incomingdegreeY + 1
                #print("no results")
                #mystring = f"the value X: {x} the value Y: {y}"
                #print(mystring)
            pass
            
            # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))
        
            #Serial Communication
        if(ser.isOpen()):
            if firsttime == 1:
                ser.write(msg.format(incomingdegreeX, incomingdegreeY, 'OFF').encode())
                firsttime = 0
            else:
            #  transfers the X coordinate, Y coordinate and the trigger
                ser.write(msg.format(incomingdegreeX, incomingdegreeY, triggerstr).encode())
            
        freq = cv2.getTickFrequency() / 1000
        end = time.time()
        cv2.putText(frame, '%.2fms' % (end - start / freq), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
        cv2.imshow('Pose estimation feet', image)
            
        print(f"Runtime of the program is {end - start}")
        start = time.time()
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        results.pose_landmarks
    
cap.release()
cv2.destroyAllWindows()
ser.close()