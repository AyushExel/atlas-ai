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

import os
import pyarrow as pa

from atlas.tasks.data_model.coco_base import CocoBaseDataset


class CocoDataset(CocoBaseDataset):
    """
    A dataset that reads data from a COCO JSON file for object detection tasks.
    """

    def _process_batch(self, batch_image_ids, images, annotations_by_image) -> pa.RecordBatch:
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
            labels = [ann["category_id"] for ann in annotations]

            all_bboxes.append(bboxes)
            all_labels.append(labels)
            heights.append(image_info.get("height", 0))
            widths.append(image_info.get("width", 0))
            file_names.append(image_info.get("file_name", ""))

        batch = pa.RecordBatch.from_arrays(
            [
                pa.array(images_data, type=pa.binary()),
                pa.array(all_bboxes, type=pa.list_(pa.list_(pa.float32()))),
                pa.array(all_labels, type=pa.list_(pa.int64())),
                pa.array(heights, type=pa.int64()),
                pa.array(widths, type=pa.int64()),
                pa.array(file_names, type=pa.string()),
            ],
            names=["image", "bbox", "label", "height", "width", "file_name"],
        )
        return batch
