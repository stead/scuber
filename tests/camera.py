import numpy as np
import cv2
import os
import time

def continuous_capture():
	i = 0
	cam = cv2.VideoCapture(0)
	while True:
		_, img = cam.read()
		cv2.imwrite(str(i) + '.png',img)
		i += 1
		time.sleep(1)
	cam.release()

def take_picture(filename):
	cam = cv2.VideoCapture(0)
	_, img = cam.read()
	cv2.imwrite(filename + '.',img)
	cam.release()

def read_picture(filename):
	img = cv2.imread(filename)
	cv2.imwrite('out_' + filename, img)

def line_detection(filename, size_ratio):
	im = cv2.imread(filename)
	gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY) # make image graylines

	# walk through threshold values to see whats best
	for i in range(0,250, 25):
		for j in range(0,250, 25):
			print str(i) + ',' + str(j)
			edges = cv2.Canny(gray,i,j,apertureSize = 3) # EDGE DETECTION
			cv2.imshow('lines',cv2.resize(edges, (0,0), fx=size_ratio, fy=size_ratio))
			k = cv2.waitKey(0)
			if k == 27:
				cv2.destroyAllWindows()
				return

	# HoughLines stuff currently not working
    # lines = cv2.HoughLinesP(edges,1,np.pi/180,150)
    # # for x1,y1,x2,y2 in lines[0]:
    # #     cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
    # # cv2.imshow('houghlines',img)

line_detection('sample_images/line.png', 0.8)