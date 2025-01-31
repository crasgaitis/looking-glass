from pylsl import StreamInlet, resolve_streams
import numpy as np
from scipy.signal import welch
from collections import deque
import socketio

# Parameters
fs = 256  # Sampling frequency (Hz)
buffer_size = 256  # Number of samples in buffer (1 second of data)
nperseg = 128  # Segment length for Welch’s method

# Resolve the EEG stream
print("Looking for an EEG stream...")
streams = resolve_streams()
petal_stream = next((s for s in streams if s.name() == 'PetalStream_eeg'), None)

if petal_stream is None:
    raise RuntimeError("Could not find EEG stream with name 'PetalStream_eeg'.")

inlet = StreamInlet(petal_stream, max_buflen=1)

buffer = deque(maxlen=buffer_size)

print("Receiving EEG data...")

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

while True:
    sample, timestamp = inlet.pull_sample()

    if sample:
        buffer.append(sample)

    if len(buffer) == buffer_size:
        data = np.array(buffer)

        # avergae channel 2 and 3 (frontal lobe)
        delta2, theta2, alpha2, beta2, total_power2 = compute_band_power(data[:, 0], fs)
        delta3, theta3, alpha3, beta3, total_power3 = compute_band_power(data[:, 3], fs)

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
            'beta': beta_percent
        })
