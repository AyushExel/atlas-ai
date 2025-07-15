import json
import os
import unittest

import lance
import numpy as np
import pandas as pd
import pyarrow as pa
from PIL import Image

from atlas.data_sinks import sink


class CocoSegmentationSinkTest(unittest.TestCase):
    def setUp(self):
        self.coco_path = "test_coco_segmentation.json"
        self.lance_path = "test_coco_segmentation.lance"
        self.image_dir = "test_segmentation_images"
        os.makedirs(self.image_dir, exist_ok=True)

        # Create dummy image files
        for i in range(1):
            img = Image.new('RGB', (100, 100), color = 'red')
            img.save(os.path.join(self.image_dir, f"image{i}.jpg"))

        coco_data = {
            "images": [
                {"id": 0, "file_name": os.path.join(self.image_dir, "image0.jpg"), "height": 100, "width": 100},
            ],
            "annotations": [
                {
                    "id": 0,
                    "image_id": 0,
                    "category_id": 1,
                    "bbox": [10, 20, 30, 40],
                    "segmentation": [[10, 20, 40, 20, 40, 60, 10, 60]],
                },
            ],
            "categories": [
                {"id": 1, "name": "cat"},
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

    def test_sink_coco_segmentation(self):
        sink(self.coco_path, self.lance_path, options={"task": "segmentation", "format": "coco"})
        dataset = lance.dataset(self.lance_path)
        self.assertEqual(dataset.count_rows(), 1)
        table = dataset.to_table()
        self.assertEqual(table.column_names, ["image", "bbox", "mask", "label", "height", "width", "file_name"])

        with open(os.path.join(self.image_dir, "image0.jpg"), "rb") as f:
            image_data = f.read()
        self.assertEqual(table.column("image").to_pylist()[0], image_data)

        self.assertEqual(table.column("bbox").to_pylist()[0], [[10.0, 20.0, 30.0, 40.0]])
        self.assertEqual(table.column("label").to_pylist()[0], [1])

        mask_bytes = table.column("mask").to_pylist()[0][0]
        mask = np.frombuffer(mask_bytes, dtype=np.uint8).reshape(100, 100)
        self.assertEqual(mask.shape, (100, 100))
        self.assertTrue(np.any(mask > 0))


if __name__ == "__main__":
    unittest.main()
