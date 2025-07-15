import atlas
import os
import requests
import zipfile
import json
from PIL import Image

# Create a temporary directory to store the data
if not os.path.exists("examples/data/coco/images"):
    os.makedirs("examples/data/coco/images")

# Download and extract the COCO annotations if not already present
annotations_zip_path = "examples/data/coco_annotations.zip"
annotations_dir = "examples/data/coco/annotations"
annotations_url = "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"

if not os.path.exists(annotations_zip_path):
    response = requests.get(annotations_url, stream=True)
    with open(annotations_zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=128):
            f.write(chunk)
else:
    print(f"{annotations_zip_path} already exists, skipping download.")

if not os.path.exists(annotations_dir):
    with zipfile.ZipFile(annotations_zip_path, "r") as zip_ref:
        zip_ref.extractall("examples/data/coco")
else:
    print(f"{annotations_dir} already exists, skipping extraction.")

# Download a single image if not already present
image_path = "examples/data/coco/images/000000289343.jpg"
image_url = "http://images.cocodataset.org/val2017/000000289343.jpg"

if not os.path.exists(image_path):
    response = requests.get(image_url, stream=True)
    with open(image_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=128):
            f.write(chunk)
else:
    print(f"{image_path} already exists, skipping download.")

# Create a new annotation file with only the downloaded image and its annotations if not already present
instances_json_path = "examples/data/coco/annotations/instances_val2017.json"
small_json_path = "examples/data/coco/annotations/instances_val2017_small.json"

if not os.path.exists(small_json_path):
    with open(instances_json_path, "r") as f:
        data = json.load(f)

    new_data = {
        "images": [img for img in data["images"] if img["id"] == 289343],
        "annotations": [ann for ann in data["annotations"] if ann["image_id"] == 289343],
        "categories": data["categories"],
    }

    with open(small_json_path, "w") as f:
        json.dump(new_data, f)
else:
    print(f"{small_json_path} already exists, skipping creation.")

# Sink the COCO dataset to a Lance dataset
atlas.sink(
    small_json_path,
    "examples/data/coco.lance",
    mode="overwrite",
    options={
        "task": "object_detection",
        "format": "coco",
        "image_root": "examples/data/coco/images",
    },
)

# Visualize some samples from the dataset
atlas.visualize("examples/data/coco.lance", num_samples=1, output_file="examples/data/coco_visualization.png")
