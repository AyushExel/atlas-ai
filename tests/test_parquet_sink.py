import os
import unittest

import lance
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from atlas.data_sinks import sink


class ParquetSinkTest(unittest.TestCase):
    def setUp(self):
        self.parquet_path = "test.parquet"
        self.lance_path = "test.lance"
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        table = pa.Table.from_pandas(df)
        pq.write_table(table, self.parquet_path)

    def tearDown(self):
        os.remove(self.parquet_path)
        if os.path.exists(self.lance_path):
            import shutil
            shutil.rmtree(self.lance_path)

    def test_sink_parquet(self):
        sink(self.parquet_path, self.lance_path)
        dataset = lance.dataset(self.lance_path)
        self.assertEqual(dataset.count_rows(), 3)
        table = dataset.to_table()
        self.assertEqual(table.column_names, ["a", "b"])
        self.assertEqual(table.column("a").to_pylist(), [1, 2, 3])
        self.assertEqual(table.column("b").to_pylist(), ["x", "y", "z"])


if __name__ == "__main__":
    unittest.main()
