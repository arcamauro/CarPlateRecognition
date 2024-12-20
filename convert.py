import json
import os
from PIL import Image

# Load the JSON annotations
with open(r'C:\Users\danil\Desktop\Universita\prova\cog_lp_dataset_small\tst_labels.json', 'r') as f:
    annotations = json.load(f)

def convert_to_yolo(points, image_width, image_height):
    # Calculate the bounding box
    x_min = min(point[0] for point in points)
    x_max = max(point[0] for point in points)
    y_min = min(point[1] for point in points)
    y_max = max(point[1] for point in points)

    # Calculate YOLO format values
    x_center = (x_min + x_max) / 2.0 / image_width
    y_center = (y_min + y_max) / 2.0 / image_height
    width = (x_max - x_min) / image_width
    height = (y_max - y_min) / image_height

    return x_center, y_center, width, height

# Directory to save YOLO annotations
os.makedirs(r'C:\Users\danil\Desktop\Universita\prova\cog_lp_dataset_small\yolo\validation', exist_ok=True)

# Convert each annotation
file_counter = 0
for filename, objects in annotations.items():
    # Open the corresponding image to get its dimensions
    image_path = os.path.join(r'C:\Users\danil\Desktop\Universita\prova\yolov5\data\images\validation', f"{file_counter:04}.jpg")
    with Image.open(image_path) as img:
        image_width, image_height = img.size

    yolo_lines = []
    for obj in objects:
        x_center, y_center, width, height = convert_to_yolo(obj['points'], image_width, image_height)
        # Assuming 'SINGLE' is class 0 and 'DOUBLE' is class 1
        class_id = 0 if obj['type'] == 'SINGLE' else 1
        yolo_lines.append(f"{class_id} {x_center} {y_center} {width} {height}")

    # Save to a .txt file with a sequential number
    yolo_filename = f"{file_counter:04}.txt"
    with open(os.path.join(r'C:\Users\danil\Desktop\Universita\prova\cog_lp_dataset_small\yolo\validation', yolo_filename), 'w') as f:
        f.write("\n".join(yolo_lines))
    
    file_counter += 1