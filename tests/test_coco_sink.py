import json
import os
import unittest

import lance
import pandas as pd
import pyarrow as pa

from atlas.data_sinks import sink


class CocoSinkTest(unittest.TestCase):
    def setUp(self):
        self.coco_path = "test_coco.json"
        self.lance_path = "test_coco.lance"
        self.image_dir = "test_images"
        os.makedirs(self.image_dir, exist_ok=True)

        # Create dummy image files
        for i in range(3):
            with open(os.path.join(self.image_dir, f"image{i}.jpg"), "w") as f:
                f.write("dummy image data")

        coco_data = {
            "images": [
                {"id": 0, "file_name": os.path.join(self.image_dir, "image0.jpg")},
                {"id": 1, "file_name": os.path.join(self.image_dir, "image1.jpg")},
                {"id": 2, "file_name": os.path.join(self.image_dir, "image2.jpg")},
            ],
            "annotations": [
                {"id": 0, "image_id": 0, "category_id": 1, "bbox": [10, 20, 30, 40]},
                {"id": 1, "image_id": 1, "category_id": 2, "bbox": [50, 60, 70, 80]},
                {"id": 2, "image_id": 2, "category_id": 1, "bbox": [90, 100, 110, 120]},
            ],
            "categories": [
                {"id": 1, "name": "cat"},
                {"id": 2, "name": "dog"},
            ],
        }
        with open(self.coco_path, "w") as f:
            json.dump(coco_data, f)

    def tearDown(self):
        os.remove(self.coco_path)
        if os.path.exists(self.lance_path):
            import shutil
            shutil.rmtree(self.lance_path)
        if os.path.exists(self.image_dir):
            import shutil
            shutil.rmtree(self.image_dir)

    def test_sink_coco(self):
        sink(self.coco_path, self.lance_path, options={"task": "object_detection", "format": "coco"})
        dataset = lance.dataset(self.lance_path)
        self.assertEqual(dataset.count_rows(), 3)
        table = dataset.to_table()
        self.assertEqual(table.column_names, ["image", "bbox", "label", "keypoints", "captions", "height", "width", "file_name"])

        images_data = []
        for i in range(3):
            with open(os.path.join(self.image_dir, f"image{i}.jpg"), "rb") as f:
                images_data.append(f.read())

        self.assertEqual(table.column("image").to_pylist(), images_data)
        self.assertEqual(
            table.column("bbox").to_pylist(),
            [[[10.0, 20.0, 30.0, 40.0]], [[50.0, 60.0, 70.0, 80.0]], [[90.0, 100.0, 110.0, 120.0]]],
        )
        self.assertEqual(table.column("label").to_pylist(), [[1], [2], [1]])


if __name__ == "__main__":
    unittest.main()
