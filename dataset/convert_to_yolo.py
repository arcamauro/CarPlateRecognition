import json
import os
from pathlib import Path
from PIL import Image
from tqdm import tqdm

# Define paths
DATASET_DIR = Path('dataset')
IMAGES_DIR = DATASET_DIR / 'images'
LABELS_DIR = DATASET_DIR / 'labels'

# Create label directories if they don't exist
for subset in ['train', 'test']:
    (LABELS_DIR / subset).mkdir(parents=True, exist_ok=True)

# Define class mapping
CLASS_MAPPING = {
    'SINGLE': 0,
    'DOUBLE': 1  # Extend this if there are more types
}

def convert_polygon_to_bbox(points):
    """
    Convert polygon points to axis-aligned bounding box.

    Args:
        points (list): List of [x, y] coordinates.

    Returns:
        tuple: (x_min, y_min, x_max, y_max)
    """
    x_coordinates = [point[0] for point in points]
    y_coordinates = [point[1] for point in points]
    x_min = min(x_coordinates)
    y_min = min(y_coordinates)
    x_max = max(x_coordinates)
    y_max = max(y_coordinates)
    return x_min, y_min, x_max, y_max

def process_label_file(label_file, subset):
    """
    Process a single JSON label file and convert annotations to YOLOv5 format.

    Args:
        label_file (Path): Path to the JSON label file.
        subset (str): Dataset subset ('train', 'test').
    """
    print(f"Processing file: {label_file}")  # Debugging line
    try:
        with open(label_file, 'r', encoding='utf-8') as f:
            # Replace 'NaN' with 'null' to handle invalid JSON
            content = f.read().replace('NaN', 'null')
            data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {label_file}: {e}")
        return  # Skip this file and continue
    except Exception as e:
        print(f"Unexpected error reading file {label_file}: {e}")
        return

    if not data:
        print(f"Warning: The file {label_file} is empty.")
        return

    for image_path, annotations in tqdm(data.items(), desc=f"Processing {subset}"):
        # Extract the image filename without any subdirectories
        image_filename = Path(image_path).name
        image_full_path = IMAGES_DIR / subset / image_filename

        if not image_full_path.exists():
            print(f"Image {image_full_path} does not exist. Skipping.")
            continue

        # Open image to get dimensions
        try:
            with Image.open(image_full_path) as img:
                img_width, img_height = img.size
        except Exception as img_err:
            print(f"Error opening image {image_full_path}: {img_err}")
            continue

        # Prepare the corresponding YOLO label file
        label_txt_path = LABELS_DIR / subset / (Path(image_filename).stem + '.txt')
        with open(label_txt_path, 'w', encoding='utf-8') as label_file_handle:
            for annot in annotations:
                # Handle cases where 'text' might be null
                if not annot.get('text'):
                    continue  # Skip annotations without text

                obj_type = annot.get('type')
                class_id = CLASS_MAPPING.get(obj_type, -1)
                if class_id == -1:
                    print(f"Unknown object type '{obj_type}' in {image_filename}. Skipping annotation.")
                    continue

                points = annot.get('points')
                if not points or len(points) < 4:
                    print(f"Invalid points for image {image_filename}. Skipping annotation.")
                    continue

                # Convert polygon to bounding box
                x_min, y_min, x_max, y_max = convert_polygon_to_bbox(points)

                # Compute YOLO format values
                x_center = (x_min + x_max) / 2.0
                y_center = (y_min + y_max) / 2.0
                width = x_max - x_min
                height = y_max - y_min

                # Normalize coordinates
                x_center /= img_width
                y_center /= img_height
                width /= img_width
                height /= img_height

                # Validate normalized coordinates
                if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and 0 <= width <= 1 and 0 <= height <= 1):
                    print(f"Normalized coordinates out of bounds for image {image_filename}. Skipping annotation.")
                    continue

                # Write to label file
                label_file_handle.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

def main():
    """
    Main function to process all label files for train and test subsets.
    """
    subsets = {
        'train': 'trn_labels.json',
        'test': 'tst_labels.json',
    }

    for subset, label_file_name in subsets.items():
        label_json_path = DATASET_DIR / 'labels' / subset / label_file_name
        if not label_json_path.exists():
            print(f"Label file {label_json_path} does not exist. Skipping {subset} subset.")
            continue

        print(f"Processing {subset} subset...")
        process_label_file(label_json_path, subset)
        print(f"Finished processing {subset} subset.")

if __name__ == "__main__":
    main()