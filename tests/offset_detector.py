import cv2
import numpy
import os
import sys

def show_img(img, size_ratio = 1):
  cv2.imshow("Abs", cv2.resize(img, (0,0), fx=size_ratio, fy=size_ratio))
  k = cv2.waitKey(0)
  if k == 27:
    cv2.destroyAllWindows()
    sys.exit(0)

BW_THRESHOLD = 90
LINE_THICKNESS_THRESHOLD = 30

def subfinder(mylist, pattern):
  return mylist.tostring().index(pattern.tostring())

def basic_detect(file):
  img = cv2.imread(file)

  # Crop the fkin picture
  height = len(img)
  width = len(img[0])
  img = img[height/4:-height/4, width/4:-width/4]

  # Threshold the picture
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to grayscale

  # Susceptible to glare, solve w/ masking tape?
  success, img = cv2.threshold(img, BW_THRESHOLD, 255, cv2.THRESH_BINARY)
  if not success:
    print "You so sensitive: %s" % (file,)
    return

  line_pattern = numpy.array([numpy.uint8(0)] * LINE_THICKNESS_THRESHOLD)

  try:
    top_row = subfinder(img[0], line_pattern)
    bottom_row = subfinder(img[-1], line_pattern)
    print top_row - bottom_row
  except:
    pass

  show_img(img)

def contour_detect(file):
  im = cv2.imread(file)

  # Crop the picture
  height = len(im)
  width = len(im[0])
  im = im[height/4:-height/4, width/4:-width/4]

  # color filter (look for black)
  # imhsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
  # lower_black = numpy.array([0,0,0])
  # upper_black = numpy.array([110,110,110])  # define range of blue color in HSV  
  # mask = cv2.inRange(imhsv, lower_black, upper_black) # Threshold the HSV image to get only black colors

  # show_img(mask, 1)

  # edge detection
  canny = cv2.Canny(im,180,220,apertureSize = 3)

  # contour detection
  contours, _ = cv2.findContours(canny,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
  sorted_contours = sorted(contours, key=lambda x:len(x), reverse=True)
  cv2.drawContours(im,sorted_contours[0:3],-1,(0,255,0),3)

  cnt = sorted_contours[0]
  cv2.drawContours(im,[cnt],0,(0,255,0),3)

  show_img(im, 1)


  #contours, hierarchy = cv2.findContours(thresh,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)

  # sorted_contours = sorted(contours, key=lambda x:len(x), reverse=True)
  # cnt = sorted_contours[0]
  # cv2.drawContours(im,[cnt],0,(0,255,0),3)

  #cv2.drawContours(im,contours,-1,(0,255,0),3)
  #show_img(im, 0.5)
  # k = cv2.waitKey(0)
  # if k == ord('h'):
  #   print cnt
  # elif k == 27:
  #   cv2.destroyAllWindows()
  #   sys.exit(0)

if __name__ == '__main__':
  path_to_images = "sample_images/highmount/"
  files = os.listdir(path_to_images)
  for file in files:
    contour_detect(path_to_images + file)