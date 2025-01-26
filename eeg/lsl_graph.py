# shows a live plot of the eeg data
# must start petal stream (titled PetalStream) first!! (do NOT title it PetalStream_eeg)

import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pylsl import StreamInlet, resolve_streams, local_clock

streams = resolve_streams()
petal_stream = next((s for s in streams if s.name() == 'PetalStream_eeg'), None)  # grab stream

if petal_stream is None:
    print("Petal EEG stream not found")
    exit()

inlet = StreamInlet(petal_stream, max_buflen=1)
num_channels = 5

window_size = 100
data = np.zeros((window_size, num_channels))

fig, axes = plt.subplots(num_channels, 1, figsize=(10, 8))
fig.canvas.manager.set_window_title('Looking Glass Synaptech EEG')
lines = []
channels = ['TP9 (left ear)', 'AF7 (left forehad)', 'AF8 (right forehead)', 'TP10 (right ear)', 'AUX']

for i in range(num_channels):
    line, = axes[i].plot(data[:, i])
    lines.append(line)
    axes[i].set_xlim(0, window_size)
    axes[i].set_ylim(-250, 250)
    axes[i].set_title(channels[i])

latency_text = axes[0].text(0.02, 0.95, '', transform=axes[0].transAxes, fontsize=12,
                            verticalalignment='top')

plt.tight_layout()

def update(frame):
    global data
    sample, timestamp = inlet.pull_sample()
    if sample is None:
        return lines + [latency_text]
    data = np.roll(data, -1, axis=0)
    data[-1, :] = sample
    for i in range(num_channels):
        lines[i].set_ydata(data[:, i])
    current_time = local_clock()
    latency = current_time - timestamp - 34421
    latency_text.set_text(f'Latency: {latency:.3f} s')
    return lines + [latency_text]

ani = animation.FuncAnimation(fig, update, interval=25, blit=True)
plt.show()
