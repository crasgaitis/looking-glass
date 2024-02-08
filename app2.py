import numpy as np
import pandas as pd
import keyboard

from eeg_utils import update_buffer, get_last_data, compute_band_powers
from pylsl import StreamInlet, resolve_byprop

import warnings
warnings.filterwarnings("ignore")

SUBJECT = 'test'

BUFFER_LENGTH = 5
EPOCH_LENGTH = 1
OVERLAP_LENGTH = 0
SHIFT_LENGTH = EPOCH_LENGTH - OVERLAP_LENGTH
INDEX_CHANNELS = [1, 3]  # [0, 1, 2, 3, 4]

df = pd.DataFrame()
        
# search for active LSL streams
print('Looking for an EEG stream...')
streams = resolve_byprop('type', 'EEG', timeout=2)
if len(streams) == 0:
    raise RuntimeError('Can\'t find EEG stream.')
else:
    print('Found it!')
    print(streams)
    
# set active EEG stream to inlet and apply time correction
print("Start acquiring data")
inlet = StreamInlet(streams[0], max_chunklen=12)
eeg_time_correction = inlet.time_correction()

# get the stream info
info = inlet.info()
fs = int(info.nominal_srate())

# initialize raw EEG data buffer
eeg_buffer = np.zeros((int(fs * BUFFER_LENGTH), 1))
filter_state = None  # for use with the notch filter

# compute the number of epochs in "buffer_length"
n_win_test = int(np.floor((BUFFER_LENGTH - EPOCH_LENGTH) /
                            SHIFT_LENGTH + 1))

# initialize the band power buffer (for plotting)
# bands will be ordered: [delta, theta, alpha, beta]
band_buffer = np.zeros((n_win_test, 4))

while True:
    # obtain EEG data from the LSL stream
    eeg_data, timestamp = inlet.pull_chunk(
        timeout=1, max_samples=int(SHIFT_LENGTH * fs))
    
    data = pd.Series()
    
    for index_channel in INDEX_CHANNELS:
        # only keep the channel we're interested in
        ch_data = np.array(eeg_data)[:, index_channel]

        # update EEG buffer with the new data
        eeg_buffer, filter_state = update_buffer(
            eeg_buffer, ch_data, notch=True,
            filter_state=filter_state)

        # get newest samples from the buffer
        data_epoch = get_last_data(eeg_buffer, EPOCH_LENGTH * fs)

        # compute band powers
        data_epoch_clean = compute_band_powers(data_epoch, index_channel, np.mean(timestamp), fs)

        data = data.append(data_epoch_clean)
            
    # append channel-specific information to DataFrame
    # df = pd.concat([df, data], axis=1)
    df = df.append(data,ignore_index=True)    
    
    if keyboard.is_pressed('q'):
        break

dir = SUBJECT + "/"
df.to_csv(dir + "eeg.csv", index=False)