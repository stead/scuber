import cv2
import numpy
import sys
import time
import zbar

from PIL import Image


def open_file(c):
  _, thresh = c.read()
  thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
  scanner = zbar.ImageScanner()
  scanner.parse_config('enable')
  pil_image = Image.fromarray(thresh, 'L')

  width, height = pil_image.size
  raw = pil_image.tostring()

  # wrap image data
  image = zbar.Image(width, height, 'Y800', raw)

  # scan the image for barcodes
  scanResult = scanner.scan(image)

  if scanResult:
    for symbol in image:
      # do something useful with results
      print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data      
  else:
    print "Scanresult was none"

if __name__ == '__main__':
  c = cv2.VideoCapture(0)
  while True:
    open_file(c)
