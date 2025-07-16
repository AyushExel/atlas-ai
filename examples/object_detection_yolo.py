import atlas
import os
import requests
import zipfile
import numpy as np

# URL of the dataset to download
DATASET_URL = "https://github.com/ultralytics/assets/releases/download/v0.0.0/coco128.zip"

# Create a temporary directory to store the data
data_dir = "examples/data/yolo"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Download and extract the dataset
if DATASET_URL:
    response = requests.get(DATASET_URL)
    zip_path = os.path.join(data_dir, "dataset.zip")
    with open(zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(data_dir)

    os.remove(zip_path)

# Sink the YOLO dataset to a Lance dataset
atlas.sink(
    data_dir,
    "examples/data/yolo.lance",
    options={"task": "object_detection", "format": "yolo"},
)

# Visualize some samples from the dataset
atlas.visualize("examples/data/yolo.lance", num_samples=5, output_file="examples/data/yolo_visualization.png")

# Verify that the dataset was created and is not empty
import lance
dataset = lance.dataset("examples/data/yolo.lance")
image_dir = os.path.join(data_dir, "coco128", "images", "train2017")
assert dataset.count_rows() == len(os.listdir(image_dir)), "The number of rows in the dataset does not match the number of images"

# Verify the contents of the dataset
table = dataset.to_table()
for i, row in enumerate(table.to_pydict()["image"]):
    file_name = table.to_pydict()["file_name"][i]
    label_path = os.path.join(data_dir, "coco128", "labels", "train2017", os.path.splitext(file_name)[0] + ".txt")
    if not os.path.exists(label_path):
        continue
    with open(label_path, "r") as f:
        lines = f.readlines()

    for j, line in enumerate(lines):
        parts = line.strip().split()
        class_id = int(parts[0])
        x_center, y_center, width, height = map(float, parts[1:])

        assert table.to_pydict()["label"][i][j] == class_id, "Labels do not match"

        bbox = table.to_pydict()["bbox"][i][j]
        assert np.allclose(bbox, [x_center, y_center, width, height], atol=1e-2), "Bounding boxes do not match"


# Verify that the visualization was created
assert os.path.exists("examples/data/yolo_visualization.png"), "The visualization was not created"
