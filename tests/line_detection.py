import numpy as np
import cv2
import time

BW_THRESHOLD = 90
def continuous_capture(size_ratio = 1):
	cam = cv2.VideoCapture(0)
	while True:
		_, im = cam.read()

		### Crop the picture
		# height = len(im)
		# width = len(im[0])
		# im = im[height/4:-height/4, width/4:-width/4]

		### thresholding. susceptible to glare, solve with masking tape?
		thresh = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
		success, thresh = cv2.threshold(thresh, BW_THRESHOLD, 255, cv2.THRESH_BINARY)

		### edge detection. constants here are magic
		canny = cv2.Canny(thresh, 180, 220, apertureSize = 3)

		### contour detection
		contours, _ = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
		cv2.drawContours(im,contours,-1,(0,255,0),3) # draw longest contour		
		# sorted_contours = sorted(contours, key=lambda x:cv2.arcLength(x,False), reverse=True)
		# cv2.drawContours(im,sorted_contours[0:1],-1,(0,255,0),3) # draw longest contour
		
		cv2.imshow('lines',cv2.resize(im, (0,0), fx=size_ratio, fy=size_ratio))
		k = cv2.waitKey(5)
		if k == 27:						
			cv2.destroyAllWindows()
			cam.release()
			break

if __name__ == '__main__':
	continuous_capture(0.5)