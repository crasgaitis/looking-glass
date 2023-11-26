import threading
from flask import Flask, render_template
import tobii_research as tr
from utils import *
from werkzeug.serving import run_simple


app = Flask(__name__)

def run_flask_app():
    # app.run(debug=True, port=5003) 
    run_simple('localhost', 5003, app, use_reloader=False)
    
@app.route('/')
def home():    
    return render_template('index.html')

if __name__ == '__main__':
    # set up
    tracker = get_tracker()
    data, _ = build_dataset(tracker, "test")
    
    # get info
    print("Starting new session...")
    subject_name = input("Subject name: ")
    time_res = float(input("Time resolution (s): "))
    tot_time = float(input("Time to record (min): "))
    
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
    data, _ = build_dataset(tracker, subject_name, time_step_sec = time_res, tot_time_min = tot_time)