# lance_utils/tasks/object_detection/base.py
from pathlib import Path
from typing import List, Dict, Generator, Any
import pyarrow as pa
from PIL import Image
import json
from atlas.tasks.base import Task

class ObjectDetectionTask(Task):
    """
    An object detection task.
    The task is to identify the bounding boxes of objects in an image.
    The data is expected to be in COCO format.
    """

    def __init__(self, input_path: str):
        self.input_path = Path(input_path)
        self.annotations_file = self.input_path / "annotations.json"
        if not self.annotations_file.exists():
            raise FileNotFoundError(f"Annotations file not found: {self.annotations_file}")

        with open(self.annotations_file, "r") as f:
            self.coco_data = json.load(f)

        self.img_id_to_filename = {img['id']: img['file_name'] for img in self.coco_data.get('images', [])}

    @property
    def name(self) -> str:
        return "object_detection"

    @property
    def version(self) -> str:
        return "0.1.0"

    def get_schema(self) -> pa.Schema:
        return pa.schema([
            pa.field("image", pa.binary()),
            pa.field("filename", pa.string()),
            pa.field("class_label", pa.string()),
            pa.field("bounding_boxes", pa.list_(pa.struct([
                pa.field("bbox", pa.list_(pa.float32(), 4)),
                pa.field("category_id", pa.int64())
            ]))),
            pa.field("masks", pa.list_(pa.binary()))
        ])

    def yield_data(self) -> Generator[Dict[str, Any], None, None]:
        for img_id, filename in self.img_id_to_filename.items():
            image_path = self.input_path / "PNGImages" / filename
            if not image_path.exists():
                continue

            with open(image_path, "rb") as f:
                image_bytes = f.read()

            annotations = [ann for ann in self.coco_data.get('annotations', []) if ann['image_id'] == img_id]
            bounding_boxes = []
            for ann in annotations:
                if 'bbox' in ann:
                    bounding_boxes.append({
                        "bbox": ann['bbox'],
                        "category_id": ann['category_id']
                    })

            mask_path = self.input_path / "PedMasks" / f"{Path(filename).stem}_mask.png"
            masks = []
            if mask_path.exists():
                with open(mask_path, "rb") as f:
                    masks.append(f.read())

            yield {
                "image": image_bytes,
                "filename": filename,
                "class_label": "PedMasks",
                "bounding_boxes": bounding_boxes,
                "masks": masks
            }
