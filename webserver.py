from bottle import route, run, template
import os
import os.path
import json

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

@route('/set_next_destination/<conference_room_name>')
def set_destination(conference_room_name):
    """Used by client to set a new destination for the scooter, i.e. to request a dispatch"""
    if os.path.exists(DESTINATION_PATH):
        return template("Sorry, all Scubers are currently busy!")
    else:
        f = open(DESTINATION_PATH, 'w')
        f.write(conference_room_name)
        f.close()
        return template('<b>Hi! Scuber dispatched to {{ conference_room_name }}</b>', conference_room_name=conference_room_name)

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
