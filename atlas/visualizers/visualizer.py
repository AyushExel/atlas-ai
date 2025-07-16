# Atlas: A data-centric AI framework
#
# Copyright (c) 2024-present, Atlas Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
import io
import math
import numpy as np

import lance
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from atlas.tasks.data_model.base import BaseDataset


def visualize(uri: str, num_samples: int = 5, output_file: str = None):
    """
    Visualizes a few random samples from a Lance dataset.

    This function is useful for quickly inspecting the contents of a Lance dataset,
    especially for datasets that contain images and other visual data. It can
    display images, draw bounding boxes, and show segmentation masks.

    Args:
        uri (str): The URI of the Lance dataset to visualize.
        num_samples (int, optional): The number of samples to visualize.
            Defaults to 5.
        output_file (str, optional): The path to save the visualization.
    """
    dataset = lance.dataset(uri)
    total_rows = dataset.count_rows()

    if total_rows == 0:
        print("Dataset is empty.")
        return

    sample_indices = random.sample(range(total_rows), min(num_samples, total_rows))
    samples = dataset.take(sample_indices).to_pydict()
    metadata = BaseDataset.get_metadata(uri)
    if metadata:
        samples["class_names"] = metadata.class_names

    if num_samples > total_rows:
        num_samples = total_rows

    num_cols = 3
    num_rows = math.ceil(num_samples / num_cols)
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))
    axes = axes.flatten()

    for i, ax in enumerate(axes):
        if i >= len(sample_indices):
            ax.axis("off")
            continue

        row = {key: value[i] for key, value in samples.items() if key != "class_names"}
        if "image" in row:
            try:
                image = Image.open(io.BytesIO(row["image"]))
                ax.imshow(image)
                ax.axis("off")

                if "bbox" in row and "label" in row:
                    bboxes = row["bbox"]
                    labels = row["label"]
                    if not isinstance(labels, list):
                        labels = [labels]
                    if bboxes and not isinstance(bboxes[0], list):
                        bboxes = [bboxes]
                    for bbox, label in zip(bboxes, labels):
                        x_center, y_center, width, height = bbox
                        x_min = x_center - width / 2
                        y_min = y_center - height / 2
                        rect = patches.Rectangle(
                            (x_min, y_min),
                            width,
                            height,
                            linewidth=1,
                            edgecolor="r",
                            facecolor="none",
                        )
                        ax.add_patch(rect)
                        if "class_names" in samples:
                            class_names = samples["class_names"]
                            if class_names:
                                class_name = class_names.get(str(label), str(label))
                                ax.text(
                                    x_min,
                                    y_min - 2,
                                    class_name,
                                    bbox=dict(facecolor="red", alpha=0.5),
                                    fontsize=8,
                                    color="white",
                                )

                if "mask" in row:
                    masks = row["mask"]
                    for idx, mask_bytes in enumerate(masks):
                        mask_image = Image.open(io.BytesIO(mask_bytes)).convert("L")
                        mask_np = np.array(mask_image)
                        # Generate a random color for each mask
                        color = np.random.randint(0, 255, size=3)
                        rgba_mask = np.zeros((*mask_np.shape, 4), dtype=np.uint8)
                        rgba_mask[mask_np > 0, :3] = color  # Set color where mask is present
                        rgba_mask[mask_np > 0, 3] = 130     # Set alpha (transparency)
                        ax.imshow(rgba_mask)

            except Exception as e:
                print(f"Could not display image: {e}")
        else:
            ax.text(0.5, 0.5, str(row), ha="center", va="center")
            ax.axis("off")

    plt.tight_layout()
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()
