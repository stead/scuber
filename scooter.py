import controller
import cv2
import itertools
import json
import numpy
import time
import urllib
import urllib2
import zbar

from PIL import Image

BW_THRESHOLD = 110
FAILED_READS_THRESHOLD = 15
CENTER_OFFSET = 29
CROP_RATIO = 4 ## TAKES 1/4 ooff each side of image

WEBSERVER_IP_ADDRESS = "54.191.68.125"

def get_next_direction(current_frame, scanner, code):
  """Given a frame from the camera and a destination, figure out which direction to take next"""
  # ### thresholding. susceptible to glare, solve with masking tape?
  thresh = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
  # success, thresh = cv2.threshold(thresh, BW_THRESHOLD, 255, cv2.THRESH_BINARY)
  # if not success:
  #   print "Could not threshold frame, skipping."
  #   # Okay to return 'STRAIGHT' here because the thresholding error will cause the
  #   # speed calculator to bail out and we'll skip the frame.
  #   return 'STRAIGHT'

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
      report_data_to_webserver(symbol.data)
      if symbol.data == code:
        return 'STOP'

  # if QR code found, and QR code text is the desired destination, return stop
  return 'STRAIGHT' # Can be one of STRAIGHT, STOP.

def report_data_to_webserver(data):
  url = 'http://%s:8080/report_code/%s' % (WEBSERVER_IP_ADDRESS, data,)
  values = {'code_data' : data}
  data_ = urllib.urlencode(values)
  req = urllib2.Request(url, data_)
  response = urllib2.urlopen(req)
  print response.read()

def get_line_error(im):
  """Given a frame from the camera, figure out the line error"""  
  ### Crop the picture
  height = len(im)
  width = len(im[0])
  im = im[height/CROP_RATIO:-height/CROP_RATIO, width/CROP_RATIO:-width/CROP_RATIO]

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

  if len(contours) < 1:
    return None

  sorted_contours = sorted(contours, key=lambda x:cv2.arcLength(x,False), reverse=True)
  
  ## JUST FOR TESTING
  # longest contours
  cv2.drawContours(im,sorted_contours[0:2],-1,(0,255,0),3) # draw longest contour  
  cv2.imshow('lines',im)
  k = cv2.waitKey(5)
  if k == 27:           
    cv2.destroyAllWindows()
    return None

  ### Find x coordinates of endpoints
  if len(sorted_contours) == 0:
    print "No contours found, skipping"
    return None

  # get points for the longest contours 
  mask = numpy.zeros(im.shape,numpy.uint8)
  cv2.drawContours(mask,[sorted_contours[0]],0,255,-1)
  pixelpoints = numpy.transpose(numpy.nonzero(mask)) 
  xTop_one = pixelpoints[0][1] # IMPORTANT: pixelpoints is returned in row, column format
  xBottom_one = pixelpoints[-1][1] ## IMPORTANT TODO: assumes points are returned sorted, need to verify

  if len(sorted_contours) > 1: # we have more than one contour
    mask = numpy.zeros(im.shape,numpy.uint8)
    cv2.drawContours(mask,[sorted_contours[1]],0,255,-1)
    pixelpoints = numpy.transpose(numpy.nonzero(mask)) 
    xTop_two = pixelpoints[0][1] # IMPORTANT: pixelpoints is returned in row, column format
    xBottom_two = pixelpoints[-1][1] ## IMPORTANT TODO: assumes points are returned sorted, need to verify

  # average two longest contours if available    
  if len(sorted_contours) == 1:
    xTop = xTop_one
    xBottom = xBottom_one
  else:
    xTop = (xTop_one + xTop_two) / 2
    xBottom = (xBottom_one + xBottom_two) / 2

  ### Calculate offset to return
  ### (XTop - XBottom) + (XTop - CENTER)
  ### CENTER = TRUE_CENTER - CENTER_OFFSET
  MOST_POSITIVE_VAL = 3*len(im[0])/2 + CENTER_OFFSET
  MOST_NEGATIVE_VAL = -3*len(im[0])/2 + CENTER_OFFSET
  adjusted_midpoint = len(im[0])/2 - CENTER_OFFSET

  #unscaled_error = xTop - xBottom + 2*(xTop - adjusted_midpoint)
  unscaled_error = xTop - adjusted_midpoint
  if unscaled_error == 0:
    return 0.0

  if unscaled_error > 0:
    scaled_error = float(unscaled_error)/MOST_POSITIVE_VAL
    if abs(scaled_error) > 1.0:
      print "Warning: scaled_error value greater than 1.0: " + scaled_error
    return min(scaled_error, 1.0)
  else:
    scaled_error = float(unscaled_error)/abs(MOST_NEGATIVE_VAL)
    if abs(scaled_error) > 1.0:
      print "Warning: scaled_error value less than -1.0: " + scaled_error    
    return max(scaled_error, -1.0)

STOP = (0, 0) # Speed first, then line error
def compute_speed_and_line_error(current_frame, scanner, code):
  """Given a frame from the camera, figure out the desired speed and current line error"""  
  next_direction = get_next_direction(current_frame, scanner, code)
  if next_direction == 'STOP':
    return STOP

  line_error = get_line_error(current_frame)
  if line_error is None:
    return None

  return (2, line_error)

def communicate_to_actuation(kontroller, speed_heading):
  kontroller.update_controller(speed_heading)

def open_appropriate_camera():
  # Super basic right now, assumes that there are at most two cameras available
  camera_heights = {} # Map from height of picture to camera #
  for cam_num in [0, 1]:
    height = get_camera_height(cam_num)
    if height is not None:
      camera_heights[height] = cam_num

  cam_num_to_open = camera_heights.get(1080)
  if cam_num_to_open is None:
    if len(camera_heights) == 0:
      return None
    else:
      cam_num_to_open = camera_heights.values()[0]

  camera = cv2.VideoCapture(cam_num_to_open)
  return camera

def get_camera_height(camera_num):
  try:
    camera = cv2.VideoCapture(camera_num)
    success, frame = camera.read()
    if success:
      return len(frame)
    else:
      return None
  finally:
    try:
      camera.release()
    except:
      pass

def get_next_destination_from_webserver():
  return json.loads(urllib2.urlopen("http://%s:8080/get_next_destination" % (WEBSERVER_IP_ADDRESS,)).read()).get("next_destination")

def travel_to_qr_code(kontroller, code):
  camera = open_appropriate_camera()
  if camera is None:
    print "Could not initialize camera, not doing anything"
    return

  try:
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    num_failed_reads = 0

    while True:
      if num_failed_reads == FAILED_READS_THRESHOLD:
        print "Missed %d frames, stopping scooter" % (FAILED_READS_THRESHOLD,)
        communicate_to_actuation(kontroller, STOP)
        break

      success, current_frame = camera.read()
      # cv2.imshow("Scuber", cv2.resize(current_frame, (0,0), fx=0.5, fy=0.5))
      # cv2.waitKey(10)
      if success:
        speed_and_line_error = compute_speed_and_line_error(current_frame, scanner, code)
        if speed_and_line_error is not None:
          num_failed_reads = 0
          communicate_to_actuation(kontroller, speed_and_line_error)
          if speed_and_line_error[0] == 0:
            break
        else:
          print "Couldn't compute speed and line error, passing"
          num_failed_reads += 1
      else:
        print "Couldn't read frame successfully, passing"
        num_failed_reads += 1
  finally:
    camera.release()

class DummyController(object):
  def update_controller(self, dummy):
    pass

if __name__ == '__main__':
  try:
    kontroller = controller.Controller()

    while True:
      next_destination = get_next_destination_from_webserver()
      if next_destination is None:
        time.sleep(1)
        continue
      print "Traveling to %s" % (next_destination,)
      travel_to_qr_code(kontroller, next_destination)
  finally:
    try:
      communicate_to_actuation(kontroller, STOP)
      kontroller.close()
    except:
      pass
