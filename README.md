# Autonomous Typing System

An intelligent robotic system that autonomously types on a keyboard by detecting keys using computer vision and commanding robot movements to press them in sequence.

## Overview

This project combines multiple computer vision and robotics techniques to enable a robot to type predefined text on a standard keyboard:

- **ArUco Marker Detection**: Estimates the 3D pose of the robot end-effector using ArUco markers
- **YOLO-based Key Detection**: Identifies individual keyboard keys using a trained YOLOv8 model
- **Distance Measurement**: Calculates inter-key distances for precise movement planning
- **Camera Calibration**: Uses ZED stereo camera calibration data for accurate pose estimation
- **Motion Planning**: Generates movement commands to navigate between keys and press them

## Project Structure

```
AutonomousTyping/
├── detection.py          # Main detection pipeline and pose estimation
├── distance.py           # Key detection and distance measurement
├── configure.py          # Camera calibration data loader
├── requirements.txt      # Python dependencies
├── best.pt              # Trained YOLOv8 model weights for key detection
├── SN30980871.conf      # ZED camera calibration file
└── README.md            # This file
```

## Components

### `detection.py`
**Main orchestration module** that:
- Loads ArUco marker dictionary and detects markers in images
- Estimates 3D pose (rotation and translation) of each detected marker
- Computes centroid of multiple markers for stable reference point
- Checks alignment tolerance before key pressing
- Executes movement sequence to type the input string

Key functions:
- `estimatePoseSingleMarkers()`: Solves PnP problem for marker pose estimation
- `centroid()`: Computes mean position of detected markers
- `aligned()`: Verifies end-effector alignment with target within tolerance
- `move()`: Commands robot motion (stub for integration)

### `distance.py`
**Computer vision analysis module** that:
- Uses YOLO model to detect keyboard keys in images
- Estimates positions of non-detected keys (y, z) through interpolation
- Measures Euclidean and component distances between consecutive keys
- Converts pixel distances to real-world measurements using reference key calibration

Key functions:
- `DistanceData()`: Main function returning list of inter-key movements
- `get_center()`: Computes bounding box center
- `draw_box()`: Visualizes detections on image

### `configure.py`
**Camera configuration module** that:
- Parses ZED camera calibration file (`.conf` format)
- Constructs 3×3 intrinsic camera matrix
- Extracts lens distortion coefficients in OpenCV format

## Requirements

Install dependencies with:
```bash
pip install -r requirements.txt
```

Dependencies:
- **opencv-python**: Computer vision operations (ArUco detection, solvePnP)
- **ultralytics**: YOLOv8 model for key detection
- **numpy**: Numerical computations
- **configparser**: Config file parsing
- **pythonbible** (optional): Launch confirmation message

## Setup

### 1. Camera Calibration
The project uses a ZED camera (serial: SN30980871). To use with a different camera:
1. Download your ZED calibration file from: https://www.stereolabs.com/developers/calib?SN=YOUR_SERIAL_NUMBER
2. Replace `SN30980871.conf` with your calibration file
3. Update the serial number reference in documentation

### 2. Model Weights
The project requires a trained YOLOv8 model for keyboard key detection:
- Place `best.pt` in the project directory (or update `model_path` in `distance.py`)
- Model should be trained to detect individual keyboard keys with confidence > 0.5

### 3. Image Paths
Update image paths in `detection.py` to match your setup:
```python
image = cv2.imread(r'/path/to/your/keyboard.jpg')
```

## Usage

### Basic Usage
```python
python detection.py
```

This prompts for a launch key string and executes the typing sequence on the keyboard.

### Robot Integration
Replace the stub `move()` function in `detection.py` with actual robot control commands:
```python
def move(x, y, z):
    """
    Command robot end-effector motion.
    
    Args:
        x: Displacement in meters (horizontal)
        y: Displacement in meters (vertical)
        z: Displacement in meters (depth/press)
    """
    # Replace with your robot API
    robot.move_relative(x, y, z)
```

### Enabling Closed-Loop Alignment
Uncomment the alignment loop in `detection.py` to enable continuous re-detection and correction during approach:
```python
while (not aligned(x, y, z)):
    print(f"Centroid of detected markers: x={x:.4f} m, y={y:.4f} m, z={z:.4f} m")
    move(x, y, z)  # Move closer
    corners, ids, rejected = detector.detectMarkers(image)
    # Re-estimate pose and check alignment...
```

## Key Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `marker_size` | 0.02 m | ArUco marker physical dimension |
| `real_key_width_mm` | 15.0 mm | Standard keyboard key width (reference) |
| `alignment_threshold` | 0.01 m | Lateral alignment tolerance |
| `press_depth` | 0.035 m | Key press distance |
| `model_confidence` | 0.5 | YOLO detection confidence threshold |

## Workflow

1. **Initialization**
   - Load camera calibration parameters
   - Load pre-trained YOLO model
   - Read input string and keyboard image

2. **Marker Detection**
   - Detect ArUco markers in the image
   - Estimate 3D pose for each marker
   - Compute centroid of all marker positions

3. **Key Detection & Measurement**
   - Run YOLO inference on keyboard image
   - Identify positions of all target keys
   - Interpolate missing key positions (y, z)
   - Measure inter-key distances in millimeters

4. **Motion Execution**
   - For each character in input string:
     - Move horizontally/vertically to key center
     - Press down (~35 mm)
     - Release (lift back up)

## Coordinate System

- **X-axis**: Horizontal (left-right), positive = right
- **Y-axis**: Vertical (up-down), positive = down
- **Z-axis**: Depth (toward/away camera), positive = away from camera
  - Negative Z = press down
  - Positive Z = lift up

## Technical Details

### Pose Estimation
Uses OpenCV's `solvePnP()` to solve the perspective-n-point problem:
- **3D object points**: ArUco marker corners in marker-local frame (z=0 plane)
- **2D image points**: Detected marker corners in image
- **Camera matrix + distortion**: From ZED calibration
- **Output**: Rotation vector (3×1) and translation vector (3×1)

### Distance Scaling
Keyboard distances are scaled using the "1" key as reference:
```
scale_factor = real_key_width_mm / detected_1_key_width_pixels
distance_mm = distance_pixels × scale_factor
```

## Future Enhancements

- [ ] Real-time video stream processing instead of single image
- [ ] Multiple camera synchronization for stereo depth
- [ ] Full 6-DOF trajectory planning with orientation control
- [ ] Adaptive thresholds based on image quality
- [ ] Keyboard layout database for missing key interpolation
- [ ] Robot control integration (UR, ABB, etc.)
- [ ] Error recovery and retry mechanisms
- [ ] Performance benchmarking and optimization

## Troubleshooting

**Issue: ArUco markers not detected**
- Ensure good lighting on markers
- Check marker size parameter matches actual marker
- Verify camera calibration is correct

**Issue: Missing keyboard keys in YOLO detection**
- If confidence < 0.5, lower threshold or retrain model
- Check image resolution and keyboard visibility
- Verify model was trained on similar keyboard layouts

**Issue: Inaccurate distances**
- Recalibrate camera using ZED tools
- Verify reference key ("1") is detected
- Check that `real_key_width_mm` matches your keyboard

## References

- [OpenCV ArUco](https://docs.opencv.org/master/d5/dae/tutorial_aruco_detection.html)
- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [ZED Camera Calibration](https://www.stereolabs.com/developers/calib/)
- [OpenCV solvePnP](https://docs.opencv.org/master/d9/d0c/group__calib3d.html#gadb8dca390f603b8d8490514dd5cda33d)

## License

This project is for educational and research purposes.

## Author

Joshua Dayal

---

**Note**: This is a research/development project. Ensure proper safety measures when operating robotics equipment.
