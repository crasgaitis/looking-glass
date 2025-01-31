import socket
import pickle
import uuid
import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

recording = False
eeg_data = {}
eyetracker_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/researcher')
def researcher():
    return render_template('researcher.html')

@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)

# detect eeg data and broadcast
@socketio.on('eeg')
def handle_eeg(data):
    global recording
    global eeg_data
    global eyetracker_data
    if recording:
        eeg_data[data['timestamp']] = data
    emit('eeg', data, broadcast=True)

@socketio.on('eye_tracking_data')
def eye_tracking_data(data):
    global recording
    global eeg_data
    global eyetracker_data
    if recording:
        eyetracker_data[data['time']] = data
    emit('eye_tracking_data', data, broadcast=True)

@socketio.on('eye_tracking_connected')
def handle_eye_tracking_connected(data):
    emit('eye_tracking_connected', data, broadcast=True)

@socketio.on('eye_tracking_calibrating')
def handle_eye_tracking_calibrating(data):
    emit('eye_tracking_calibrating', data, broadcast=True)

@socketio.on('eye_tracking_calibrated')
def handle_eye_tracking_calibrated(data):
    emit('eye_tracking_calibrated', data, broadcast=True)

@socketio.on('eye_track_disconnect')
def handle_eye_track_disconnect(data):
    emit('eye_track_disconnect', data, broadcast=True)

@socketio.on('begin_calib')
def handle_begin_calib(data):
    emit('begin_calib', data, broadcast=True)

@socketio.on('start_recording')
def handle_start_recording(data):
    global recording
    global eeg_data
    global eyetracker_data
    eeg_data = {}
    eyetracker_data = {}
    recording = True


@socketio.on('end_recording')
def handle_end_recording(data):
    global recording
    global eeg_data
    global eyetracker_data
    global recording
    recording = False

    uid = uuid.uuid4()

    eeg_filename = f"sessions/{uid}_eeg.pickle"
    eyetracker_filename = f"sessions/{uid}_et.pickle"

    # send pathname to client
    emit('paths', {'eeg': eeg_filename, 'eyetracker': eyetracker_filename}, broadcast=True)

    if not os.path.exists("sessions"):
        os.makedirs("sessions")

    pickle.dump(eeg_data, open(eeg_filename, "wb"))
    pickle.dump(eyetracker_data, open(eyetracker_filename, "wb"))


if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
