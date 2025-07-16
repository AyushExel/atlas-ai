import atlas
import os
import requests
import zipfile

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
atlas.visualize("examples/data/yolo.lance", num_samples=1, output_file="examples/data/yolo_visualization.png")

# Verify that the dataset was created and is not empty
import lance
dataset = lance.dataset("examples/data/yolo.lance")
assert dataset.count_rows() > 0, "The dataset is empty"

# Verify that the visualization was created
assert os.path.exists("examples/data/yolo_visualization.png"), "The visualization was not created"
