import numpy as np
from scipy.signal import welch, iirnotch, filtfilt
import socketio
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

# Parameters
fs = 256  # Sampling frequency (Hz)
BUFFER_LENGTH = 5  # Buffer length in seconds
EPOCH_LENGTH = 1  # Processing window length in seconds
OVERLAP_LENGTH = 0  # Overlap between processing windows
SHIFT_LENGTH = EPOCH_LENGTH - OVERLAP_LENGTH  # Amount to shift window

# Calculate buffer size in samples
buffer_size = int(fs * BUFFER_LENGTH)
epoch_size = int(fs * EPOCH_LENGTH)

# Initialize buffer with zeros
eeg_buffer = np.zeros((buffer_size, 1))
filter_state = None  # for use with the notch filter

# Calculate number of windows
n_win_test = int(np.floor((BUFFER_LENGTH - EPOCH_LENGTH) / SHIFT_LENGTH + 1))
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

def update_buffer(buffer, new_data, notch=False, filter_state=None):
    """
    Updates buffer with new_data and applies optional notch filter.
    """
    if new_data.ndim == 1:
        new_data = new_data.reshape(-1, buffer.shape[1])

    # Roll the buffer to make room for new samples
    buffer = np.roll(buffer, -len(new_data), axis=0)

    # Replace the last n elements with new data
    buffer[-len(new_data):] = new_data

    if notch:
        if filter_state is None:
            # Create notch filter at 60 Hz for line noise
            b, a = iirnotch(60, 30, fs)
            # Apply filter
            buffer, filter_state = filtfilt(b, a, buffer, axis=0, padtype='odd', padlen=3*(max(len(b), len(a))-1), method='pad', irlen=None)
        else:
            buffer, filter_state = filtfilt(b, a, buffer, axis=0, padtype='odd', padlen=3*(max(len(b), len(a))-1), method='pad', irlen=None)

    return buffer, filter_state

def get_last_data(buffer, n_samples):
    """
    Returns the last n_samples of the buffer.
    """
    return buffer[-n_samples:]

def compute_band_powers(data, fs):
    """
    Compute the average power of the EEG signal in different frequency bands using Welch's method.

    Bands:
    - Delta: 1-4 Hz
    - Theta: 4-8 Hz
    - Alpha: 8-12 Hz
    - Beta: 12-30 Hz
    """
    # Compute power spectrum using Welch's method
    nperseg = min(256, len(data))  # Use shorter segments for short data
    f, Pxx = welch(data, fs=fs, nperseg=nperseg)

    # Define frequency bands
    delta_band = (f >= 1) & (f <= 4)
    theta_band = (f >= 4) & (f <= 8)
    alpha_band = (f >= 8) & (f <= 12)
    beta_band = (f >= 12) & (f <= 30)

    # Calculate average power in each band
    delta_power = np.mean(Pxx[delta_band])
    theta_power = np.mean(Pxx[theta_band])
    alpha_power = np.mean(Pxx[alpha_band])
    beta_power = np.mean(Pxx[beta_band])

    # Normalize by total power
    total_power = np.sum(Pxx)
    if total_power != 0:
        delta_percent = (delta_power / total_power) * 100
        theta_percent = (theta_power / total_power) * 100
        alpha_percent = (alpha_power / total_power) * 100
        beta_percent = (beta_power / total_power) * 100
    else:
        delta_percent = theta_percent = alpha_percent = beta_percent = 0

    return [delta_percent, theta_percent, alpha_percent, beta_percent]

def eeg_handler(unused_addr, *args):
    '''
    Every stream is preceded by these data points:
        * int: sample ID
        * int: unix timestamp (whole number)
        * float: unix timestamp (decimal part)
        * int: LSL timestamp (whole number)
        * float: LSL timestamp (decimal part)

    The next set of data in the transmission are:
        EEG:
            * float: channel 1
            * float: channel 2
            * float: channel 3
            * float: channel 4
    '''
    global eeg_buffer, filter_state, band_buffer

    sample_id = args[0]
    unix_ts = args[1] + args[2]
    lsl_ts = args[3] + args[4]
    data = args[5:]  # Should be [channel1, channel2, channel3, channel4]

    # Send data to socket.io server
    sio.emit('eeg', {
        'data': data,
        'timestamp': unix_ts
    })

if __name__ == "__main__":
    dispatcher = Dispatcher()
    dispatcher.map('/PetalStream/eeg', eeg_handler)

    ip = '127.0.0.1'
    udp_port = 14739  # Ensure this matches the sending OSC port

    server = BlockingOSCUDPServer((ip, udp_port), dispatcher)
    print(f"Serving on {ip}:{udp_port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        sio.emit('eeg_disconnect', True)
        sio.disconnect()
