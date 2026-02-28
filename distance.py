import cv2
from ultralytics import YOLO
import math

# ── Constants ──────────────────────────────────────────────────────────────────
real_key_width_mm = 15.0        # Physical width of a keyboard key in millimetres
input_string = "joshua"         # The string whose keys we want to locate and measure
print("Input string:", input_string)

target_keys = list(input_string) # Individual characters to detect
refernce_key = "1"               # The reference key used as the origin for distance measurements
positions = {}                   # Dictionary mapping key labels to their bounding boxes (x1,y1,x2,y2)

# ── Model & Image Setup ────────────────────────────────────────────────────────
model = YOLO(r'best.pt')         # Load custom-trained YOLO model for keyboard key detection
image = cv2.imread(r'/Users/joshuadayal/Documents/Python/detectron/myvenv/test.jpg')

if image is None:
    raise FileNotFoundError("Could not load 'test.jpg'. Check the file path.")

# Run inference with 50% confidence threshold
results = model.predict(image, conf=0.5, verbose=False, show=False)

pixel_width = None        # Width of the reference key '1' in pixels (used for scale + estimated boxes)
reference_center = None   # Center coordinates of the reference key '1'


# ── Helper Functions ───────────────────────────────────────────────────────────

def draw_box(image, box, label, conf=-1):
    """
    Draws a bounding box and label on the image.

    Args:
        image:  The image array to draw on (modified in place).
        box:    Bounding box as (x1, y1, x2, y2).
        label:  Text label to display above the box.
        conf:   Confidence score (unused visually, reserved for future use).
    """
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(image, f'{label}', (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def get_center(box):
    """
    Computes the center point of a bounding box.

    Args:
        box: Bounding box as (x1, y1, x2, y2).

    Returns:
        Tuple (cx, cy) representing the center coordinates.
    """
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


# ── Detection Loop ─────────────────────────────────────────────────────────────
for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        cls_name = model.names[cls]

        # Store bounding box for every detected key
        positions[cls_name] = (x1, y1, x2, y2)

        # Draw box for target keys, skipping 'y' and 'z' (estimated separately below)
        if cls_name in target_keys and cls_name != "z" and cls_name != "y":
            draw_box(image, (x1, y1, x2, y2), cls_name, conf)

        # Use key '1' as the reference for scale and origin
        if cls_name == "1":
            pixel_width = x2 - x1
            reference_center = get_center((x1, y1, x2, y2))


if pixel_width is None or reference_center is None:
    raise ValueError("Reference key '1' not detected. Cannot compute scale.")


# ── Estimate 'y' Position ──────────────────────────────────────────────────────
# 'y' is not directly detected, so its position is estimated as the midpoint
# between the 't' and 'u' keys, which flank it on a standard QWERTY keyboard.
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


# ── Estimate 'z' Position ──────────────────────────────────────────────────────
# 'z' is estimated as one key-width to the left of 'x' on a standard QWERTY keyboard.
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


# ── Display Annotated Image ────────────────────────────────────────────────────
cv2.imshow("Keyboard Detection", image)

# ── Scale Factor ───────────────────────────────────────────────────────────────
# Converts pixel distances to real-world millimetres using the known key width
scale_factor = real_key_width_mm / pixel_width
print(f"Scale factor: {scale_factor:.4f} mm per pixel\n")

# ── Distance Measurements ──────────────────────────────────────────────────────
# Iterates through each character in the input string, measuring the distance
# from the previous key to the current one (chained, not all from '1').
ref_x, ref_y = reference_center

for key in target_keys:
    if key not in positions:
        print(f"Warning: '{key}' not found or estimated.")
        continue

    x1, y1, x2, y2 = positions[key]
    key_center_x, key_center_y = get_center((x1, y1, x2, y2))

    # Euclidean distance in pixels, converted to mm
    pixel_distance = math.sqrt(
        (key_center_x - ref_x) ** 2 +
        (key_center_y - ref_y) ** 2
    )
    distance_mm = pixel_distance * scale_factor

    print(f"Distance from '{refernce_key}' to '{key}': {distance_mm:.2f} mm")
    print(f"Vertical distance: {(key_center_y - ref_y) * scale_factor:.2f} mm")
    print(f"Horizontal distance: {(key_center_x - ref_x) * scale_factor:.2f} mm\n")

    # Update reference to current key for next iteration (chained distances)
    refernce_key = key
    ref_x, ref_y = key_center_x, key_center_y

cv2.waitKey(0)
cv2.destroyAllWindows()