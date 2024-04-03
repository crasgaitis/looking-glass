from flask import Flask, render_template, request
import threading
import pandas as pd
import os
import numpy as np
from utils import build_dataset, get_tracker
from eeg_utils import update_buffer, get_last_data, compute_band_powers
from pylsl import StreamInlet, resolve_byprop

app = Flask(__name__)

# Global variables
image_folder = "static/images/"
images = os.listdir(image_folder)
current_image_index = 0
data = []
ready_flag = threading.Event()

SUBJECT = 'test'
TRACKER = get_tracker()
TIME_RES = 0.1
TOT_TIME = 0.05

BUFFER_LENGTH = 5
EPOCH_LENGTH = 1
OVERLAP_LENGTH = 0
SHIFT_LENGTH = EPOCH_LENGTH - OVERLAP_LENGTH
INDEX_CHANNELS = [2] 

def show_image():
    global current_image_index
    
    while current_image_index < len(images):
        
        ready_flag.clear()

        tracker = get_tracker()
        image_name = images[current_image_index]
        print(f"Showing image: {image_name}")
                
        prefix = subject + "/" + image_name
        
        brain_data_thread = threading.Thread(target=get_brain_data, args=(prefix,))
        eye_tracking_thread = threading.Thread(target=build_dataset, args=(prefix, tracker, SUBJECT, 0.15, 0.09))
        
        brain_data_thread.start()
        eye_tracking_thread.start()
        
        # wait for both threads to finish
        brain_data_thread.join()
        eye_tracking_thread.join()
        
        # wait until ready_flag is 1 before looping again  
        ready_flag.wait()    
            
        # current_image_index += 1

def record_data(image_name, user_number):
    global data
    data.append({'image': image_name, 'user_number': user_number})
    save_data()

def get_brain_data(prefix): 
    eeg_buffer = np.zeros((int(fs * BUFFER_LENGTH), 1))
    filter_state = None
    
    data_list = []
        
    while True:
        eeg_data, timestamp = inlet.pull_chunk(
            timeout=1, max_samples=int(SHIFT_LENGTH * fs))
        
        ch_data = np.array(eeg_data)[:, INDEX_CHANNELS]
        
        # update EEG buffer with the new data
        eeg_buffer, filter_state = update_buffer(
            eeg_buffer, ch_data, notch=True,
            filter_state=filter_state)

        # get newest samples from the buffer
        data_epoch = get_last_data(eeg_buffer, EPOCH_LENGTH * fs)

        # compute band powers
        data_epoch_clean = compute_band_powers(data_epoch, INDEX_CHANNELS, np.mean(timestamp), fs)

        data_list.append(data_epoch_clean)
                
        first_timestamp = data_list[0][30]
        last_timestamp = data_epoch_clean[30]

        if (last_timestamp - first_timestamp > 6):
            df = pd.DataFrame(data_list)
            df.to_csv(f"{prefix}_brain_data.csv", index=False)
            break
    
def save_data():
    global data
    user_df = pd.DataFrame(data)
    user_df.to_csv(f"{subject}/image_user_data.csv", index=False)
    ready_flag.set()

@app.route('/')
def index():    
    return render_template('index.html', images=images)

@app.route('/submit', methods=['POST'])
def submit():
    global current_image_index
    user_number = request.form['user_number']
    image_name = images[current_image_index]
    record_data(image_name, user_number)
    current_image_index += 1
    return '', 204

if __name__ == '__main__':
    global inlet
    global eeg_buffer
    global filter_state
    global subject
    
    subject = input('Test subject name: ')
    
    if os.path.exists(subject):
        print(f"The folder '{subject}' already exists.")
    else:
        os.mkdir(subject)
    
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

    # get the stream info
    info = inlet.info()
    fs = int(info.nominal_srate())

    # initialize raw EEG data buffer
    eeg_buffer = np.zeros((int(fs * BUFFER_LENGTH), 1))
    filter_state = None  # for use with the notch filter

    print('EEG is set up')
        
    threading.Thread(target=show_image).start()

    app.run(debug=True, port=1430)
