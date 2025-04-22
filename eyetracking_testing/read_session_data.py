import pickle

session_id = input("Enter session ID: ")
session_eeg = pickle.load(open(f"sessions/{session_id}_eeg.pickle", "rb"))
session_et = pickle.load(open(f"sessions/{session_id}_et.pickle", "rb"))
session_state = pickle.load(open(f"sessions/{session_id}_state.pickle", "rb"))

# Get the keys from the session_et dictionary
keys = list(session_eeg.keys())

# Initialize a variable to store the sum of differences
total_diff = 0
count = 0

# Loop through the keys up to the second-to-last key
for i in range(len(keys) - 1):
    current_key = keys[i]
    next_key = keys[i + 1]

    # Calculate the difference between consecutive keys divided by 2
    diff = (next_key - current_key) / 2

    # Add to the total
    total_diff += diff
    count += 1

# Calculate the average difference
avg_diff = total_diff / count if count > 0 else 0

print(f"Average difference between consecutive keys: {avg_diff}")


print("Session state:")
print(session_state)

print()
print("Session EEG:")
print(session_eeg)

print()
print("Session Eye Tracking:")
print(session_et)
