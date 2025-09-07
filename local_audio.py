import sounddevice as sd
import numpy as np
from audio_interfaces import AudioInput, AudioOutput

class LocalMicrophoneInput(AudioInput):
    """Concrete class for reading audio from the system microphone."""
    def __init__(self, samplerate=16000, blocksize=4000):
        self.samplerate = samplerate
        self.blocksize = blocksize # ~250ms chunks
        self.stream = None

    def start(self):
        # Create an input stream. We'll use 16kHz, mono, as it's ideal for Whisper.
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            blocksize=self.blocksize,
            dtype='float32' # Piper and Whisper may need int16, we'll convert later.
        )
        self.stream.start()

    def read_chunk(self):
        # Read one chunk of audio from the stream.
        # This will block until the chunk is ready.
        audio_data, overflowed = self.stream.read(self.blocksize)
        if overflowed:
            print("Audio input overflowed! Data may be lost.")
        # Convert float32 to int16 for compatibility with whisper.cpp/piper
        audio_data_int16 = (audio_data * 32767).astype(np.int16)
        return audio_data_int16.tobytes() # Return raw bytes

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()

class LocalSpeakerOutput(AudioOutput):
    """Concrete class for playing audio to the system speakers."""
    def __init__(self, samplerate=22050): # Piper's default sample rate
        self.samplerate = samplerate
        self.stream = None

    def start(self):
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype='int16'
        )
        self.stream.start()

    def write_chunk(self, audio_data):
        # audio_data is raw bytes from piper. Convert to numpy array.
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        # Write the audio data to the output stream to play it.
        self.stream.write(audio_array)

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()