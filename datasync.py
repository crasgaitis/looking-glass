# syncs data from Tobii eye tracker and EEG (petal) through labstreaminglayer
# NOT tested

import tobii_research as tr
from pylsl import StreamInfo, StreamOutlet, resolve_byprop, StreamInlet, local_clock
import time
from collections import deque
from threading import Lock

found_eyetrackers = tr.find_all_eyetrackers()
if not found_eyetrackers:
    print("No Tobii eye trackers found!")
    exit()
eyetracker = found_eyetrackers[0]
print(f"Connected to Tobii: {eyetracker.model} (Serial: {eyetracker.serial_number})")

tobii_stream_name = 'Tobii_Gaze'
tobii_stream_type = 'Gaze'
n_channels = 2 
info = StreamInfo(tobii_stream_name, tobii_stream_type, n_channels,
                  eyetracker.get_gaze_output_frequency(), 'float32', eyetracker.serial_number)
outlet = StreamOutlet(info)

tobii_buffer = deque(maxlen=1000) 
buffer_lock = Lock()

def gaze_data_callback(gaze_data):
    """Callback function for Tobii gaze data."""
    lsl_timestamp = local_clock()
    gaze_x = gaze_data['left_gaze_point_on_display_area'][0]
    gaze_y = gaze_data['left_gaze_point_on_display_area'][1]
    
    outlet.push_sample([gaze_x, gaze_y], lsl_timestamp)
    
    with buffer_lock:
        tobii_buffer.append((lsl_timestamp, (gaze_x, gaze_y)))

eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

print("Looking for LSL streams...")
streams = resolve_byprop('type', 'EEG', timeout=5)
if not streams:
    print("No EEG stream found.")
    eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    exit()
inlet = StreamInlet(streams[0])
print(f"Connected to LSL stream: {inlet.info().name()}")

try:
    while True:
        sample, timestamp = inlet.pull_sample(timeout=1.0)
        if sample is None:
            continue

        corrected_ts = timestamp + inlet.time_correction()

        with buffer_lock:
            buffer_copy = list(tobii_buffer)
        
        if not buffer_copy:
            continue

        closest = min(buffer_copy, key=lambda x: abs(x[0] - corrected_ts))
        tobii_ts, (gaze_x, gaze_y) = closest
        time_diff = tobii_ts - corrected_ts

        print(f"\nSynced Data - Time diff: {time_diff:.3f}s")
        print(f"EEG Sample: {sample[:5]}...")
        print(f"Gaze Position: X={gaze_x:.2f}, Y={gaze_y:.2f}")

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    print("Disconnected from Tobii eye tracker")