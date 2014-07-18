from bottle import route, run, template
import subprocess

current_destination = None

@route('/request_scuber/<conference_room_name>')
def request_scuber(conference_room_name):
    global current_destination
    if current_destination is None:
        current_destination = conference_room_name
        return template('<b>Hi! Scuber dispatched to {{ conference_room_name }}</b>', conference_room_name=conference_room_name)
    else:
        return template("Sorry, all Scubers are currently busy")

run(host='0.0.0.0', port=8080)
