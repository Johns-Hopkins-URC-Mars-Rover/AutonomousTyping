import cv2
import numpy as np
from configure import CameraMatrix, DistortionCoefficients
from distance import DistanceData
import pythonbible as bible

# ── Startup ────────────────────────────────────────────────────────────────────
print(bible.get_verse_text(1001001), "\n")
launch_key = input("Enter the launch key string: ")


# ── ZED Camera Setup ───────────────────────────────────────────────────────────

def init_camera(port = 0):
    """
    Initialises and returns the ZED camera using OpenCV's VideoCapture.

    The ZED camera exposes itself as two side-by-side frames in a single
    wide image. We capture that and split it to get the left frame only.

    Returns:
        cv2.VideoCapture: An opened camera capture object.

    Raises:
        RuntimeError: If the camera cannot be opened.
    """
    cap = cv2.VideoCapture(port)  # Change port if ZED is not on device 0
    if not cap.isOpened():
        raise RuntimeError("Could not open ZED camera. Check USB connection.")
    return cap


def capture_frame(cap):
    """
    Captures a single frame from the ZED camera and returns the left image.

    The ZED outputs a wide side-by-side stereo image. The left half
    corresponds to the left camera, which matches the calibration file.

    Args:
        cap: An open cv2.VideoCapture object for the ZED.

    Returns:
        np.ndarray: The left camera image as a BGR numpy array.

    Raises:
        RuntimeError: If the frame could not be read.
    """
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Failed to capture frame from ZED camera.")

    # ZED side-by-side format: left half = left camera
    width = frame.shape[1] // 2
    left_frame = frame[:, :width]

    return left_frame


def release_camera(cap):
    """
    Releases the ZED camera and closes any OpenCV windows.

    Args:
        cap: The cv2.VideoCapture object to release.
    """
    cap.release()
    cv2.destroyAllWindows()


# ── Pose Estimation ────────────────────────────────────────────────────────────

def estimatePoseSingleMarkers(corners, markerLength, cameraMatrix, distCoeffs):
    """
    Estimates the pose (rotation and translation) of each detected ArUco marker.

    For each marker, a set of 3D object points is defined in the marker's local
    coordinate frame (centered at the origin, lying flat on the z=0 plane).
    OpenCV's solvePnP then solves for the rotation and translation vectors that
    map those object points to their detected 2D image corners.

    Args:
        corners:      List of detected marker corners, each of shape (1, 4, 2).
        markerLength: The real-world side length of the marker in meters.
        cameraMatrix: The 3x3 intrinsic camera matrix.
        distCoeffs:   The camera distortion coefficients.

    Returns:
        rvecs: List of rotation vectors (one per marker).
        tvecs: List of translation vectors (one per marker).
    """
    rvecs = []
    tvecs = []

    for corner in corners:
        obj_points = np.array([
            [-markerLength / 2,  markerLength / 2, 0],   # Top-left
            [ markerLength / 2,  markerLength / 2, 0],   # Top-right
            [ markerLength / 2, -markerLength / 2, 0],   # Bottom-right
            [-markerLength / 2, -markerLength / 2, 0]    # Bottom-left
        ], dtype=np.float32)

        _, rvec, tvec = cv2.solvePnP(
            obj_points, corner, cameraMatrix, distCoeffs
        )
        rvecs.append(rvec)
        tvecs.append(tvec)

    return rvecs, tvecs


def centroid(tvecs):
    """
    Computes the mean position of all detected markers.

    Args:
        tvecs: List or array of translation vectors, each of shape (3, 1).

    Returns:
        A 1D numpy array [x, y, z] representing the average position in meters.
    """
    return np.mean(tvecs, axis=0)


def aligned(x, y, z, threshold=0.005):
    """
    Checks whether the end-effector is sufficiently aligned with the target.

    Args:
        x:         Lateral offset in meters (positive = right).
        y:         Vertical offset in meters (positive = down).
        z:         Depth offset in meters (positive = away from camera).
        threshold: Maximum allowable lateral error in meters (default 5 mm).

    Returns:
        True if all axes are within tolerance, False otherwise.
    """
    return abs(x) < threshold and abs(y) < threshold and abs(z) < 0.03 + threshold


def move(x, y, z):
    """
    Commands the robot end-effector to move by the given offset.

    Args:
        x: Displacement in meters along the x-axis (horizontal).
        y: Displacement in meters along the y-axis (vertical).
        z: Displacement in meters along the z-axis (depth / press direction).
    """
    pass


# ── Configuration ──────────────────────────────────────────────────────────────
marker_size   = 0.02
camera_matrix = CameraMatrix()
dist_coeffs   = DistortionCoefficients()

aruco_dict  = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parameters  = cv2.aruco.DetectorParameters()
detector    = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# ── Open Camera & Capture First Frame ─────────────────────────────────────────
cap   = init_camera()
image = capture_frame(cap)

# ── Initial Pose Estimation ────────────────────────────────────────────────────
corners, ids, rejected = detector.detectMarkers(image)
rvecs, tvecs = estimatePoseSingleMarkers(corners, marker_size, camera_matrix, dist_coeffs)
# FIX [TODO]: Loop until we get a valid detection, otherwise we have no reference for alignment

x, y, z = centroid(tvecs).flatten()

# ── Alignment Loop ─────────────────────────────────────────────────────────────
# Continuously moves the end-effector and captures a fresh frame after each
# correction until the centroid falls within tolerance on all axes.
while not aligned(x, y, z):
    print(f"Aligning... x={x:.4f} m  y={y:.4f} m  z={z:.4f} m")
    move(x, y, z)

    # Pull a new frame from the camera after each movement
    image   = capture_frame(cap)
    corners, ids, rejected = detector.detectMarkers(image)

    if len(corners) == 0:
        print("Warning: no markers detected after move, retrying...")
        continue

    rvecs, tvecs = estimatePoseSingleMarkers(corners, marker_size, camera_matrix, dist_coeffs)
    x, y, z = centroid(tvecs).flatten()

print(f"Aligned.    x={x:.4f} m  y={y:.4f} m  z={z:.4f} m")

# ── Final Image Capture ────────────────────────────────────────────────────────
# Once aligned, take one clean final frame to use for key detection
final_image = capture_frame(cap)
release_camera(cap)   # Camera no longer needed after this point

# ── Key Press Sequence ─────────────────────────────────────────────────────────
# Pass the final aligned image to DistanceData for key detection
data = DistanceData(
    input_string=launch_key,
    image=final_image
)

for movement in data:
    x = movement["horizontal_dist_mm"] / 1000
    y = movement["vertical_dist_mm"]   / 1000
    z = 0

    move(x, y, z)       # Translate to next key
    move(0, 0, -0.035)  # Press key down 35 mm
    move(0, 0,  0.035)  # Lift back up 35 mm