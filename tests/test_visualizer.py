import os
import unittest
from unittest.mock import patch, call

import lance
import pandas as pd
from PIL import Image

from atlas.visualizers.visualizer import visualize


class VisualizerTest(unittest.TestCase):
    def setUp(self):
        self.lance_path = "test_visualizer.lance"
        self.image_dir = "test_visualizer_images"
        os.makedirs(self.image_dir, exist_ok=True)

        # Create dummy image files
        for i in range(3):
            img = Image.new('RGB', (100, 100), color = 'red')
            img.save(os.path.join(self.image_dir, f"image{i}.jpg"))

        images_data = []
        for i in range(3):
            with open(os.path.join(self.image_dir, f"image{i}.jpg"), "rb") as f:
                images_data.append(f.read())

        df = pd.DataFrame({
            "image": images_data,
            "bbox": [[10, 20, 30, 40], [50, 60, 70, 80], [90, 100, 110, 120]],
            "label": [1, 2, 1],
        })
        import pyarrow as pa
        table = pa.Table.from_pandas(df)
        lance.write_dataset(table, self.lance_path)

    def tearDown(self):
        if os.path.exists(self.lance_path):
            import shutil
            shutil.rmtree(self.lance_path)
        if os.path.exists(self.image_dir):
            import shutil
            shutil.rmtree(self.image_dir)

    @patch('matplotlib.pyplot.show')
    def test_visualize(self, mock_show):
        visualize(self.lance_path, num_samples=2)
        self.assertEqual(mock_show.call_count, 1)

    @patch('matplotlib.pyplot.savefig')
    def test_visualize_saves_file(self, mock_savefig):
        output_file = "test_visualizer.png"
        visualize(self.lance_path, num_samples=2, output_file=output_file)
        mock_savefig.assert_called_once_with(output_file)


if __name__ == "__main__":
    unittest.main()
