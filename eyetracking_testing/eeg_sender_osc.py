import numpy as np
from scipy.signal import welch
from collections import deque
import socketio
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

# Parameters
fs = 256  # Sampling frequency (Hz)
buffer_size = 256  # Number of samples in buffer (1 second of data)
nperseg = 128  # Segment length for Welch’s method

buffer = deque(maxlen=buffer_size)

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

# Connect to the server running on localhost:5000
sio.connect('http://127.0.0.1:5000')

def compute_band_power(data, fs):
    """Computes power spectral density and extracts EEG bands."""
    f, Pxx = welch(data, fs=fs, nperseg=nperseg)
    total_power = np.trapz(Pxx, f)

    # frequency bands
    delta_band = (f >= 1) & (f < 4)
    theta_band = (f >= 4) & (f < 8)
    alpha_band = (f >= 8) & (f < 12)
    beta_band = (f >= 12) & (f < 30)

    delta_power = np.trapz(Pxx[delta_band], f[delta_band])
    theta_power = np.trapz(Pxx[theta_band], f[theta_band])
    alpha_power = np.trapz(Pxx[alpha_band], f[alpha_band])
    beta_power = np.trapz(Pxx[beta_band], f[beta_band])

    return delta_power, theta_power, alpha_power, beta_power, total_power

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
    sample_id = args[0]
    unix_ts = args[1] + args[2]
    lsl_ts = args[3] + args[4]
    data = args[5:]  # Should be [channel1, channel2, channel3, channel4]

    # Ensure that we have exactly 4 EEG channels
    if len(data) != 5:
        print("Received data with incorrect number of channels.")
        return

    # Append data to buffer
    buffer.append(data)

    if len(buffer) == buffer_size:
        data_array = np.array(buffer)
        # data_array has shape (buffer_size, 4)

        # Use channels 2 and 3 (indices 1 and 2) for calculations
        ch2_data = data_array[:, 0]
        ch3_data = data_array[:, 3]

        delta2, theta2, alpha2, beta2, total_power2 = compute_band_power(ch2_data, fs)
        delta3, theta3, alpha3, beta3, total_power3 = compute_band_power(ch3_data, fs)

        delta = (delta2 + delta3) / 2
        theta = (theta2 + theta3) / 2
        alpha = (alpha2 + alpha3) / 2
        beta = (beta2 + beta3) / 2
        total_power = (total_power2 + total_power3) / 2

        if total_power != 0:
            delta_percent = (delta / total_power) * 100
            theta_percent = (theta / total_power) * 100
            alpha_percent = (alpha / total_power) * 100
            beta_percent = (beta / total_power) * 100
        else:
            delta_percent = theta_percent = alpha_percent = beta_percent = 0

        # Send data to socket.io server
        sio.emit('eeg', {
            'delta': delta_percent,
            'theta': theta_percent,
            'alpha': alpha_percent,
            'beta': beta_percent,
            'timestamp': unix_ts
        })
        # The buffer will automatically discard old data due to maxlen

if __name__ == "__main__":
    dispatcher = Dispatcher()
    dispatcher.map('/PetalStream/eeg', eeg_handler)

    ip = '127.0.0.1'
    udp_port = 14739  # Ensure this matches the sending OSC port

    server = BlockingOSCUDPServer((ip, udp_port), dispatcher)
    print(f"Serving on {ip}:{udp_port}")
    server.serve_forever()

    sio.emit('eeg_disconnect', True)
