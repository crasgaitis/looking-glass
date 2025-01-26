# print live eeg data to terminal

import time
from pylsl import StreamInlet, resolve_streams

streams = resolve_streams()

petal_stream = next((s for s in streams if s.name() == 'PetalStream_eeg'), None)

if petal_stream is None:
    print("Petal EEG stream not found")
    exit()

inlet = StreamInlet(petal_stream)

print("receiving data...")

while True:
    sample, timestamp = inlet.pull_sample()
    print(f"Timestamp: {timestamp}, Sample: {sample}")
    time.sleep(0.01)
