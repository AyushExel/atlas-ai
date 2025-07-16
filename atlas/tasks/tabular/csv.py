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

import pandas as pd
import pyarrow as pa
from pyarrow import csv
import lance

from atlas.tasks.data_model.base import BaseDataset


class CsvDataset(BaseDataset):
    """
    A dataset that reads data from a CSV file.
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
        df = pd.read_csv(self.data)
        lance.write_dataset(df, uri, mode=mode)

    def to_batches(self, batch_size: int = 1024) -> Generator[pa.RecordBatch, None, None]:
        """
        Yields batches of the dataset as Arrow RecordBatches.
        """

        reader = pd.read_csv(self.data, chunksize=batch_size)
        for chunk in reader:
            yield pa.Table.from_pandas(chunk).to_batches()[0]
