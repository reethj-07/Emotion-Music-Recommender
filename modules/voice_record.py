import sounddevice as sd
import soundfile as sf
import tempfile

def record_audio(duration=5, samplerate=16000, channels=1):
    print(f"🔴 Recording for {duration} seconds...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels)
    sd.wait()
    print("✅ Recording complete.")

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(tmp_file.name, recording, samplerate)
    return tmp_file.name
