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

import lance
from PIL import Image, ImageDraw


def visualize(uri: str, num_samples: int = 5):
    """
    Visualizes a few random samples from a Lance dataset.

    This function is useful for quickly inspecting the contents of a Lance dataset,
    especially for datasets that contain images and other visual data. It can
    display images, draw bounding boxes, and show segmentation masks.

    Args:
        uri (str): The URI of the Lance dataset to visualize.
        num_samples (int, optional): The number of samples to visualize.
            Defaults to 5.
    """
    dataset = lance.dataset(uri)
    total_rows = dataset.count_rows()

    if total_rows == 0:
        print("Dataset is empty.")
        return

    sample_indices = random.sample(range(total_rows), min(num_samples, total_rows))
    samples = dataset.take(sample_indices).to_pydict()

    for i in range(len(sample_indices)):
        print(f"--- Sample {i+1} ---")
        row = {key: value[i] for key, value in samples.items()}
        if "image" in row:
            try:
                from io import BytesIO
                image = Image.open(BytesIO(row["image"]))
                if "bbox" in row:
                    draw = ImageDraw.Draw(image)
                    bbox = row["bbox"]
                    if isinstance(bbox[0], list): # multiple bboxes
                        for b in bbox:
                            draw.rectangle(b, outline="red", width=2)
                    else:
                        draw.rectangle(bbox, outline="red", width=2)
                image.show()
            except Exception as e:
                print(f"Could not display image: {e}")
        else:
            print(row)
