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
from PIL import Image
import yaml

import pyarrow as pa

from atlas.tasks.data_model.base import BaseDataset


class YoloDataset(BaseDataset):
    """
    A dataset that reads data from a YOLO detection file.
    """

    def __init__(self, data: str, options: dict = None):
        super().__init__(data)
        self.options = options or {}

    def _load_yolo_metadata(self, max_class_id: int = 0):
        """
        Loads the class names from the data.yaml file.
        If not found, it will generate a default mapping.
        """
        data_yaml_path = os.path.join(self.data, "data.yaml")
        if os.path.exists(data_yaml_path):
            with open(data_yaml_path, "r") as f:
                data_yaml = yaml.safe_load(f)
                if "names" in data_yaml:
                    self.metadata.class_names = {
                        i: name for i, name in enumerate(data_yaml["names"])
                    }
                    return

        # If no class names are found, generate default ones
        if not self.metadata.class_names:
            num_classes = max_class_id + 1
            self.metadata.class_names = {i: str(i) for i in range(num_classes)}

    def to_batches(
        self, batch_size: int = 1024
    ) -> Generator[pa.RecordBatch, None, None]:
        """
        Yields batches of the dataset as Arrow RecordBatches.
        """
        # The coco128 dataset has a subdirectory with the same name.
        data_dir = os.path.join(self.data, "coco128")
        if not os.path.exists(data_dir):
            data_dir = self.data

        image_dir = os.path.join(data_dir, "images", "train2017")
        label_dir = os.path.join(data_dir, "labels", "train2017")

        image_files = []
        for file in sorted(os.listdir(image_dir)):
            if file.endswith((".jpg", ".png", ".jpeg")):
                image_files.append(os.path.join(image_dir, file))

        label_files = []
        for file in sorted(os.listdir(label_dir)):
            if file.endswith(".txt"):
                label_files.append(os.path.join(label_dir, file))

        # First pass to determine the max_class_id
        max_class_id = 0
        for label_path in label_files:
            with open(label_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    class_id = int(parts[0])
                    if class_id > max_class_id:
                        max_class_id = class_id
        
        self._load_yolo_metadata(max_class_id)

        for i in range(0, len(image_files), batch_size):
            batch_image_files = image_files[i : i + batch_size]

            images_data = []
            all_bboxes = []
            all_labels = []
            heights = []
            widths = []
            file_names = []

            for image_path in batch_image_files:
                with open(image_path, "rb") as f:
                    img_bytes = f.read()
                    images_data.append(img_bytes)
                    img = Image.open(image_path)
                    width, height = img.size
                    widths.append(width)
                    heights.append(height)
                    file_names.append(os.path.basename(image_path))

                label_path = os.path.join(label_dir, os.path.basename(os.path.splitext(image_path)[0]) + ".txt")
                if label_path not in label_files:
                    all_bboxes.append([])
                    all_labels.append([])
                    continue

                bboxes = []
                labels = []
                with open(label_path, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        class_id = int(parts[0])
                        x_center, y_center, width, height = map(float, parts[1:])

                        bboxes.append(
                            [
                                round(x, 6)
                                for x in [x_center, y_center, width, height]
                            ]
                        )
                        labels.append(class_id)
                all_bboxes.append(bboxes)
                all_labels.append(labels)

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
            yield batch
