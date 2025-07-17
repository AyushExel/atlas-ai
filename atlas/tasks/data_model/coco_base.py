import json
import os
from typing import Generator

import pyarrow as pa

from atlas.tasks.data_model.base import BaseDataset


class CocoBaseDataset(BaseDataset):
    """
    A base class for datasets that read data from a COCO JSON file.
    """

    def __init__(self, data: str, options: dict = None, **kwargs):
        super().__init__(data)
        self.options = options or {}
        self.image_root = self.options.get("image_root") or kwargs.get("image_root")
        if self.image_root is None:
            self.image_root = self._infer_image_root()

    def _infer_image_root(self) -> str:
        """
        Infers the image root directory from the annotation file path.
        """
        # Check for common image directory names relative to the annotation file
        annotation_dir = os.path.dirname(self.data)
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
            yield self._process_batch(batch_image_ids, images, annotations_by_image)

    def _process_batch(self, batch_image_ids, images, annotations_by_image) -> pa.RecordBatch:
        raise NotImplementedError
