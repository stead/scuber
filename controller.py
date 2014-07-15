import cv2

def get_next_direction():
  return 'STRAIGHT' # Can be one of STRAIGHT, STOP, LEFT, RIGHT

def get_speed_and_heading(current_frame):
  next_direction = get_next_direction()
  if next_direction == 'STOP':
    return (0, 0) # Speed first, then heading
  else: # Go straight
    return (2, 0)

def communicate_to_actuation(speed_heading):
  print speed_heading

def grab_frame():
  camera = cv2.VideoCapture(0)
  try:
    return camera.read()
  finally:
    camera.release()

if __name__ == '__main__':
  while True:
    success, current_frame = grab_frame()
    if success:
      speed_heading = get_speed_and_heading(current_frame)
      communicate_to_actuation(speed_heading)
    else:
      pass
