import os
import unittest

import lance
import pandas as pd
import pyarrow as pa

from atlas.data_sinks import sink


class YoloSinkTest(unittest.TestCase):
    def setUp(self):
        self.yolo_dir = "test_yolo"
        self.lance_path = "test_yolo.lance"
        os.makedirs(self.yolo_dir, exist_ok=True)

        # Create dummy image and label files
        for i in range(3):
            with open(os.path.join(self.yolo_dir, f"image{i}.jpg"), "w") as f:
                f.write("dummy image data")
            with open(os.path.join(self.yolo_dir, f"image{i}.txt"), "w") as f:
                f.write(f"{i} 0.5 0.5 0.2 0.2\n")

    def tearDown(self):
        if os.path.exists(self.yolo_dir):
            import shutil
            shutil.rmtree(self.yolo_dir)
        if os.path.exists(self.lance_path):
            import shutil
            shutil.rmtree(self.lance_path)

    def test_sink_yolo(self):
        sink(self.yolo_dir, self.lance_path, options={"task": "object_detection", "format": "yolo"})
        dataset = lance.dataset(self.lance_path)
        self.assertEqual(dataset.count_rows(), 3)
        table = dataset.to_table()
        self.assertEqual(table.column_names, ["image", "bbox", "label"])

        images_data = []
        for i in range(3):
            with open(os.path.join(self.yolo_dir, f"image{i}.jpg"), "rb") as f:
                images_data.append(f.read())

        self.assertEqual(table.column("image").to_pylist(), images_data)
        for i, row in enumerate(table.column("bbox").to_pylist()):
            for j, val in enumerate(row):
                self.assertAlmostEqual(val, [0.5, 0.5, 0.2, 0.2][j], places=6)
        self.assertEqual(table.column("label").to_pylist(), [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
