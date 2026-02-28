import configparser
import numpy as np

# Load the ZED camera calibration file using the camera's serial number
config = configparser.ConfigParser()
config.read(r'/Users/joshuadayal/Downloads/SN1010.conf')


def CameraMatrix():
    """
    Constructs the intrinsic camera matrix for the left ZED camera at HD resolution.

    Reads the focal lengths (fx, fy) and principal point (cx, cy) from the
    camera's .conf calibration file and arranges them into a 3x3 intrinsic matrix:

        [[fx,  0, cx],
         [ 0, fy, cy],
         [ 0,  0,  1]]

    Returns:
        np.ndarray: A 3x3 float64 camera intrinsic matrix.
    """
    # Read focal lengths and principal point from the HD left camera section
    # fx, fy: focal lengths in pixels along x and y axes
    # cx, cy: principal point (optical centre) in pixels
    camera_matrix = np.array([
        [float(config['LEFT_CAM_HD']['fx']), 0,                                   float(config['LEFT_CAM_HD']['cx'])],
        [0,                                  float(config['LEFT_CAM_HD']['fy']),   float(config['LEFT_CAM_HD']['cy'])],
        [0,                                  0,                                    1                                 ]
    ], dtype=np.float64)
    
    return camera_matrix


def DistortionCoefficients():
    """
    Retrieves the lens distortion coefficients for the left ZED camera at HD resolution.

    Reads the radial distortion coefficients (k1, k2, k3) and tangential
    distortion coefficients (p1, p2) from the camera's .conf calibration file,
    returning them in the standard OpenCV order: [k1, k2, p1, p2, k3].

    Returns:
        np.ndarray: A 1D float64 array of 5 distortion coefficients [k1, k2, p1, p2, k3].
    """
    dist_coeffs = np.array([
        float(config['LEFT_CAM_HD']['k1']),   # Radial distortion coefficient 1 (barrel/pincushion)
        float(config['LEFT_CAM_HD']['k2']),   # Radial distortion coefficient 2
        float(config['LEFT_CAM_HD']['p1']),   # Tangential distortion coefficient 1 (lens tilt)
        float(config['LEFT_CAM_HD']['p2']),   # Tangential distortion coefficient 2 (lens tilt)
        float(config['LEFT_CAM_HD']['k3'])    # Radial distortion coefficient 3 (higher order)
    ], dtype=np.float64)

    return dist_coeffs