import numpy as np
import cv2
import time

cam = cv2.VideoCapture(0)
while True:
	_, img = cam.read()
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to grayscale
	_, img = cv2.threshold(img,100,255,cv2.THRESH_BINARY)
	cv2.imshow('lines',cv2.resize(img, (0,0), fx=0.5, fy=0.5))
	k = cv2.waitKey(10)
	if k == 27:						
		cv2.destroyAllWindows()
		cam.release()
		break