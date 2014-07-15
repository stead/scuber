import numpy as np
import cv2
import time

def continuous_capture(size_ratio = 1):
	cam = cv2.VideoCapture(0)
	while True:
		_, img = cam.read()
		cv2.imshow('lines',cv2.resize(img, (0,0), fx=size_ratio, fy=size_ratio))
		k = cv2.waitKey(10)
		if k == 27:						
			cv2.destroyAllWindows()
			cam.release()
			break

def take_picture(filename):
	cam = cv2.VideoCapture(0)
	_, img = cam.read()
	cv2.imwrite(filename + '.',img)
	cam.release()

def read_picture(filename):
	img = cv2.imread(filename)
	cv2.imwrite('out_' + filename, img)


def thresholding(size_ratio = 1):
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

def edge_detection(size_ratio=1):
	cam = cv2.VideoCapture(0)
	while True:
		_, img = cam.read()
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to grayscale
		img = cv2.Canny(img,180,220,apertureSize = 3) # edge detect
		cv2.imshow('lines',cv2.resize(img, (0,0), fx=0.5, fy=0.5))
		k = cv2.waitKey(10)
		if k == 27:						
			cv2.destroyAllWindows()
			cam.release()
			break

		# Logic to circle through thresholds to find the best combination!
		# for i in range(0,250, 25):
		# 	for j in range(0,250, 25):
		# 		print str(i) + ',' + str(j)
		# 		edges = cv2.Canny(gray,i,j,apertureSize = 3) # EDGE DETECTION
		# 		cv2.imshow('lines',cv2.resize(edges, (0,0), fx=size_ratio, fy=size_ratio))
		# 		k = cv2.waitKey(1000)
		# 		if k == 27:						
		# 			cv2.destroyAllWindows()
		# 			cam.release()
		# 			return

# HoughLines stuff (currently not working)
# lines = cv2.HoughLinesP(edges,1,np.pi/180,150)
# # for x1,y1,x2,y2 in lines[0]:
# #     cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
# # cv2.imshow('houghlines',img)

edge_detection(0.3)
thresholding(0.3)