from local_audio import LocalMicrophoneInput, LocalSpeakerOutput

def main():
    print("Testing audio loop... Press Ctrl+C to stop.")
    mic = LocalMicrophoneInput()
    speaker = LocalSpeakerOutput()

    mic.start()
    speaker.start()

    try:
        while True:
            # 1. Read a chunk from the mic
            audio_chunk = mic.read_chunk()
            # 2. Immediately write it to the speaker
            speaker.write_chunk(audio_chunk)
            print(".", end="", flush=True) # Show we're running
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        mic.stop()
        speaker.stop()

if __name__ == "__main__":
    main()