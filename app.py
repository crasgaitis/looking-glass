import io
import os
import numpy as np
from flask import Flask, render_template, Response
import tobii_research as tr
from utils import *

app = Flask(__name__)

@app.route('/')
def home():
    # get info
    print("Starting new session...")
    subject_name = input("Subject name: ")
    time_res = input("Time resolution (s): ")
    tot_time = input("Time to record (min): ")
    
    tracker = get_tracker()
    
    build_dataset(tracker, subject_name, time_res, tot_time)
    
    return render_template('index.html', subject_name=subject_name) # also get json w/ img links

if __name__ == '__main__':
    app.run(debug=True)