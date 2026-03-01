import cv2
from ultralytics import YOLO
import math

# ── Constants ──────────────────────────────────────────────────────────────────
real_key_width_mm = 15.0
refernce_key_default = "CENTER"

# ── Helper Functions ───────────────────────────────────────────────────────────

def draw_box(image, box, label, conf=-1):
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(image, f'{label}', (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def get_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def DistanceData(input_string, image, model_path=r'best.pt'):
    """
    Detects keyboard keys in an image and measures distances between them.

    Args:
        input_string: The string whose keys you want to locate and measure.
        image:   The loaded OpenCV image object.
        model_path:   Path to the YOLO model weights file.

    Returns:
        A list of dicts, each containing:
            start_key, end_key, euclidean_dist_mm, vertical_dist_mm, horizontal_dist_mm
    """
    print("Input string:", input_string)

    target_keys = list(input_string)
    refernce_key = refernce_key_default
    positions = {}

    # ── Model & Image Setup ────────────────────────────────────────────────────
    model = YOLO(model_path)

    if image is None:
        raise FileNotFoundError(f"Could not load image. Check the image object.")

    results = model.predict(image, conf=0.5, verbose=False, show=False)

    pixel_width = None

    # ── Detection Loop ─────────────────────────────────────────────────────────
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            cls_name = model.names[cls]

            positions[cls_name] = (x1, y1, x2, y2)

            if cls_name in target_keys and cls_name != "z" and cls_name != "y":
                draw_box(image, (x1, y1, x2, y2), cls_name, conf)

            if cls_name == "1":
                pixel_width = x2 - x1

    if pixel_width is None:
        raise ValueError("Reference key '1' not detected. Cannot compute scale.")

    # ── Estimate 'y' Position ──────────────────────────────────────────────────
    if "y" in target_keys:
        if "t" in positions and "u" in positions:
            tx, ty = get_center(positions["t"])
            ux, uy = get_center(positions["u"])

            y_center = ((tx + ux) / 2, (ty + uy) / 2)
            half_w = pixel_width / 2

            y_box = (
                y_center[0] - half_w,
                y_center[1] - half_w,
                y_center[0] + half_w,
                y_center[1] + half_w,
            )

            positions["y"] = y_box
            draw_box(image, y_box, "y")

    # ── Estimate 'z' Position ──────────────────────────────────────────────────
    if "z" in target_keys:
        if "x" in positions:
            xx, xy = get_center(positions["x"])

            z_center = (xx - pixel_width, xy)
            half_w = pixel_width / 2

            z_box = (
                z_center[0] - half_w,
                z_center[1] - half_w,
                z_center[0] + half_w,
                z_center[1] + half_w,
            )

            positions["z"] = z_box
            draw_box(image, z_box, "z")

    # ── Display Annotated Image ────────────────────────────────────────────────
    cv2.imshow("Keyboard Detection", image)

    # ── Scale Factor ───────────────────────────────────────────────────────────
    scale_factor = real_key_width_mm / pixel_width
    print(f"Scale factor: {scale_factor:.4f} mm per pixel\n")

    # ── Distance Measurements ──────────────────────────────────────────────────
    height, width, _ = image.shape
    ref_x = width / 2
    ref_y = height / 2
    distance_data = []

    for key in target_keys:
        if key not in positions:
            print(f"Warning: '{key}' not found or estimated.")
            continue

        x1, y1, x2, y2 = positions[key]
        key_center_x, key_center_y = get_center((x1, y1, x2, y2))

        pixel_distance = math.sqrt(
            (key_center_x - ref_x) ** 2 +
            (key_center_y - ref_y) ** 2
        )

        distance_mm = pixel_distance * scale_factor
        vertical_mm = (key_center_y - ref_y) * scale_factor
        horizontal_mm = (key_center_x - ref_x) * scale_factor

        print(f"Distance from '{refernce_key}' to '{key}': {distance_mm:.2f} mm")
        print(f"Vertical distance: {vertical_mm:.2f} mm")
        print(f"Horizontal distance: {horizontal_mm:.2f} mm\n")

        measurement = {
            "start_key": refernce_key,
            "end_key": key,
            "euclidean_dist_mm": distance_mm,
            "vertical_dist_mm": vertical_mm,
            "horizontal_dist_mm": horizontal_mm
        }

        distance_data.append(measurement)

        refernce_key = key
        ref_x, ref_y = key_center_x, key_center_y

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return distance_data

if __name__ == "__main__":
    test_path = r'/Users/joshuadayal/Documents/Python/detectron/myvenv/test.jpg'
    image = cv2.imread(test_path)
    data = DistanceData("joshua", image)
    print(data)