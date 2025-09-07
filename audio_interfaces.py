from abc import ABC, abstractmethod

class AudioInput(ABC):
    """Abstract base class defining the interface for audio input devices."""
    
    @abstractmethod
    def start(self):
        """Start capturing audio."""
        pass
        
    @abstractmethod
    def read_chunk(self):
        """Return a chunk of raw audio data."""
        pass
        
    @abstractmethod
    def stop(self):
        """Stop capturing audio."""
        pass


class AudioOutput(ABC):
    """Abstract base class defining the interface for audio output devices."""
    
    @abstractmethod
    def start(self):
        """Start the output system."""
        pass
        
    @abstractmethod
    def write_chunk(self, audio_data):
        """Play or send a chunk of raw audio data."""
        pass
        
    @abstractmethod
    def stop(self):
        """Stop the output system."""
        pass