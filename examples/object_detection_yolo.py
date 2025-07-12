import atlas
import os
from PIL import Image

# Create a temporary directory to store the data
if not os.path.exists("examples/data/yolo/images"):
    os.makedirs("examples/data/yolo/images")
if not os.path.exists("examples/data/yolo/labels"):
    os.makedirs("examples/data/yolo/labels")

# Create a dummy image
image = Image.new("RGB", (100, 100), color="red")
image.save("examples/data/yolo/images/dummy.jpg")

# Create a dummy label file
with open("examples/data/yolo/labels/dummy.txt", "w") as f:
    f.write("0 0.5 0.5 0.5 0.5")

# Sink the YOLO dataset to a Lance dataset
atlas.sink(
    "examples/data/yolo",
    "examples/data/yolo.lance",
    options={"task": "object_detection", "format": "yolo"},
)

# Visualize some samples from the dataset
atlas.visualize("examples/data/yolo.lance", num_samples=1)
