import sounddevice as sd
import numpy as np
from audio_interfaces import AudioInput, AudioOutput

class LocalMicrophoneInput(AudioInput):
    """Concrete implementation of AudioInput for system microphone."""
    
    def __init__(self, samplerate=16000, channels=1, blocksize=4000):
        """
        Initialize the microphone input.
        
        Args:
            samplerate (int): Sample rate in Hz (16000 is optimal for Whisper)
            channels (int): Number of audio channels (1 for mono)
            blocksize (int): Size of audio blocks to read at once
        """
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.stream = None

    def start(self):
        """Start capturing audio from the microphone."""
        try:
            self.stream = sd.InputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                blocksize=self.blocksize,
                dtype='float32'  # We'll record in float32 for processing
            )
            self.stream.start()
            print(f"Microphone started: {self.samplerate}Hz, {self.channels} channel(s)")
        except Exception as e:
            print(f"Error starting microphone: {e}")
            raise

    def read_chunk(self):
        """
        Read a chunk of audio data from the microphone.
        
        Returns:
            bytes: Raw audio data in int16 format
        """
        if not self.stream:
            raise RuntimeError("Microphone stream not started")
            
        # Read audio data
        audio_data, overflowed = self.stream.read(self.blocksize)

        if overflowed:
            raise RuntimeError("Audio input overflowed! Data may be lost.")
        
        # Convert float32 to int16 for compatibility with Whisper.cpp
        audio_data_int16 = (audio_data * 32767).astype(np.int16)
        
        return audio_data_int16.tobytes()

    def stop(self):
        """Stop capturing audio and close the microphone stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("Microphone stopped")



class LocalSpeakerOutput(AudioOutput):
    """Concrete implementation of AudioOutput for system speakers."""
    
    def __init__(self, samplerate=22050, channels=1):
        """
        Initialize the speaker output.
        
        Args:
            samplerate (int): Sample rate in Hz (22050 is Piper's default)
            channels (int): Number of audio channels (1 for mono)
        """
        self.samplerate = samplerate
        self.channels = channels
        self.stream = None

    def start(self):
        """Start the speaker output stream."""
        try:
            self.stream = sd.OutputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                dtype='int16'  # Piper outputs int16 audio
            )
            self.stream.start()
            print(f"Speaker started: {self.samplerate}Hz, {self.channels} channel(s)")
        except Exception as e:
            print(f"Error starting speaker: {e}")
            raise

    def write_chunk(self, audio_data):
        """
        Write a chunk of audio data to the speakers.

        Args:
            audio_data (bytes): Raw audio data in int16 format
        """
        if not self.stream:
            raise RuntimeError("Speaker stream not started")

        if not isinstance(audio_data, bytes):
            raise ValueError("audio_data must be bytes")

        # Convert bytes to numpy array
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
        except ValueError as e:
            raise ValueError(f"Invalid audio data: {e}")

        # Ensure the array is the right shape for output
        if self.channels > 1:
            audio_array = audio_array.reshape(-1, self.channels)

        # Write to output stream
        self.stream.write(audio_array)

    def stop(self):
        """Stop audio output and close the speaker stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("Speaker stopped")


# Simple test function to verify audio works
def test_audio_loop():
    """Test function to verify microphone and speaker work together."""
    print("Testing audio loop... Speak into microphone (press Ctrl+C to stop)")
    
    mic = LocalMicrophoneInput()
    speaker = LocalSpeakerOutput(samplerate=16000)
    
    try:
        mic.start()
        speaker.start()
        
        while True:
            # Read from mic and immediately play through speaker
            audio_chunk = mic.read_chunk()
            speaker.write_chunk(audio_chunk)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during audio test: {e}")
    finally:
        mic.stop()
        speaker.stop()


if __name__ == "__main__":
    # Run the test if this file is executed directly
    test_audio_loop()