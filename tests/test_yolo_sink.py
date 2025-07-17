import os
import unittest
import yaml

import lance
import pandas as pd
import pyarrow as pa

from atlas.data_sinks import sink
from atlas.tasks.data_model.base import BaseDataset


class YoloSinkTest(unittest.TestCase):
    def setUp(self):
        self.yolo_dir = "test_yolo"
        self.lance_path = "test_yolo.lance"
        os.makedirs(self.yolo_dir, exist_ok=True)

        # Create dummy image and label files
        from PIL import Image
        image_dir = os.path.join(self.yolo_dir, "images", "train2017")
        label_dir = os.path.join(self.yolo_dir, "labels", "train2017")
        os.makedirs(image_dir, exist_ok=True)
        os.makedirs(label_dir, exist_ok=True)
        for i in range(3):
            img = Image.new('RGB', (100, 100), color = 'red')
            img.save(os.path.join(image_dir, f"image{i}.jpg"))
            with open(os.path.join(label_dir, f"image{i}.txt"), "w") as f:
                f.write(f"{i} 0.5 0.5 0.2 0.2\n")

    def tearDown(self):
        if os.path.exists(self.yolo_dir):
            import shutil
            shutil.rmtree(self.yolo_dir)
        if os.path.exists(self.lance_path):
            import shutil
            shutil.rmtree(self.lance_path)
        if os.path.exists("data.yaml"):
            os.remove("data.yaml")

    def test_sink_yolo_with_data_yaml(self):
        # Create a data.yaml file
        with open(os.path.join(self.yolo_dir, "data.yaml"), "w") as f:
            yaml.dump({"names": ["class0", "class1", "class2"]}, f)

        sink(self.yolo_dir, self.lance_path, options={"task": "object_detection", "format": "yolo"})
        dataset = lance.dataset(self.lance_path)
        self.assertEqual(dataset.count_rows(), 3)
        metadata = BaseDataset.get_metadata(self.lance_path)
        self.assertEqual(metadata.class_names, {0: "class0", 1: "class1", 2: "class2"})

    def test_sink_yolo_without_data_yaml(self):
        sink(self.yolo_dir, self.lance_path, options={"task": "object_detection", "format": "yolo"})
        dataset = lance.dataset(self.lance_path)
        self.assertEqual(dataset.count_rows(), 3)
        metadata = BaseDataset.get_metadata(self.lance_path)
        self.assertEqual(metadata.class_names, {0: "0", 1: "1", 2: "2"})

    def test_sink_yolo(self):
        sink(self.yolo_dir, self.lance_path, options={"task": "object_detection", "format": "yolo"})
        dataset = lance.dataset(self.lance_path)
        self.assertEqual(dataset.count_rows(), 3)
        table = dataset.to_table()
        self.assertEqual(table.column_names, ["image", "bbox", "label", "height", "width", "file_name"])

        images_data = []
        image_dir = os.path.join(self.yolo_dir, "images", "train2017")
        for i in range(3):
            with open(os.path.join(image_dir, f"image{i}.jpg"), "rb") as f:
                images_data.append(f.read())

        self.assertEqual(table.column("image").to_pylist(), images_data)
        for i, row in enumerate(table.column("bbox").to_pylist()):
            for j, inner_row in enumerate(row):
                for k, val in enumerate(inner_row):
                    self.assertAlmostEqual(val, [0.5, 0.5, 0.2, 0.2][k], places=6)
        self.assertEqual(table.column("label").to_pylist(), [[0], [1], [2]])


if __name__ == "__main__":
    unittest.main()
