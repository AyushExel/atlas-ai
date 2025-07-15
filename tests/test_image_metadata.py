import os
import json
import tempfile
import unittest
import pyarrow as pa
from PIL import Image

from atlas.tasks.object_detection.coco import CocoDataset
from atlas.tasks.object_detection.yolo import YoloDataset
from atlas.tasks.segmentation.coco import CocoSegmentationDataset


class TestImageMetadata(unittest.TestCase):
    def test_coco_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # create a sample COCO JSON file
            coco_data = {
                "images": [
                    {"id": 1, "file_name": "image1.jpg", "height": 480, "width": 640},
                    {"id": 2, "file_name": "image2.jpg", "height": 480, "width": 640},
                ],
                "annotations": [
                    {"id": 1, "image_id": 1, "category_id": 1, "bbox": [10, 10, 50, 50]},
                    {"id": 2, "image_id": 2, "category_id": 2, "bbox": [20, 20, 60, 60]},
                ],
                "categories": [
                    {"id": 1, "name": "cat"},
                    {"id": 2, "name": "dog"},
                ],
            }
            with open(os.path.join(tmpdir, "coco.json"), "w") as f:
                json.dump(coco_data, f)

            # create dummy image files
            for image in coco_data["images"]:
                with open(os.path.join(tmpdir, image["file_name"]), "w") as f:
                    f.write("")

            dataset = CocoDataset(
                os.path.join(tmpdir, "coco.json"), options={"image_root": tmpdir}
            )
            for batch in dataset.to_batches():
                self.assertIn("height", batch.schema.names)
                self.assertIn("width", batch.schema.names)
                self.assertIn("file_name", batch.schema.names)
                self.assertEqual(batch["height"].to_pylist(), [480, 480])
                self.assertEqual(batch["width"].to_pylist(), [640, 640])
                self.assertEqual(batch["file_name"].to_pylist(), ["image1.jpg", "image2.jpg"])

    def test_yolo_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # create dummy image and label files
            for i in range(2):
                img = Image.new("RGB", (100, 200), color="red")
                img.save(os.path.join(tmpdir, f"image{i}.jpg"))
                with open(os.path.join(tmpdir, f"image{i}.txt"), "w") as f:
                    f.write(f"{i} 0.5 0.5 0.1 0.1")

            dataset = YoloDataset(tmpdir)
            for batch in dataset.to_batches():
                self.assertIn("height", batch.schema.names)
                self.assertIn("width", batch.schema.names)
                self.assertIn("file_name", batch.schema.names)
                self.assertEqual(batch["height"].to_pylist(), [200, 200])
                self.assertEqual(batch["width"].to_pylist(), [100, 100])
                self.assertEqual(batch["file_name"].to_pylist(), ["image0.jpg", "image1.jpg"])

    def test_coco_segmentation_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # create a sample COCO JSON file
            coco_data = {
                "images": [
                    {"id": 1, "file_name": "image1.jpg", "height": 480, "width": 640},
                    {"id": 2, "file_name": "image2.jpg", "height": 480, "width": 640},
                ],
                "annotations": [
                    {
                        "id": 1,
                        "image_id": 1,
                        "category_id": 1,
                        "bbox": [10, 10, 50, 50],
                        "segmentation": [[10, 10, 60, 10, 60, 60, 10, 60]],
                    },
                    {
                        "id": 2,
                        "image_id": 2,
                        "category_id": 2,
                        "bbox": [20, 20, 60, 60],
                        "segmentation": [[20, 20, 80, 20, 80, 80, 20, 80]],
                    },
                ],
                "categories": [
                    {"id": 1, "name": "cat"},
                    {"id": 2, "name": "dog"},
                ],
            }
            with open(os.path.join(tmpdir, "coco.json"), "w") as f:
                json.dump(coco_data, f)

            # create dummy image files
            for image in coco_data["images"]:
                with open(os.path.join(tmpdir, image["file_name"]), "w") as f:
                    f.write("")

            dataset = CocoSegmentationDataset(
                os.path.join(tmpdir, "coco.json"), options={"image_root": tmpdir}
            )
            for batch in dataset.to_batches():
                self.assertIn("height", batch.schema.names)
                self.assertIn("width", batch.schema.names)
                self.assertIn("file_name", batch.schema.names)
                self.assertEqual(batch["height"].to_pylist(), [480, 480])
                self.assertEqual(batch["width"].to_pylist(), [640, 640])
                self.assertEqual(batch["file_name"].to_pylist(), ["image1.jpg", "image2.jpg"])


if __name__ == "__main__":
    unittest.main()
