from bottle import route, run, template
import os
import os.path
import json
from bottle import static_file

@route('/pages/<filename>')
def server_static(filename):
    return static_file(filename, root='pages')

DESTINATION_PATH = "/tmp/destination.txt"
CURRENT_LOCATION_PATH = "/tmp/current_location.txt"

def __readDestination():
    if os.path.exists(DESTINATION_PATH):
        f = open(DESTINATION_PATH, 'r')
        destination = f.read()
        f.close()
    else:
        destination = None
    return destination

@route('/')
def get_home_page():
  return open("pages/index.html").read()

@route('/set_next_destination/<conference_room_name>')
def set_destination(conference_room_name):
    """Used by client to set a new destination for the scooter, i.e. to request a dispatch"""
    if os.path.exists(DESTINATION_PATH):
        return open('pages/busy.html').read()
    else:
        f = open(DESTINATION_PATH, 'w')
        f.write(conference_room_name)
        f.close()
        return open('pages/dispatched.html').read()

@route('/get_next_destination')
def get_destination():
    """Used by scooter to ask where it should go"""
    return json.dumps({'next_destination' : __readDestination()})

@route('/report_code/<conference_room_name>')
def report_current_location(conference_room_name):
    """Used by scooter to report its last location"""
    if __readDestination() == conference_room_name: # did scooter arrive at destination
        if os.path.exists(DESTINATION_PATH):
            os.remove(DESTINATION_PATH) # delete the destination

    f = open(CURRENT_LOCATION_PATH, 'w') # update the location
    f.write(conference_room_name)
    f.close()

run(host='0.0.0.0', port=8080)
