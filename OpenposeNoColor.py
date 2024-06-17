
import serial 
import cv2
import mediapipe as mp
import time

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