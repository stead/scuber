import cv2
import numpy
import os
import sys

def show_img(img):
  cv2.imshow("Abs", img)
  k = cv2.waitKey(0)
  if k == 27:
    cv2.destroyAllWindows()
    sys.exit(0)

def basic_detect(file):
  img = cv2.imread(file)

  # Crop the fkin picture
  height = len(img)
  width = len(img[0])
  img = img[height/4:-height/4, width/4:-width/4]

  # Threshold the picture
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to grayscale

  # Susceptible to glare, solve w/ masking tape?
  success, img = cv2.threshold(img, 90, 255, cv2.THRESH_BINARY)
  if not success:
    print "You so sensitive: %s" % (file,)
    return

  show_img(img)

if __name__ == '__main__':
  path_to_images = "sample_images/lowmount/"
  files = os.listdir(path_to_images)
  for file in files:
    basic_detect(path_to_images + file)
