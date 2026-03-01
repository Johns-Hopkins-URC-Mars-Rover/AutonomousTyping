import cv2
import numpy as np
from configure import CameraMatrix, DistortionCoefficients
from distance import DistanceData
import pythonbible as bible

# ── Startup ────────────────────────────────────────────────────────────────────
# Print an opening verse (Genesis 1:1) as a launch confirmation message
print(bible.get_verse_text(1001001), "\n")

launch_key = input("Enter the launch key string: ")


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
        # Define the marker's four corners in its own 3D coordinate system.
        # The marker is centred at the origin and lies flat on the z=0 plane.
        obj_points = np.array([
            [-markerLength / 2,  markerLength / 2, 0],   # Top-left
            [ markerLength / 2,  markerLength / 2, 0],   # Top-right
            [ markerLength / 2, -markerLength / 2, 0],   # Bottom-right
            [-markerLength / 2, -markerLength / 2, 0]    # Bottom-left
        ], dtype=np.float32)

        # Solve for the pose that maps the 3D object points to the 2D image corners
        _, rvec, tvec = cv2.solvePnP(
            obj_points, corner, cameraMatrix, distCoeffs
        )
        rvecs.append(rvec)
        tvecs.append(tvec)

    return rvecs, tvecs


def centroid(tvecs):
    """
    Computes the mean position of all detected markers.

    Taking the centroid of multiple marker translation vectors gives a single
    stable reference point even if individual markers are partially occluded
    or noisy.

    Args:
        tvecs: List or array of translation vectors, each of shape (3, 1).

    Returns:
        A 1D numpy array [x, y, z] representing the average position in meters.
    """
    return np.mean(tvecs, axis=0)


def aligned(x, y, z, threshold=0.01):
    """
    Checks whether the end-effector is sufficiently aligned with the target.

    Lateral alignment (x, y) is checked against a configurable threshold.
    Depth alignment (z) uses a slightly looser tolerance to account for the
    physical press distance of a key (~35 mm).

    Args:
        x:         Lateral offset in meters (positive = right).
        y:         Vertical offset in meters (positive = down).
        z:         Depth offset in meters (positive = away from camera).
        threshold: Maximum allowable lateral error in meters (default 10 mm).

    Returns:
        True if all axes are within tolerance, False otherwise.
    """
    return abs(x) < threshold and abs(y) < threshold and abs(z) < 0.03 + threshold


def move(x, y, z):
    """
    Commands the robot end-effector to move by the given offset.

    Currently a stub — replace with the real robot movement command.

    Args:
        x: Displacement in meters along the x-axis (horizontal).
        y: Displacement in meters along the y-axis (vertical).
        z: Displacement in meters along the z-axis (depth / press direction).
    """
    pass


# ── Configuration ──────────────────────────────────────────────────────────────
marker_size = 0.02          # Real-world ArUco marker side length in meters
camera_matrix = CameraMatrix()
dist_coeffs = DistortionCoefficients()

# ── ArUco Detection ────────────────────────────────────────────────────────────
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parameters = cv2.aruco.DetectorParameters()
image = cv2.imread(r'/Users/joshuadayal/Downloads/keyboard.jpg')

detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
corners, ids, rejected = detector.detectMarkers(image)

# ── Initial Pose & Alignment ───────────────────────────────────────────────────
rvecs, tvecs = estimatePoseSingleMarkers(corners, marker_size, camera_matrix, dist_coeffs)

# Convert the first marker's rotation vector to a full 3x3 rotation matrix.
# This is available for future use (e.g. orientation-aware movements) but is
# not used directly in the current planar x-y motion scheme.
rotation_matrix, _ = cv2.Rodrigues(rvecs[0])

x, y, z = centroid(tvecs).flatten()

# ── Alignment Loop (disabled) ──────────────────────────────────────────────────
# Uncomment to enable closed-loop alignment before key pressing begins.
# The loop continuously moves the end-effector and re-detects markers until
# the centroid falls within the alignment threshold on all axes.
#
# while (not aligned(x, y, z)):
#     print(f"Centroid of detected markers: x={x:.4f} m, y={y:.4f} m, z={z:.4f} m")
#     move(x, y , z)
#     corners, ids, rejected = detector.detectMarkers(image)
#     rvecs, tvecs = estimatePoseSingleMarkers(corners, marker_size, camera_matrix, dist_coeffs)
#     x, y, z = centroid(tvecs).flatten()

# ── Key Press Sequence ─────────────────────────────────────────────────────────
# Retrieve the chained inter-key distances for every character in the launch key
# string. Each entry gives the x/y offset from the previous key to the next.
data = DistanceData(
    input_string=launch_key,
    image=cv2.imread(r'/Users/joshuadayal/Downloads/keyboard.jpg')
)

for movement in data:
    # Convert millimetres → metres for the robot motion commands
    x = movement["horizontal_dist_mm"] / 1000
    y = movement["vertical_dist_mm"] / 1000
    z = 0   # All lateral movement happens in the x-y plane; no depth change yet

    move(x, y, z)       # Translate to the next key position
    move(0, 0, -0.035)  # Press down ~35 mm to actuate the key
    move(0, 0,  0.035)  # Lift back up 35 mm to release the key