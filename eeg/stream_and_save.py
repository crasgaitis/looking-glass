# print live eeg data to terminal

import time
from pylsl import StreamInlet, resolve_streams
import sys
import uuid
import threading
import os
import pickle

streams = resolve_streams()

petal_stream = next((s for s in streams if s.name() == 'PetalStream_eeg'), None)

if petal_stream is None:
    print("Petal EEG stream not found")
    exit()

inlet = StreamInlet(petal_stream)

print("Connected to stream and ready. Press enter to start stream.")

input()

print("Starting stream... Press enter to stop.")

data = {}
stop_stream = False

def wait_for_key_press():
    global stop_stream
    input()
    stop_stream = True

threading.Thread(target=wait_for_key_press).start()

while not stop_stream:
    sample, timestamp = inlet.pull_sample()
    data[timestamp] = sample
    # print(f"Timestamp: {timestamp}, Sample: {sample}")
    time.sleep(0.01)


filename = f"streams/{uuid.uuid4()}.pickle"

if not os.path.exists("streams"):
    os.makedirs("streams")

print("Stream stopped. Saving data to " + filename)

pickle.dump(data, open(filename, "wb"))

print("Data saved.")
