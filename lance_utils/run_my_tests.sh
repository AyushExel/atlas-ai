#!/bin/bash

set -e

echo "--- Setting up virtual environment ---"
python3 -m venv .venv
source .venv/bin/activate

echo "--- Installing dependencies ---"
pip install . pyyaml psutil

echo "--- Cleaning up previous run ---"
rm -rf dummy_data *.lance

echo "--- Creating dummy data ---"
python3 create_dummy_images.py

# Create dummy annotations file
cat << EOF > dummy_data/my_complex_dataset/annotations.json
{
    "images": [
        {"id": 1, "file_name": "1.png"},
        {"id": 2, "file_name": "2.png"},
        {"id": 3, "file_name": "3.png"}
    ],
    "annotations": [
        {"image_id": 1, "bbox": [10, 10, 50, 50], "category_id": 1},
        {"image_id": 2, "bbox": [20, 20, 60, 60], "category_id": 1},
        {"image_id": 3, "bbox": [30, 30, 70, 70], "category_id": 1}
    ]
}
EOF

echo "Dummy data created."
echo ""

mkdir -p outputs

# --- Run Tests ---

echo "--- Testing object detection task ---"
atlas build -i dummy_data/my_complex_dataset -o outputs/object_detection.lance
atlas inspect -i outputs/object_detection.lance
echo "--> Note: Schema should contain image, filename, class_label, bounding_boxes, and masks."
echo ""

echo "--- All tests passed successfully! ---"
