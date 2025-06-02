import cv2 # Βιβλιοθήκη για χρήση κάμερας
import HandTrackingModule as htm # Scriptaki για την ανιχνευση χεριών

# για ελεγχο ήχου
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER # για χρήση δεδομένων τύπου C
from comtypes import CLSCTX_ALL
# Για τον υπολογισμό FPS θα διαιρούμε την διαφορά χρόνου ανάμεσα σε κάθε 
# frame από το 1  (1/(currentTime-previousTime))
import time
import math
import numpy as np

wCam, hCam = 640, 480 # Μέγεθος παραθύρου κάμερας

cap = cv2.VideoCapture(0) # Ορισμός κάμερας

# Ορισμός του μεγέθους
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0 # previousTime

detector = htm.handDetector(detectionCon=0.7) # δημιουργία αντικειμένου handDetector

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None) # αλλαγή έντασης
volume = cast(interface, POINTER(IAudioEndpointVolume)) # pointer volume για αλλαγή έντασης

# μεταβητές για την ένταση
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0 # η ενταση
volBar = 400 # η μπάρα που θα ανεβωκατεβαίνει στην οθόνη
volPer = 0 # Το ποσοστό που θα εμφανίζεται στην οθόνη

while True:
    
    # cap.read() επιστρέφει εάν ήταν επυτχιά η καταγραφή του frame (success = True/False)
    # και την εικόνα (img)
    success, img = cap.read() 
    
    img = detector.findHands(img) #Βρες τα χερια στην εικόνα
    lmList = detector.findPosition(img, draw=False) #Κράτα την τοποθεσία τους

    #Εάν η λίστα δεν είναι κενή κρατάμε τις συντεταγμένες των δάχτυλων που θέλουμε
    # καθώς και τα κέντρα των 2 σημείων
    if lmList != ([],[]):
        x1, y1 = lmList[0][4][1], lmList[0][4][2] # το 4 είναι ο αντίχειρας
        x2, y2 = lmList[0][20][1], lmList[0][20][2] # το 20 είναι το μικρό δάχτυλο
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1,y1), (x2,y2), (255, 0, 255), 3)
        cv2.circle(img, (cx,cy), 15, (255,0,255), cv2.FILLED)
        
        length = math.hypot(x2-x1, y2-y1)
        


        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])
        

        volume.SetMasterVolumeLevel(vol, None)
        print("length: " + str(length)+", vol: " + str(vol))
        

        if length < 50:
            cv2.circle(img, (cx,cy), 15, (0, 255, 0), cv2.FILLED)
        
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    

    cv2.putText(img, "FPS: "+str(int(fps)), (40,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    

    cv2.imshow("Gesture Volume Control", img)

    k = cv2.waitKey(1)
    if k%256 == 27:

        print("Escape hit, closing...")
        break
    

cap.release()
cv2.destroyAllWindows()