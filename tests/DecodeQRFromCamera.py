from sys import argv
import zbar
from PIL import Image
import numpy
from cv2 import *
import time

# init camera
cam = VideoCapture(0)   # 0 -> index of camera

# create a reader
scanner = zbar.ImageScanner()

# configure the reader
scanner.parse_config('enable')

namedWindow("cam-test",CV_WINDOW_AUTOSIZE)

while True:
	isImageRead, img = cam.read()
	if isImageRead:    # frame captured without any errors
		# obtain image data
		# Show captured image in popup window
		imshow("cam-test",img)
		imwrite('tempFrame.png', img) #save image
		
		pil = Image.open('tempFrame.png').convert('L')
		width, height = pil.size
		raw = pil.tostring()

		# wrap image data
		image = zbar.Image(width, height, 'Y800', raw)

		# scan the image for barcodes
		scanResult = scanner.scan(image)

		if scanResult:
			# extract results
			for symbol in image:
				# do something useful with results
				print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
		else:
			print "No QR Code detected"

		# clean up
		del(image)
	waitKey(1000)
	
cam.release()
destroyAllWindows()


