import streamlit as st
import os
from PIL import Image
from utils import build_dataset, get_tracker

SUBJECT = 'test'
TRACKER = get_tracker()
TIME_RES = 0.1
TOT_TIME = 0.1

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

# display the current image
st.image(Image.open(image_files[st.session_state.current_index]), caption='Image', use_column_width=True)

title = SUBJECT + "_" + str(st.session_state.current_index)
print(title)
build_dataset(TRACKER, SUBJECT, title = title, time_step_sec = TIME_RES, tot_time_min = TOT_TIME)

# increment index
st.session_state.current_index += 1

# loop back around
if st.session_state.current_index >= len(image_files):
    st.session_state.current_index = 0

# force a re-run of the app to ensure the updated state is used
st.experimental_rerun()
