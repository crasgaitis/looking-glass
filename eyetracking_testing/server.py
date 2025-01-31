from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

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
    emit('eeg', data, broadcast=True)

@socketio.on('eye_tracking_data')
def eye_tracking_data(data):
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

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
