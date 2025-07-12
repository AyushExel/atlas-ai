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
from typing import Generator

import pyarrow as pa

from atlas.tasks.data_model.base import BaseDataset


class YoloDataset(BaseDataset):
    """
    A dataset that reads data from a YOLO detection file.
    """
    def __init__(self, data: str, options: dict = None):
        super().__init__(data)
        self.options = options or {}

    def to_batches(self, batch_size: int = 1024) -> Generator[pa.RecordBatch, None, None]:
        """
        Yields batches of the dataset as Arrow RecordBatches.
        """
        image_files = []
        label_files = []
        for file in sorted(os.listdir(self.data)):
            if file.endswith((".jpg", ".png", ".jpeg")):
                image_files.append(os.path.join(self.data, file))
            elif file.endswith(".txt"):
                label_files.append(os.path.join(self.data, file))

        for i in range(0, len(image_files), batch_size):
            batch_image_files = image_files[i : i + batch_size]

            images_data = []
            bboxes = []
            labels = []

            for image_path in batch_image_files:
                with open(image_path, "rb") as f:
                    images_data.append(f.read())

                label_path = os.path.splitext(image_path)[0] + ".txt"
                if label_path in label_files:
                    with open(label_path, "r") as f:
                        for line in f:
                            parts = line.strip().split()
                            class_id = int(parts[0])
                            x_center, y_center, width, height = map(float, parts[1:])

                            bboxes.append([round(x, 6) for x in [x_center, y_center, width, height]])
                            labels.append(class_id)

            batch = pa.RecordBatch.from_arrays(
                [
                    pa.array(images_data, type=pa.binary()),
                    pa.array(bboxes, type=pa.list_(pa.float32())),
                    pa.array(labels, type=pa.int64()),
                ],
                names=["image", "bbox", "label"],
            )
            yield batch
