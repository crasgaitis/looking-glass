# looking-glass
Team: Catherine Rasgaitis, Srishti Bakshi, James Wilson, Arav Bhosle, Brice Liu

## Everything you need is in /eyetracking_testing

1. Install dependencies (`pip install -r requirements.txt`)
2. cd into eyetracking_testing (`cd eyetracking_testing`)
3. (OPTIONAL) Make a new directory under `eyetracking_testing/data` and put the images you want to show the user in there.
4. Run `python server.py`
5. Run `python server.py`
6. Go to http://localhost:5000 for what the user sees and http://localhost:5000/researcher for what you see
7. Open Petal Metrics, set stream name to `PetalStream` (default) and set Type to `OSC`. Make sure Destination IP Address is set to `localhost` and Port is set to `14739` (defaults).
8. Press Save.
9. Start streaming through Petal.
10. In a new terminal, cd into eyetracking_testing (`cd eyetracking_testing`)
11. Run `python eeg_sender_osc.py`
12. NOW go to http://localhost:5000/researcher, you should see the EEG status say connected and the backend light up green as well.
13. Press the 'Calibrate' button and switch to the user view and eyetracking will begin calibration.
14. Choose the directory on the researcher view to show the images from.
15. Press the start button on the researcher view to begin recording data.
16. When the user completes all tasks, the data will be stored to `sessions/(session_id)`. The `session_id` will be shown in the researcher view after the data recording is complete.

## FILE DESCRIPTIONS
- `yaya/` is a directory of CSV files from the pilot study of eye tracking and EEG data. Files are named after what faces were used to generate the stimuli and what % the morph occured at.
- `eeg/` is a directory of utils to graph/log EEG data from petal.
- `README.md` is a markdown file (what you're looking at right now) with information on the repository as a whole.
- `app.py` is the old version of the data collection app which used threads in order to simultaneously collect eeg data, eye tracking data, and display stimuli to the user.
- `eeg_utils.py` is a utility function file which includes processing and streaming functions for dealing with EEG data.
- `eigenfaces.ipynb` is a Jupyter notebook (mix of Python cells + markdown) containing experiments for morphing faces using eigenfaces.
- `faceutils.py` is a utility function file which includes functions for creating stimuli, especially aligning and morphing faces.
- `sanitychecks.ipynb` is an old Jupyter notebook with sanity checks used to verify data quality for the pilot study.
- `shape predictors` are .dat files for getting face landmarks used for aligning faces prior to the morphing steps.
- `test_data.ipynb` contains preliminary figures and analysis from the pilot study.
- `utils.py` contains remaining auxiliary utility functions, especially for eye tracking data.


## ARCHIVED

USAGE:
0. set subject name in app2 and app3 to set saving directory
1. set INDEX_CHANNELS in app2 to select what nodes to record from
- note that temporal resolution and number of nodes have a significant tradeoff
2. run app2.py w/ eye tracker (show to subject) and run app3.py by running Petal Metrics first (this will run EEG collection in VSCode and does not open in browser)
3. syncing step: subject should blink several times while facing away from the screen. We can use this data to sync the eye-tracking and eeg clocks
4. app2.py will stop running automatically, you must press 'q' in terminal for app3.py to stop running. Data saves after both apps terminate.

NOTES:
- app3.py to record eye-tracking and display images
- app2.py to record EEG data

TODOs:

- fix build_dataset function✅
- add flagging functionality ✅
- finish modifying StyleGAN with different anchor points and weighting parameters
- conglomerate script -> input a json file of people objects with name, familiarity, image.
    - outputs a folder with correct images
- finally input folder name with images to use in app ✅
- build up UI for st app ✅
- eye tracking ✅
- eeg recording ✅

- script should include info on initial calibration step with tobii
