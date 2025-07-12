import os
import unittest

import lance
import pandas as pd
import pyarrow as pa

from atlas.data_sinks import sink


class CsvSinkTest(unittest.TestCase):
    def setUp(self):
        self.csv_path = "test.csv"
        self.lance_path = "test.lance"
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        df.to_csv(self.csv_path, index=False)

    def tearDown(self):
        os.remove(self.csv_path)
        if os.path.exists(self.lance_path):
            import shutil
            shutil.rmtree(self.lance_path)

    def test_sink_csv(self):
        sink(self.csv_path, self.lance_path)
        dataset = lance.dataset(self.lance_path)
        self.assertEqual(dataset.count_rows(), 3)
        table = dataset.to_table()
        self.assertEqual(table.column_names, ["a", "b"])
        self.assertEqual(table.column("a").to_pylist(), [1, 2, 3])
        self.assertEqual(table.column("b").to_pylist(), ["x", "y", "z"])


if __name__ == "__main__":
    unittest.main()
