from tkinter import *
import autopy
import cv2 
import mediapipe as mp
import time
import pyautogui as p
from mediapipe.python.solutions import hands 
import math
import numpy as np

class handDetector():
    def __init__(self, mode =False, maxHands=2,modelC=1 ,detectionCon=0.5, trackCon=0.5 ):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.modelC= modelC

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode,self.maxHands,self.modelC,self.detectionCon,self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
    def findHands(self,img):
        convt = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(convt)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    #print(id,lm)
                    h,w,c = img.shape
                    cx, cy = int(lm.x*w), int(lm.y*h)
                    #print(id, cx, cy)
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img
        
    def findPosition2(self,img1, handNo=0,draw = True):
        self.lmList = []
        xList = []
        yList = []
        bbox =[]
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
                h,w,c = img1.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id,cx,cy])
                if draw:
                    cv2.circle(img1,(cx,cy),5,(255,0,255),cv2.FILLED)
            xmin, xmax =min(xList), max(xList)
            ymin, ymax =min(yList), max(yList)
            bbox =xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img1, (xmin-20,ymin-20),(xmax +20,ymax+20),(0,255,0),2)
        return self.lmList, bbox
    
    def findPosition(self,img, handNo=0,draw = True):
        self.lmList2 = []
        
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
                h,w,c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
               
                self.lmList2.append([id,cx,cy])
                
        return self.lmList2
    
    
    def finddistance(self,p1,p2,img,draw=True, r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1+x2)//2, (y1+y2)//2
         
        if draw:
            cv2.line(img,(x1,y1),(x2,y2),(255,0,255),t)
            cv2.circle(img,(x1,y1),10,(0,0,255),cv2.FILLED)
            cv2.circle(img,(x2,y2),10,(0,0,255),cv2.FILLED)
            cv2.circle(img,(cx,cy),10,(0,0,255),cv2.FILLED)
        length = math.hypot(x2-x1,y2-y1)
        return length,img, [x1,y1,x2,y2,cx,cy]


def Virtual_media_controller(): 
    pTime = 0 
    cTime = 0
    cap  = cv2.VideoCapture(1)
    detector = handDetector(maxHands=1)

    while (True):
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw = False)
        if len(lmList)!=0:
            if lmList[8][2]<lmList[6][2] and lmList[12][2]>lmList[10][2]:
                p.press("up")
                cv2.putText(img, "Volume Increase", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
            elif lmList[12][2]< lmList[10][2] and lmList[8][2] < lmList[6][2]:
                p.press("down")
                cv2.putText(img, "Volume Decrease", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
            elif lmList[0][1] < lmList[0-1][1] and lmList[20][2]<lmList[18][2]:
                p.press("right")
                cv2.putText(img, "forward", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
            elif lmList[0][1]< lmList[0-1][1]:
                if lmList[0][1]< lmList[0-1][1] and lmList[20][2] > lmList[18][2]:
                    p.press("left")
                    cv2.putText(img, "backward", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
            else:
                for i in range(1):
                    p.press("Space")
                    cv2.putText(img,"Play",(50,50),cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
                    break
                
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20,50), cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)

       
        cv2.imshow("VLC media controller", img)

        if cv2.waitKey(1) == 113:
            break
          
        
def Mouse_controller():
    wCam,hCam = 640,480
    cap = cv2.VideoCapture(0)
    cap.set(3,wCam)
    cap.set(4,hCam)
    pTime = 0 
    cTime = 0
    detector = handDetector(maxHands=1)
    wScr, hScr = autopy.screen.size()
    fpr= 50
    smth = 7
    pLocx, pLocy =0,0
    cLocx, cLocy = 0,0
    while True:
        suc, img1 = cap.read()
        img1 = detector.findHands(img1)
        lmList, bbox = detector.findPosition2(img1)
      

        if len(lmList)!=0:
            x1,y1 = lmList[8][1:]
            
            cv2.rectangle(img1,(fpr,fpr),(wCam-fpr,hCam-fpr),(255,0,255),2)
            if lmList[8][2]< lmList[6][2] and lmList[12][2]>lmList[10][2]:
                
                x3 = np.interp(x1, (fpr,wCam-fpr),(0,1920))
                y3 = np.interp(y1, (fpr,hCam-fpr),(0,1080))
                cLocx=pLocx+(x3-pLocx)/smth
                cLocy=pLocy+(y3-pLocy)/smth

                autopy.mouse.move(wScr-cLocx,cLocy)
                cv2.circle(img1,(x1,y1),10,(0,0,255),cv2.FILLED)
                pLocx, pLocy = cLocx, cLocy
                
            if lmList[8][2]< lmList[6][2] and lmList[12][2]<lmList[10][2]:
                le, img,linfo =detector.finddistance(8,12,img1)
                if le<40:
                    cv2.circle(img1,(linfo[4],linfo[5]),10,(0,255,0),cv2.FILLED)
                    cv2.putText(img, "Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
            
                    autopy.mouse.click()



        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img1, str(int(fps)), (20,50), cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)

        
        cv2.imshow("Virtual Mouse",img1)
        if cv2.waitKey(1) == 113:
            break

def py():
    Virtual_media_controller()

def second():
    Mouse_controller()

       
window = Tk()
window.resizable(0, 0)

window.geometry("1000x500")
window.title("Hand Tracker")
window.configure(background='Black')

Label(window,text="Hand Tracker",font=("Times",20,'bold')).place(x=380, y=25)

l1 = Label(window, text = "Instructions for VLC controller: ",font=('times',15,'bold'),bg="Black",fg = "White").place(x=1,y=80)

l2 = Label(window, text = "Instructions for Mouse: ",font=('times',15,'bold'),bg="Black",fg = "White").place(x=580,y=80)

l3 = Label(window, text = "1. Show the Index finger for volume increse. ",font=('times',12),bg="Black",fg = "White").place(x=1,y=140)
l4 = Label(window, text = "1. Show the Index finger for moving the Cursor. ",font=('times',12),bg="Black",fg = "White").place(x=580,y=140)

l5 = Label(window, text = "2. Show the Index finger and Middle finger for volume decrease.",font=('times',12),bg="Black",fg = "White").place(x=1,y=180)
l6 = Label(window, text = "2.Show the both Index and Midde finger to stop. ",font=('times',12),bg="Black",fg = "White").place(x=580,y=180)

l7 = Label(window, text = "3.Show the thumb in backward direction for Backward the video.",font=('times',12),bg="Black",fg = "White").place(x=1,y=220)
l8 = Label(window, text = "3.For click touch the Index and middle fingertip. ",font=('times',12),bg="Black",fg = "White").place(x=580,y=220)

l9 = Label(window, text = "4. Show the thumb and the last finger for Forward the video.",font=('times',12),bg="Black",fg = "White").place(x=1,y=260)
l10 = Label(window, text = "Click the below button:",font=('times',12),bg="Black",fg = "White").place(x=100,y=340)
l11 = Label(window, text = "Click the below button:",font=('times',12),bg="Black",fg = "White").place(x=680,y=340)
l10 = Label(window, text = "> Q for exit:",font=('times',12),bg="Black",fg = "White").place(x=100,y=360)
l11 = Label(window, text = "> Q for exit:",font=('times',12),bg="Black",fg = "White").place(x=680,y=360)

button = Button(window,text ="Media Player controller", bg= "#0080FF", fg = "black", width = 25, height = 1 ,cursor="Hand1",
font=('times', 12, ' bold '), command = py)
button.place(x= 50, y= 400)

button1 = Button(window,text ="Mouse Control", bg= "#0080FF", fg = "black", width = 20, height = 1 ,cursor="Hand1",
font=('times', 12, ' bold '), command = second)
button1.place(x= 650, y= 400)

window.mainloop()