# looking-glass
Team: Catherine Rasgaitis, Srishti Bakshi

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