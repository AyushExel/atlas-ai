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

import json
from typing import Generator

import pyarrow as pa
from PIL import Image
import numpy as np

from atlas.tasks.data_model.base import BaseDataset


import os

class CocoSegmentationDataset(BaseDataset):
    """
    A dataset that reads data from a COCO JSON file for segmentation tasks.
    """
    def __init__(self, data: str, options: dict = None):
        super().__init__(data)
        self.options = options or {}
        self.image_root = self.options.get("image_root")

    def to_batches(self, batch_size: int = 1024) -> Generator[pa.RecordBatch, None, None]:
        """
        Yields batches of the dataset as Arrow RecordBatches.
        """
        with open(self.data, "r") as f:
            coco_data = json.load(f)

        images = {image["id"]: image for image in coco_data["images"]}
        annotations = coco_data["annotations"]

        for i in range(0, len(annotations), batch_size):
            batch_annotations = annotations[i : i + batch_size]

            images_data = []
            bboxes = []
            masks = []
            labels = []

            for ann in batch_annotations:
                image_id = ann["image_id"]
                image_info = images[image_id]
                image_path = os.path.join(self.image_root, image_info["file_name"]) if self.image_root else image_info["file_name"]
                with open(image_path, "rb") as f:
                    images_data.append(f.read())

                bboxes.append(ann["bbox"])

                # Create a mask from the segmentation data
                mask = np.zeros((image_info['height'], image_info['width']), dtype=np.uint8)
                for seg in ann['segmentation']:
                    poly = np.array(seg).reshape((len(seg)//2, 2))
                    # This is a simplified mask creation, for polygons only.
                    # For a more robust solution, consider using a library like pycocotools.
                    from PIL import ImageDraw
                    img = Image.new('L', (image_info['width'], image_info['height']), 0)
                    ImageDraw.Draw(img).polygon(tuple(map(tuple, poly)), outline=1, fill=1)
                    mask = np.maximum(mask, np.array(img))

                masks.append(mask.tobytes())
                labels.append(ann["category_id"])

            batch = pa.RecordBatch.from_arrays(
                [
                    pa.array(images_data, type=pa.binary()),
                    pa.array(bboxes, type=pa.list_(pa.float32())),
                    pa.array(masks, type=pa.binary()),
                    pa.array(labels, type=pa.int64()),
                ],
                names=["image", "bbox", "mask", "label"],
            )
            yield batch
