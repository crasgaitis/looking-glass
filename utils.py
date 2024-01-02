import math
import os
import threading
import time
import pandas as pd
import tobii_research as tr
import keyboard

global_gaze_data = None
lock = threading.Lock()

def get_tracker():
  all_eyetrackers = tr.find_all_eyetrackers()
  # print(f'{len(all_eyetrackers)} trackers found.')

  for tracker in all_eyetrackers:
    # print("Model: " + tracker.model)
    # print("Serial number: " + tracker.serial_number) 
    # print(f"Can stream gaze data: {tr.CAPABILITY_HAS_GAZE_DATA in tracker.device_capabilities}")
    return tracker

def gaze_data_callback(gaze_data):
  global global_gaze_data
  with lock:
    global_gaze_data = gaze_data
  
def gaze_data(eyetracker, wait_time=5):
  global global_gaze_data
  
  with lock:
    eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

  time.sleep(wait_time)
  
  with lock:
    eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

  return global_gaze_data

def combine_dicts_with_labels(dict_list):
    combined_dict = {}
    for i, dictionary in enumerate(dict_list, start=1):
        label = f"timestep_{i}"
        combined_dict[label] = dictionary

    return combined_dict
  
def build_dataset(tracker, label, title=None, add_on = False, df_orig = pd.DataFrame(), 
                  time_step_sec = 0.5, tot_time_min = 0.1):
    
    global global_gaze_data
    
    intervals = math.ceil((tot_time_min * 60) / time_step_sec)
    dict_list = []
    
    for _ in range(intervals):
        data = gaze_data(tracker, time_step_sec)
        dict_list.append(data)
    
    tot_dict = combine_dicts_with_labels(dict_list)
    df = pd.DataFrame(tot_dict).T
    df['type'] = label
    
    if title != None:
      os.makedirs(label, exist_ok=True)
      dir = label + "/"
      df.to_csv(dir + title + ".csv", index=False)
        
    # if add_on:
    #     df_new = pd.concat([df_orig, df])
    #     df_new = df_new.reset_index(drop=True)
    #     return df_new
    
    # else:
    #     return df, dict_list