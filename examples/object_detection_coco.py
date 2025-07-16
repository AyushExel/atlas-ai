import atlas
import os
import requests
import zipfile
import json
from PIL import Image
import numpy as np

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

# Create a new annotation file with the first N images and their annotations if not already present
instances_json_path = "examples/data/coco/annotations/instances_val2017.json"
small_json_path = "examples/data/coco/annotations/instances_val2017_small.json"
N = 10  # Number of images to include

with open(instances_json_path, "r") as f:
    data = json.load(f)

image_infos = data["images"][:N]
image_ids = [img["id"] for img in image_infos]

new_data = {
    "images": [img for img in data["images"] if img["id"] in image_ids],
    "annotations": [ann for ann in data["annotations"] if ann["image_id"] in image_ids],
    "categories": data["categories"],
}

with open(small_json_path, "w") as f:
    json.dump(new_data, f)


# Download all images referenced in the filtered annotation file if not already present
with open(small_json_path, "r") as f:
    filtered_data = json.load(f)

for img in filtered_data["images"]:
    file_name = img["file_name"]
    image_path = f"examples/data/coco/images/{file_name}"
    image_url = f"http://images.cocodataset.org/val2017/{file_name}"
    if not os.path.exists(image_path):
        response = requests.get(image_url, stream=True)
        with open(image_path, "wb") as f_img:
            for chunk in response.iter_content(chunk_size=128):
                f_img.write(chunk)
    else:
        print(f"{image_path} already exists, skipping download.")

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
atlas.visualize("examples/data/coco.lance", num_samples=5, output_file="examples/data/coco_visualization.png")

# Verify that the dataset was created and is not empty
import lance
dataset = lance.dataset("examples/data/coco.lance")
assert dataset.count_rows() == len(new_data["images"]), "The number of rows in the dataset does not match the number of images"

# Verify the contents of the dataset
table = dataset.to_table()
for i, row in enumerate(table.to_pydict()["image"]):
    image_info = new_data["images"][i]
    annotations = [ann for ann in new_data["annotations"] if ann["image_id"] == image_info["id"]]

    assert table.to_pydict()["file_name"][i] == image_info["file_name"], "File names do not match"

    for j, bbox in enumerate(table.to_pydict()["bbox"][i]):
        print(f" {bbox} {annotations[j]['bbox']}")
        assert np.allclose(bbox, annotations[j]["bbox"], atol=1e-2), "Bounding boxes do not match"

    for j, label in enumerate(table.to_pydict()["label"][i]):
        assert label == annotations[j]["category_id"], "Labels do not match"

# Verify that the visualization was created
assert os.path.exists("examples/data/coco_visualization.png"), "The visualization was not created"
