import os
import wave
from array import array
from datetime import datetime
import pyaudio
import threading
from userpaths import get_my_documents

COUNTDOWN_MAX = 10  # seconds
THRESHOLD = 5000

CHUNK_SIZE = 4410
CHANNELS = 1
FORMAT = pyaudio.paInt16
SAMPLING_RATE = 44100

p = pyaudio.PyAudio()
stream = p.open(
    rate=SAMPLING_RATE,
    channels=CHANNELS,
    format=FORMAT,
    input=True,
    frames_per_buffer=CHUNK_SIZE
)

continue_loop = True


def get_filepath():
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{current_datetime}.wav"
    file_path = f"{get_my_documents()}/sound_detection/{filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create parent directory if it doesn't exist
    return file_path


def save_to_file(file_path: str, data_to_save: []):
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(SAMPLING_RATE)
    wf.writeframes(b''.join(data_to_save))
    wf.close()


def run():
    countdown = COUNTDOWN_MAX
    sound_to_save = []
    saving_chunks = False

    while continue_loop:
        chunk = stream.read(CHUNK_SIZE)
        snd_data = array('h', chunk)
        snd_data_max = max(snd_data)
        print(f"{snd_data_max}  ", end='\r')

        if snd_data_max > THRESHOLD and not saving_chunks:
            saving_chunks = True

        if snd_data_max > THRESHOLD and saving_chunks:
            countdown = COUNTDOWN_MAX

        if snd_data_max < THRESHOLD and saving_chunks:
            countdown -= CHUNK_SIZE / SAMPLING_RATE
            if countdown <= 0:
                # Countdown adds 10 additional seconds to the recording.
                # Remove last 9 seconds. Leave 1 second offset.
                sound_to_save = sound_to_save[: int(len(sound_to_save) - 9 * (1 / (CHUNK_SIZE / SAMPLING_RATE)))]
                save_to_file(get_filepath(), sound_to_save)

                saving_chunks = False
                countdown = COUNTDOWN_MAX
                sound_to_save = []

        if saving_chunks:
            sound_to_save.append(chunk)


def exit_condition():
    input("Press Enter to exit.\n")
    global continue_loop
    continue_loop = False


if __name__ == "__main__":
    t = threading.Thread(target=exit_condition)
    t.start()

    run()

    t.join()
    stream.close()
    p.terminate()
    print("Exiting.")
