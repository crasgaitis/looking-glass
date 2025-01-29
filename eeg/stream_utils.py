import pickle
import matplotlib.pyplot as plt


def load_stream(filename):
    # if filename has .pickle, load it else add .pickle
    if filename[-7:] != ".pickle":
        filename += ".pickle"

    return pickle.load(open(filename, "rb"))


def graph_stream(stream_data):
    timestamps = list(stream_data.keys())
    values = list(stream_data.values())

    # Transposing the list of values to separate them into individual series
    series = list(map(list, zip(*values)))

    plt.figure(figsize=(10, 6))

    for i in range(4): # exclude AUX stream
        plt.plot(timestamps, series[i], label=f'Series {i+1}')

    plt.xlabel('Timestamps')
    plt.ylabel('Values')
    plt.title('EEG Stream Data Over Time')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    filename = input("Enter the filename/uid of the stream to load: ")
    data = load_stream(filename)
    graph_stream(data)
