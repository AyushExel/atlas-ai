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

import lance
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches


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

        row = {key: value[i] for key, value in samples.items()}
        if "image" in row:
            try:
                image = Image.open(io.BytesIO(row["image"]))
                ax.imshow(image)
                ax.axis("off")

                if "bbox" in row:
                    bboxes = row["bbox"]
                    for bbox in bboxes:
                        rect = patches.Rectangle(
                            (bbox[0], bbox[1]),
                            bbox[2],
                            bbox[3],
                            linewidth=1,
                            edgecolor="r",
                            facecolor="none",
                        )
                        ax.add_patch(rect)

                if "mask" in row:
                    masks = row["mask"]
                    for mask_bytes in masks:
                        mask_image = Image.open(io.BytesIO(mask_bytes)).convert("RGBA")
                        ax.imshow(mask_image, alpha=0.5)

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
