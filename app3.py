import streamlit as st
import os
from PIL import Image
from utils import build_dataset, get_tracker
import pandas as pd

SUBJECT = 'test'
TRACKER = get_tracker()
TIME_RES = 0.1
TOT_TIME = 0.05

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# list of image paths
folder_path = "static/people_images/"
image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# keys: file name, values: rating
# will be turned into csv file at the very end
selections = dict()
choices = {'1 text' : 1, 
           '2 text' : 2, 
           '3 text' : 3, 
           '4 text' : 4, 
           '5 text' : 5}
    
# alternate between displaying image and rating selection box
if (st.session_state.current_index % 2 == 0):
    # display the current image
    st.image(Image.open(image_files[st.session_state.current_index]), use_column_width=True)

    title = SUBJECT + "_" + str(st.session_state.current_index)

    build_dataset(TRACKER, SUBJECT, title = title, time_step_sec = TIME_RES, tot_time_min = TOT_TIME)
else:
    option = st.selectbox(
        'Rate your familiarity',
        ('1 text', '2 text', '3 text', '4 text', '5 text'))
        
    while option is None:
        option = st.selectbox(
            'Rate your familiarity',
            ('1 text', '2 text', '3 text', '4 text', '5 text'))
        
    # option is the selected choice; query into choices to get corresponding number rating
    rating = choices[option]
    file_name = image_files[st.session_state.current_index - 1]  # ?
    selections[file_name] = rating        

# increment index
st.session_state.current_index += 1

# loop back around
# comment this out when not testing
if st.session_state.current_index >= len(image_files):
    st.session_state.current_index = 0

# create csv file
print(selections)
df = pd.DataFrame(selections)
df.to_csv('output.csv')

# force a re-run of the app to ensure the updated state is used
st.experimental_rerun()

# Notes: time.sleep possibly needed