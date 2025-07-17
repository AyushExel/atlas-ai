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
        if self.image_root is None:
            self.image_root = self._infer_image_root()

    def _infer_image_root(self) -> str:
        """
        Infers the image root directory from the annotation file path.
        """
        # Check for common image directory names relative to the annotation file
        annotation_dir = os.path.dirname(os.path.dirname(self.data))
        common_image_dirs = ["images", "train2017", "val2017", "test2017"]
        for dir_name in common_image_dirs:
            image_dir = os.path.join(annotation_dir, dir_name)
            if os.path.isdir(image_dir):
                return image_dir
        return annotation_dir

    def to_batches(self, batch_size: int = 1024, **kwargs) -> Generator[pa.RecordBatch, None, None]:
        """
        Yields batches of the dataset as Arrow RecordBatches.
        """
        with open(self.data, "r") as f:
            coco_data = json.load(f)

        images = {image["id"]: image for image in coco_data["images"]}
        annotations_by_image = {}
        for ann in coco_data.get("annotations", []):
            annotations_by_image.setdefault(ann["image_id"], []).append(ann)

        captions_by_image = {}
        if "captions" in coco_data:
            for cap in coco_data["captions"]:
                captions_by_image.setdefault(cap["image_id"], []).append(cap["caption"])

        if "categories" in coco_data:
            self.metadata.class_names = {cat["id"]: cat["name"] for cat in coco_data["categories"]}

        image_ids = list(images.keys())

        for i in range(0, len(image_ids), batch_size):
            batch_image_ids = image_ids[i : i + batch_size]

            images_data = []
            all_bboxes = []
            all_labels = []
            all_keypoints = []
            all_captions = []
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
                bboxes = [ann.get("bbox") for ann in annotations]
                labels = [ann.get("category_id") for ann in annotations]
                keypoints = [ann.get("keypoints") for ann in annotations]

                all_bboxes.append(bboxes)
                all_labels.append(labels)
                all_keypoints.append(keypoints)
                all_captions.append(captions_by_image.get(image_id, []))
                heights.append(image_info.get("height", 0))
                widths.append(image_info.get("width", 0))
                file_names.append(image_info.get("file_name", ""))

            batch = pa.RecordBatch.from_arrays(
                [
                    pa.array(images_data, type=pa.binary()),
                    pa.array(all_bboxes, type=pa.list_(pa.list_(pa.float32()))),
                    pa.array(all_labels, type=pa.list_(pa.int64())),
                    pa.array(all_keypoints, type=pa.list_(pa.list_(pa.float32()))),
                    pa.array(all_captions, type=pa.list_(pa.string())),
                    pa.array(heights, type=pa.int64()),
                    pa.array(widths, type=pa.int64()),
                    pa.array(file_names, type=pa.string()),
                ],
                names=[
                    "image",
                    "bbox",
                    "label",
                    "keypoints",
                    "captions",
                    "height",
                    "width",
                    "file_name",
                ],
            )
            yield batch

    @property
    def schema(self) -> pa.Schema:
        """
        Returns the schema of the dataset.
        """
        return pa.schema(
            [
                pa.field("image", pa.binary()),
                pa.field("bbox", pa.list_(pa.list_(pa.float32()))),
                pa.field("label", pa.list_(pa.int64())),
                pa.field("keypoints", pa.list_(pa.list_(pa.float32()))),
                pa.field("captions", pa.list_(pa.string())),
                pa.field("height", pa.int64()),
                pa.field("width", pa.int64()),
                pa.field("file_name", pa.string()),
            ]
        )

