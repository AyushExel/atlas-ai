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
import os
from typing import Generator

import pyarrow as pa

from atlas.tasks.data_model.base import BaseDataset


class CocoDataset(BaseDataset):
    """
    A dataset that reads data from a COCO JSON file.
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
        annotations_by_image = {}
        for ann in coco_data["annotations"]:
            annotations_by_image.setdefault(ann["image_id"], []).append(ann)
        if "categories" in coco_data:
            self.metadata.class_names = {cat["id"]: cat["name"] for cat in coco_data["categories"]}

        image_ids = list(images.keys())

        for i in range(0, len(image_ids), batch_size):
            batch_image_ids = image_ids[i : i + batch_size]

            images_data = []
            all_bboxes = []
            all_labels = []
            heights = []
            widths = []
            file_names = []

            for image_id in batch_image_ids:
                image_info = images[image_id]
                image_path = (
                    os.path.join(self.image_root, image_info["file_name"])
                    if self.image_root
                    else image_info["file_name"]
                )
                with open(image_path, "rb") as f:
                    images_data.append(f.read())

                annotations = annotations_by_image.get(image_id, [])
                bboxes = [ann["bbox"] for ann in annotations]
                labels = [self.metadata.class_names[ann["category_id"]] for ann in annotations]

                all_bboxes.append(bboxes)
                all_labels.append(labels)
                heights.append(image_info.get("height", 0))
                widths.append(image_info.get("width", 0))
                file_names.append(image_info.get("file_name", ""))

            batch = pa.RecordBatch.from_arrays(
                [
                    pa.array(images_data, type=pa.binary()),
                    pa.array(all_bboxes, type=pa.list_(pa.list_(pa.float32()))),
                    pa.array(all_labels, type=pa.list_(pa.string())),
                    pa.array(heights, type=pa.int64()),
                    pa.array(widths, type=pa.int64()),
                    pa.array(file_names, type=pa.string()),
                ],
                names=["image", "bbox", "label", "height", "width", "file_name"],
            )
            yield batch
