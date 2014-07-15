import cv2

def get_next_direction():
  return 'STRAIGHT' # Can be one of STRAIGHT, STOP, LEFT, RIGHT

THRESHOLD=150
def filter_pixel(pixel):
  for rgb_component in pixel:
    if rgb_component >= THRESHOLD:
      return 0
  return 1

NUM_ROWS=20
def get_line_offset(current_frame):
  # Take middle half and run filter over it
  width_of_frame = len(current_frame)
  height_of_frame = len(current_frame[0])

  half_frame = []
  for row in xrange(width_of_frame/4, width_of_frame*3/4):
    row_for_half_frame = []
    for col in xrange(height_of_frame/4, height_of_frame*3/4):
      row_for_half_frame.append(filter_pixel(current_frame[row][col]))
    half_frame.append(row_for_half_frame)

  # Average middle 20(?) rows, find line
  # TODO: Other stuff to convet ti inches

def get_speed_and_heading(current_frame):
  next_direction = get_next_direction()
  line_offset = get_line_offset(current_frame)
  if next_direction == 'STOP':
    return (0, 0) # Speed first, then heading
  else: # Go straight
    return (2, 0)

def communicate_to_actuation(speed_heading):
  print speed_heading

if __name__ == '__main__':
  camera = cv2.VideoCapture(0)
  try:
    while True:
      success, current_frame = camera.read()
      if success:
        speed_heading = get_speed_and_heading(current_frame)
        communicate_to_actuation(speed_heading)
      else:
        pass
  finally:
    camera.release()
