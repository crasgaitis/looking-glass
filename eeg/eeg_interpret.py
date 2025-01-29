from pylsl import StreamInlet, resolve_streams
import numpy as np
from scipy.signal import welch
from collections import deque
import matplotlib.pyplot as plt

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

# Initialize a ring buffer for EEG data
buffer = deque(maxlen=buffer_size)

print("Receiving EEG data...")

def compute_band_power(data, fs):
    """Computes power spectral density and extracts EEG bands."""
    f, Pxx = welch(data, fs=fs, nperseg=nperseg)

    # Total power across all frequencies
    total_power = np.trapz(Pxx, f)

    # Define frequency bands
    delta_band = (f >= 1) & (f < 4)
    theta_band = (f >= 4) & (f < 8)
    alpha_band = (f >= 8) & (f < 12)
    beta_band = (f >= 12) & (f < 30)

    # Integrate the power spectral density over each band
    delta_power = np.trapz(Pxx[delta_band], f[delta_band])
    theta_power = np.trapz(Pxx[theta_band], f[theta_band])
    alpha_power = np.trapz(Pxx[alpha_band], f[alpha_band])
    beta_power = np.trapz(Pxx[beta_band], f[beta_band])

    return delta_power, theta_power, alpha_power, beta_power, total_power

# Set up the plot
plt.ion()  # Interactive mode on
fig, ax = plt.subplots(figsize=(6, 8))
ax.set_ylim(0, 100)
ax.set_ylabel('Percentage (%)')
ax.set_title('Current Band Power Distribution')
ax.set_xticks([])
ax.legend(loc='upper right')

# Create empty handles for the legend
delta_patch = plt.Rectangle((0, 0), 1, 1, fc='blue')
theta_patch = plt.Rectangle((0, 0), 1, 1, fc='green')
alpha_patch = plt.Rectangle((0, 0), 1, 1, fc='yellow')
beta_patch = plt.Rectangle((0, 0), 1, 1, fc='red')
ax.legend([delta_patch, theta_patch, alpha_patch, beta_patch], ['Delta', 'Theta', 'Alpha', 'Beta'])

while True:
    # Pull a sample from the LSL stream
    sample, timestamp = inlet.pull_sample()

    # Ensure sample is valid before processing
    if sample:
        buffer.append(sample)

    # Process when buffer is full
    if len(buffer) == buffer_size:
        data = np.array(buffer)  # Convert buffer to NumPy array

        # Process only channel 1 (index 0)
        ch = 2
        delta, theta, alpha, beta, total_power = compute_band_power(data[:, ch], fs)

        # Compute percentages safely
        if total_power != 0:
            delta_percent = (delta / total_power) * 100
            theta_percent = (theta / total_power) * 100
            alpha_percent = (alpha / total_power) * 100
            beta_percent = (beta / total_power) * 100
        else:
            delta_percent = theta_percent = alpha_percent = beta_percent = 0

        # Clear the axis to redraw
        ax.cla()
        ax.set_ylim(0, 100)
        ax.set_ylabel('Percentage (%)')
        ax.set_title('Current Band Power Distribution')
        ax.set_xticks([])

        # Plot the stacked bar chart
        bottom_alpha = delta_percent + theta_percent
        bottom_beta = bottom_alpha + alpha_percent

        ax.bar(0, delta_percent, label='Delta', color='blue')
        ax.bar(0, theta_percent, bottom=delta_percent, label='Theta', color='green')
        ax.bar(0, alpha_percent, bottom=delta_percent + theta_percent, label='Alpha', color='yellow')
        ax.bar(0, beta_percent, bottom=delta_percent + theta_percent + alpha_percent, label='Beta', color='red')

        # Add legend
        ax.legend(loc='upper right')

        # Refresh the plot
        plt.draw()
        plt.pause(0.001)
