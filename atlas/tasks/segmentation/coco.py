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

import io
import json
import os
from typing import Generator

import numpy as np
import pyarrow as pa
from PIL import Image, ImageDraw

from atlas.tasks.data_model.base import BaseDataset


class CocoSegmentationDataset(BaseDataset):
    """
    A dataset that reads data from a COCO JSON file for segmentation tasks.
    """

    def __init__(self, data: str, **kwargs):
        super().__init__(data)
        self.image_root = kwargs.get("image_root")
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
        for ann in coco_data["annotations"]:
            annotations_by_image.setdefault(ann["image_id"], []).append(ann)
        if "categories" in coco_data:
            self.metadata.class_names = {cat["id"]: cat["name"] for cat in coco_data["categories"]}

        image_ids = list(images.keys())

        for i in range(0, len(image_ids), batch_size):
            batch_image_ids = image_ids[i : i + batch_size]

            images_data = []
            all_bboxes = []
            all_masks = []
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
                labels = [ann["category_id"] for ann in annotations]
                masks = []
                for ann in annotations:
                    mask = np.zeros(
                        (image_info["height"], image_info["width"]), dtype=np.uint8
                    )
                    if isinstance(ann["segmentation"], list):
                        for seg in ann["segmentation"]:
                            poly = np.array(seg).reshape((len(seg) // 2, 2))
                            img = Image.new(
                                "L", (image_info["width"], image_info["height"]), 0
                            )
                            ImageDraw.Draw(img).polygon(
                                tuple(map(tuple, poly)), outline=1, fill=1
                            )
                            mask = np.maximum(mask, np.array(img))
                    else:
                        from pycocotools import mask as mask_utils
                        rle = mask_utils.frPyObjects(
                            ann["segmentation"],
                            image_info["height"],
                            image_info["width"],
                        )
                        mask = np.maximum(mask, mask_utils.decode(rle))
                    img = Image.fromarray(mask * 255)  # scale mask to 0-255
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    masks.append(buf.getvalue())

                all_bboxes.append(bboxes)
                all_masks.append(masks)
                all_labels.append(labels)
                heights.append(image_info["height"])
                widths.append(image_info["width"])
                file_names.append(image_info["file_name"])

            batch = pa.RecordBatch.from_arrays(
                [
                    pa.array(images_data, type=pa.binary()),
                    pa.array(all_bboxes, type=pa.list_(pa.list_(pa.float32()))),
                    pa.array(all_masks, type=pa.list_(pa.binary())),
                    pa.array(all_labels, type=pa.list_(pa.int64())),
                    pa.array(heights, type=pa.int64()),
                    pa.array(widths, type=pa.int64()),
                    pa.array(file_names, type=pa.string()),
                ],
                names=[
                    "image",
                    "bbox",
                    "mask",
                    "label",
                    "height",
                    "width",
                    "file_name",
                ],
            )
            yield batch
