import atlas
import os
import requests
import zipfile
import json
from PIL import Image

# Create a temporary directory to store the data
if not os.path.exists("examples/data/coco/images"):
    os.makedirs("examples/data/coco/images")

# Download and extract the COCO annotations
if not os.path.exists("examples/data/coco/annotations"):
    annotations_url = "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
    response = requests.get(annotations_url, stream=True)
    with open("examples/data/coco_annotations.zip", "wb") as f:
        for chunk in response.iter_content(chunk_size=128):
            f.write(chunk)

    with zipfile.ZipFile("examples/data/coco_annotations.zip", "r") as zip_ref:
        zip_ref.extractall("examples/data/coco")

# Download a single image
if not os.path.exists("examples/data/coco/images/000000289343.jpg"):
    image_url = "http://images.cocodataset.org/val2017/000000289343.jpg"
    response = requests.get(image_url, stream=True)
    with open("examples/data/coco/images/000000289343.jpg", "wb") as f:
        for chunk in response.iter_content(chunk_size=128):
            f.write(chunk)

# Create a new annotation file with only the downloaded image and its annotations
if not os.path.exists("examples/data/coco/annotations/instances_val2017_small.json"):
    with open("examples/data/coco/annotations/instances_val2017.json", "r") as f:
        data = json.load(f)

    new_data = {
        "images": [img for img in data["images"] if img["id"] == 289343],
        "annotations": [ann for ann in data["annotations"] if ann["image_id"] == 289343],
        "categories": data["categories"],
    }

    with open("examples/data/coco/annotations/instances_val2017_small.json", "w") as f:
        json.dump(new_data, f)

# Sink the COCO dataset to a Lance dataset
atlas.sink(
    "examples/data/coco/annotations/instances_val2017_small.json",
    "examples/data/coco_segmentation.lance",
    options={
        "task": "segmentation",
        "format": "coco",
        "image_root": "examples/data/coco/images",
    },
)

# Visualize some samples from the dataset
atlas.visualize("examples/data/coco_segmentation.lance", num_samples=5, output_file="examples/data/coco_segmentation_visualization.png")

# Verify that the dataset was created and is not empty
import lance
dataset = lance.dataset("examples/data/coco_segmentation.lance")
assert dataset.count_rows() == len(new_data["images"]), "The number of rows in the dataset does not match the number of images"

# Verify the contents of the dataset
table = dataset.to_table()
for i, row in enumerate(table.to_pydict()["image"]):
    image_info = new_data["images"][i]
    annotations = [ann for ann in new_data["annotations"] if ann["image_id"] == image_info["id"]]

    assert table.to_pydict()["file_name"][i] == image_info["file_name"], "File names do not match"

    assert len(table.to_pydict()["mask"][i]) > 0, "Mask is empty"

# Verify that the visualization was created
assert os.path.exists("examples/data/coco_segmentation_visualization.png"), "The visualization was not created"
