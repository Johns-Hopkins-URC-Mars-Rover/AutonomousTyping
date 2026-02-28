import cv2
import numpy as np
from configure import CameraMatrix, DistortionCoefficients


def estimatePoseSingleMarkers(corners, markerLength, cameraMatrix, distCoeffs):
    rvecs = []
    tvecs = []
    for corner in corners:
        obj_points = np.array([
            [-markerLength / 2,  markerLength / 2, 0],
            [ markerLength / 2,  markerLength / 2, 0],
            [ markerLength / 2, -markerLength / 2, 0],
            [-markerLength / 2, -markerLength / 2, 0]
        ], dtype=np.float32)

        _, rvec, tvec = cv2.solvePnP(
            obj_points, corner, cameraMatrix, distCoeffs
        )
        rvecs.append(rvec)
        tvecs.append(tvec)

    return rvecs, tvecs

marker_size = 0.02  # real size of the marker in meters
camera_matrix = CameraMatrix()
dist_coeffs = DistortionCoefficients()

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parameters = cv2.aruco.DetectorParameters()
image = cv2.imread(r'/Users/joshuadayal/Downloads/keyboard.jpg')

detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
corners, ids, rejected = detector.detectMarkers(image)

tvecs, rvecs = estimatePoseSingleMarkers(corners, marker_size, camera_matrix, dist_coeffs)
rotation_matrix, _ = cv2.Rodrigues(rvecs[0])


if ids is not None:
    cv2.aruco.drawDetectedMarkers(image, corners, ids)

cv2.imshow("ArUco Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()


# ---------- Test ----------
# print("Rotation Matrix:\n", rotation_matrix)
# print("Rotation Vectors (rvecs):", rvecs)
# print("Translation Vectors (tvecs):", tvecs)
print(np.linalg.det(rotation_matrix)) # Should be close to 1
print(rotation_matrix @ rotation_matrix.T) # Should be close to identity