import pickle

session_id = input("Enter session ID: ")
session_eeg = pickle.load(open(f"sessions/{session_id}_eeg.pickle", "rb"))
session_et = pickle.load(open(f"sessions/{session_id}_et.pickle", "rb"))
session_state = pickle.load(open(f"sessions/{session_id}_state.pickle", "rb"))

print()
print("Session state includes "+str(len(session_state))+" measurements")
print("Session EEG includes "+str(len(session_eeg))+" measurements")
print("Session Eye Tracking includes "+str(len(session_et))+" measurements")
print()
