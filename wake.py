

import pvporcupine
import sounddevice as sd
import numpy as np

# ===============================
# 🔐 PASTE YOUR PICOVOICE KEY
# ===============================
ACCESS_KEY = "3hZcGS3UavCu7XiAV+5iSV0j0aehGS9GJFIMJQOnaQV6Rii9/ISd0Q=="

if not ACCESS_KEY or "PASTE_" in ACCESS_KEY:
    raise RuntimeError("Please paste your Picovoice access key in wake.py")

# Built-in wake words supported by Porcupine
WAKE_WORD = "computer"
WAKE_WORD = "jarvis"

class WakeWord:
    def __init__(self):
        self.porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keywords=[WAKE_WORD]
        )

    def listen(self):
        with sd.RawInputStream(
            samplerate=self.porcupine.sample_rate,
            blocksize=self.porcupine.frame_length,
            dtype="int16",
            channels=1
        ) as stream:
            while True:
                pcm_bytes, _ = stream.read(self.porcupine.frame_length)

                # 🔒 ABSOLUTE SAFE CONVERSION
                pcm = np.frombuffer(pcm_bytes, dtype=np.int16).tolist()

                if self.porcupine.process(pcm) >= 0:
                    return

