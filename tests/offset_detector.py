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
  # upper_black = numpy.array([115,115,115])  # define range of blue color in HSV  
  # mask = cv2.inRange(imhsv, lower_black, upper_black) # Threshold the HSV image to get only black colors
  # show_img(mask, 1)

  # thresholding
  thresh = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
  _, thresh = cv2.threshold(thresh, 110, 255, cv2.THRESH_BINARY)  

  # edge detection
  canny = cv2.Canny(thresh,180,220,apertureSize = 3)

  # contour detection
  contours, _ = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
  # get contours sorted by length
  sorted_contours = sorted(contours, key=lambda x:cv2.arcLength(x,False), reverse=True)
  cv2.drawContours(im,sorted_contours[0:1],-1,(0,255,0),3) # draw longest contour

  # get points for a single contour
  cnt = sorted_contours[0]
  mask = numpy.zeros(im.shape,numpy.uint8)
  cv2.drawContours(mask,[cnt],0,255,-1)
  pixelpoints = numpy.transpose(numpy.nonzero(mask)) 

  # Find x coordinates of endpoints
  xTop = pixelpoints[0][1] # IMPORTANT: pixelpoints is returned in row, column format
  xBottom = pixelpoints[-1][1]
  print xTop,xBottom

  show_img(im, 1)

if __name__ == '__main__':
  path_to_images = "sample_images/highmount/"
  files = os.listdir(path_to_images)
  for file in files:
    contour_detect(path_to_images + file)
