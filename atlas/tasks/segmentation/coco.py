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
import os

import numpy as np
import pyarrow as pa
from PIL import Image, ImageDraw

from atlas.tasks.object_detection.coco import CocoDataset


class CocoSegmentationDataset(CocoDataset):
    """
    A dataset that reads data from a COCO JSON file for segmentation tasks.
    """

    def _process_batch(self, batch_image_ids, images, annotations_by_image) -> pa.RecordBatch:
        record_batch = super()._process_batch(batch_image_ids, images, annotations_by_image)

        all_masks = []
        for image_id in batch_image_ids:
            image_info = images[image_id]
            annotations = annotations_by_image.get(image_id, [])
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
            all_masks.append(masks)

        return record_batch.add_column(2, "mask", pa.array(all_masks, type=pa.list_(pa.binary())))
