**Overview**

This project contains two main Python pose scripts and a small `Homedefender` Arduino subproject. The README below reflects the current filenames in the repository:

- `Openpose.py` — OpenCV DNN (TensorFlow) based pose detector with a screen-color trigger and serial output to an Arduino (full automation).
- `pose_mediapipe_no_trigger.py` — MediaPipe-based pose detector (renamed from `OpenposeNoColor.py`). Can be run without screen capture and supports serial output to the Arduino.
- `Homedefender/` — contains Arduino code and a helper script:
  - `Homedefender/Motioncapture/Motioncapture.ino` — Arduino sketch that accepts serial commands like `X{deg}Y{deg}T{ON|OFF}\\n` and moves servos / toggles a relay.
  - `Homedefender/Homedefender3000.py` — (auxiliary Python script; open to check its role if needed).

**What each script does**

- `Openpose.py` (DNN + screen-color trigger)
  - Loads `graph_opt.pb` via `cv.dnn.readNetFromTensorflow(...)` and extracts pose keypoints from webcam frames.
  - Runs a background trigger thread that samples a small screen region (health bar) using `pyscreenshot`/`mss` and `extcolors` to decide when to set `triggerstr = "ON"`.
  - Opens a serial connection (example: `COM5`, 115200) and writes messages `X{deg}Y{deg}T{ON|OFF}\\n` to the Arduino.
  - Visualizes detections with OpenCV drawing functions.

- `pose_mediapipe_no_trigger.py` (MediaPipe variant)
  - Uses `mediapipe` (`mp_pose`) to detect landmarks and `mp_drawing` to visualize them.
  - Computes `incomingdegreeX`/`incomingdegreeY` from shoulder landmarks and writes the formatted message over serial to the Arduino.
  - It can be extended with either a screen-color trigger (port the `triggerthread`) or a gesture-based trigger (recommended for demos).

- `Homedefender/Motioncapture/Motioncapture.ino` (Arduino)
  - Reads serial lines and parses `X...Y...T...` commands, moves `xServo`/`yServo`, and provides a `triggertruefalse()` function that returns true when `ON` is present.
  - Attach servos to pins configured in the sketch (by default pins 10 and 11) and a relay to `RELAY_PIN` (pin 7).

**Dependencies**

- Python packages (install via `pip`):
  - `opencv-python`
  - `mediapipe`
  - `pyserial`
  - `pyscreenshot` or `mss` and `extcolors` (if you use the screen-color trigger in `Openpose.py`)
  - `pytesseract` (optional; referenced in `Openpose.py`)

Install example (PowerShell):

```powershell
pip install opencv-python mediapipe pyserial mss extcolors pyscreenshot pytesseract
```

**How to run**

- Run the DNN + color-trigger script (requires `graph_opt.pb` and a valid COM port):

```powershell
python Openpose.py
```

- Run the MediaPipe variant (renamed to `pose_mediapipe_no_trigger.py`):

```powershell
python pose_mediapipe_no_trigger.py
```

- Upload the Arduino sketch to your board using the Arduino IDE or `arduino-cli`:

```powershell
# example with arduino-cli (adjust board and port)
arduino-cli upload -p COM3 --fqbn arduino:avr:uno Homedefender/Motioncapture/Motioncapture.ino
```

Ensure the serial port in the Python script matches the Arduino port (for example `COM5`). The sketch expects messages like `X90Y95TOFF\\n`.

**Notes & quick fixes**

- `pose_mediapipe_no_trigger.py` was renamed from `OpenposeNoColor.py` — confirm it initializes `ser` before calling `ser.write(...)`. A safe pattern:

```py
ser = None
try:
    ser = serial.Serial('COM5', 115200, timeout=1)
except Exception as e:
    print('Serial not opened:', e)

if ser and ser.is_open:
    ser.write(msg.format(inX, inY, triggerstr).encode())

# on exit
if ser:
    try:
        ser.close()
    except Exception:
        pass
```

- If you use the screen-color trigger from `Openpose.py`, `mss` is a more reliable cross-platform capture method than `pyscreenshot` on Windows. The repository already contains examples using `mss`.

- The runtime text overlay uses `cv2.putText(frame, '%.2fms' % (end - start / freq), ...)` in several scripts; it likely intends `(end - start) / freq`.

**Suggested clear filenames (optional)**

- If you prefer names that explicitly state capabilities, use:
  - `pose_dnn_trigger_serial.py` for `Openpose.py`
  - `pose_mediapipe_no_trigger.py` (current) for the MediaPipe variant

I can also perform the rename in the repository and update any references if you want me to. Additionally, I can:

- Add a short `USAGE.md` with wiring diagrams and COM-port troubleshooting, or
- Patch `pose_mediapipe_no_trigger.py` to add a gesture-based trigger (both wrists above head) instead of the screen-color trigger for safe demos.

---
If you'd like me to rename files, update serial initialization, or add a gesture trigger, tell me which change and I will apply it.
