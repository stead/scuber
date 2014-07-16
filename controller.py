import cv2
import itertools
import numpy
import time
import zbar

from PIL import Image

BW_THRESHOLD = 110
FAILED_READS_THRESHOLD = 30

def find_subarray(mylist):
  # Group the list and look for the longest run of zeros.
  longest_array_of_zeros = max(sum(1 for _ in l if n == 0) for n, l in itertools.groupby(mylist))
  if longest_array_of_zeros > 0:
    line_pattern = numpy.array([numpy.uint8(0)] * longest_array_of_zeros).tostring()
    return (mylist.tostring().index(line_pattern), longest_array_of_zeros)
  else:
    return None

def get_next_direction(current_frame, scanner):
  cv2.imwrite('/tmp/tempFrame.png', current_frame)
  pil_image = Image.open('/tmp/tempFrame.png').convert('L')

  width, height = pil_image.size
  raw = pil_image.tostring()

  # wrap image data
  image = zbar.Image(width, height, 'Y800', raw)

  # scan the image for barcodes
  scanResult = scanner.scan(image)

  if scanResult:
    # TODO: Still have to configure specific QR codes and check that we only stop
    # when we see the correct one
    return 'STOP'

  # if QR code found, and QR code text is the desired destination, return stop
  return 'STRAIGHT' # Can be one of STRAIGHT, STOP, LEFT, RIGHT. Right now only STRAIGHT or STOP.

def get_line_offset(im):
  ### Crop the picture
  height = len(im)
  width = len(im[0])
  im = im[height/4:-height/4, width/4:-width/4]

  ### thresholding. susceptible to glare, solve with masking tape?
  thresh = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
  success, thresh = cv2.threshold(thresh, BW_THRESHOLD, 255, cv2.THRESH_BINARY)
  if not success:
    print "Could not threshold frame, skipping."
    return None

  ### edge detection. constants here are magic
  canny = cv2.Canny(thresh, 180, 220, apertureSize = 3)

  ### contour detection
  contours, _ = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
  sorted_contours = sorted(contours, key=lambda x:cv2.arcLength(x,False), reverse=True)
  # cv2.drawContours(im,sorted_contours[0:1],-1,(0,255,0),3) # draw longest contour

  ### Find x coordinates of endpoints
  # get points for the single, longest contour
  cnt = sorted_contours[0]
  mask = numpy.zeros(im.shape,numpy.uint8)
  cv2.drawContours(mask,[cnt],0,255,-1)
  pixelpoints = numpy.transpose(numpy.nonzero(mask)) 
  xTop = pixelpoints[0][1] # IMPORTANT: pixelpoints is returned in row, column format
  xBottom = pixelpoints[-1][1]
  return xTop - xBottom #TODO: Add center offset

STOP = (0, 0) # Speed first, then heading
def compute_speed_and_heading(current_frame, scanner):
  next_direction = get_next_direction(current_frame, scanner)
  if next_direction == 'STOP':
    return STOP

  line_offset = get_line_offset(current_frame)
  if line_offset is None:
    return None
  return (2, line_offset)

def communicate_to_actuation(speed_heading):
  print speed_heading

if __name__ == '__main__':
  camera = cv2.VideoCapture(0)
  scanner = zbar.ImageScanner()
  scanner.parse_config('enable')
  try:
    num_failed_reads = 0
    while True:
      if num_failed_reads == FAILED_READS_THRESHOLD:
        print "Missed %d frames, stopping scooter" % (FAILED_READS_THRESHOLD,)
        communicate_to_actuation(STOP)
        break

      success, current_frame = camera.read()
      cv2.imshow("Wutup", cv2.resize(current_frame, (0,0), fx=0.5, fy=0.5))
      cv2.waitKey(10)
      if success:
        speed_heading = compute_speed_and_heading(current_frame, scanner)
        if speed_heading is not None:
          num_failed_reads = 0
          communicate_to_actuation(speed_heading)
          if speed_heading[0] == 0:
            break
        else:
          print "Couldn't compute speed and heading, passing"
          num_failed_reads += 1
      else:
        print "Couldn't read frame successfully, passing"
        num_failed_reads += 1
  finally:
    camera.release()
