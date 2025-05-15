import socket
import pickle
import uuid
import os
from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

recording = False
eeg_data = []
eyetracker_data = {}
state_data = []

# serve images
@app.route('/images/<path:path>')
def serve_images(path):
    return send_from_directory('data', path)

@app.route('/GazeCloudAPI.js')
def serve_GazeCloudAPI():
    return send_from_directory('static', 'GazeCloudAPI.js')

@app.route('/webgazer.js')
def serve_webgazer():
    return send_from_directory('static', 'webgazer.js')

# given an image index, return it from the dir else return 404
@app.route('/i/<string:folder>/<int:index>')
def serve_image(folder, index):
    # get the index'th image from the data directory (list files then get that index, do NOT use name)
    images = [img for img in os.listdir(f'data/{folder}') if img != '.DS_Store']
    # order by name
    images.sort()

    if index < len(images):
        return send_from_directory(f'data/{folder}', images[index])
    else:
        return '404', 404

@app.route('/')
def index():
    return render_template('indexv2.html')

@app.route('/old')
def indexv2():
    return render_template('indexold.html')

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
        eeg_data.append(data)
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
    global state_data
    state_data = []
    eeg_data = []
    eyetracker_data = {}
    recording = True

@socketio.on('state_update')
def handle_state_update(data):
    state_data.append(data)

@socketio.on('start_show_faces')
def handle_start_show_faces(data):
    print(data)
    print("Starting show faces")
    emit('start_show_faces', data, broadcast=True)

@socketio.on('get_directories')
def handle_get_directories(data):
    directories = [d for d in os.listdir('data') if os.path.isdir(os.path.join('data', d))]
    emit('directories', {'faces': directories}, broadcast=True)

@socketio.on('end_recording')
def handle_end_recording(data):
    global recording
    global eeg_data
    global eyetracker_data
    global recording
    global state_data
    recording = False

    uid = uuid.uuid4()

    eeg_filename = f"sessions/{uid}_eeg.pickle"
    eyetracker_filename = f"sessions/{uid}_et.pickle"
    state_filename = f"sessions/{uid}_state.pickle"

    # send pathname to client
    emit('paths', {'eeg': eeg_filename, 'eyetracker': eyetracker_filename, 'state': state_filename}, broadcast=True)

    if not os.path.exists("sessions"):
        os.makedirs("sessions")

    pickle.dump(eeg_data, open(eeg_filename, "wb"))
    pickle.dump(eyetracker_data, open(eyetracker_filename, "wb"))
    pickle.dump(state_data, open(state_filename, "wb"))


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5001, allow_unsafe_werkzeug=True)
