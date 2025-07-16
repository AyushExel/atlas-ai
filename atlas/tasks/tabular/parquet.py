# Atlas: A data-centric AI framework
#
# Copyright (c) 2024-present, Atlas Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Generator

import lance
import pyarrow as pa
import pyarrow.parquet as pq

from atlas.tasks.data_model.base import BaseDataset


class ParquetDataset(BaseDataset):
    """
    A dataset that reads data from a Parquet file.
    """

    def to_lance(
        self,
        uri: str,
        mode: str = "create",
        batch_size: int = 1024,
        **kwargs,
    ) -> None:
        """
        Converts the dataset to Lance format and saves it to the given URI.
        """
        table = pq.read_table(self.data)
        lance.write_dataset(table, uri, mode=mode)

    def to_batches(self, batch_size: int = 1024) -> Generator[pa.RecordBatch, None, None]:
        """
        Yields batches of the dataset as Arrow RecordBatches.
        """
        parquet_file = pq.ParquetFile(self.data)
        for batch in parquet_file.iter_batches(batch_size=batch_size):
            yield batch
