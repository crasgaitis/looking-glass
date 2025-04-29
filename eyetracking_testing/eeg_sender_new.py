# print live eeg data to terminal

import time
from pylsl import StreamInlet, resolve_streams, local_clock
from eegutil import compute_band_powers, update_buffer, get_last_data
import numpy as np
import socketio

BUFFER_LENGTH = 5
EPOCH_LENGTH = 1
OVERLAP_LENGTH = 0
SHIFT_LENGTH = EPOCH_LENGTH - OVERLAP_LENGTH
INDEX_CHANNEL = [0]

streams = resolve_streams()

petal_stream = next((s for s in streams if s.name() == 'PetalStream_eeg'), None)

if petal_stream is None:
    print("Petal EEG stream not found")
    exit()

inlet = StreamInlet(petal_stream, max_buflen=1)

print("receiving data...")

eeg_time_correction = inlet.time_correction()
fs = int(inlet.info().nominal_srate())

eeg_buffer = np.zeros((int(fs * BUFFER_LENGTH), 1))
filter_state = None  # for use with the notch filter

n_win_test = int(np.floor((BUFFER_LENGTH - EPOCH_LENGTH) /
                               SHIFT_LENGTH + 1))

band_buffer = np.zeros((n_win_test, 4))

# Initialize socketio client
sio = socketio.Client()

@sio.event
def connect():
    print("Connection to server established.")

@sio.event
def connect_error(data):
    print("Connection to server failed.")

@sio.event
def disconnect():
    print("Disconnected from server.")

# Connect to the server running on localhost:5001
sio.connect('http://127.0.0.1:5001')


while True:
        # Obtain EEG data from the LSL stream
        eeg_data, timestamp = inlet.pull_chunk(
            timeout=1, max_samples=int(SHIFT_LENGTH * fs))

        # Only keep the channel we're interested in
        ch_data = np.array(eeg_data)[:, INDEX_CHANNEL]

        # Update EEG buffer with the new data
        eeg_buffer, filter_state = update_buffer(
            eeg_buffer, ch_data, notch=True,
            filter_state=filter_state)

        # Get newest samples from the buffer
        data_epoch = get_last_data(eeg_buffer,
                                            EPOCH_LENGTH * fs)

        # Compute band powers
        band_powers = compute_band_powers(data_epoch, fs)
        band_buffer, _ = update_buffer(band_buffer,
                                                np.asarray([band_powers]))
        delta = band_powers[0]
        theta = band_powers[1]
        alpha = band_powers[2]
        beta = band_powers[3]

        sio.emit('eeg', {
            'delta': delta,
            'theta': theta,
            'alpha': alpha,
            'beta': beta,
            'timestamp': timestamp
        })
