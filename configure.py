import configparser
import numpy as np

config = configparser.ConfigParser()
config.read(r'/Users/joshuadayal/Downloads/SN1010.conf')


def CameraMatrix():
    camera_matrix = np.array([
        [float(config['LEFT_CAM_HD']['fx']), 0, float(config['LEFT_CAM_HD']['cx'])],
        [0, float(config['LEFT_CAM_HD']['fy']), float(config['LEFT_CAM_HD']['cy'])],
        [0, 0, 1]
    ], dtype=np.float64)
    
    return camera_matrix

def DistortionCoefficients():
    dist_coeffs = np.array([
        float(config['LEFT_CAM_HD']['k1']),
        float(config['LEFT_CAM_HD']['k2']),
        float(config['LEFT_CAM_HD']['p1']),
        float(config['LEFT_CAM_HD']['p2']),
        float(config['LEFT_CAM_HD']['k3'])
    ], dtype=np.float64)

    return dist_coeffs
