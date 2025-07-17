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

import json
from typing import Generator

import pyarrow as pa

from atlas.tasks.data_model.base import BaseDataset


class JsonlDataset(BaseDataset):
    """
    A class to represent a JSONL dataset.
    """

    def to_batches(self, batch_size: int = 1024) -> Generator[pa.RecordBatch, None, None]:
        """
        Yields batches of the dataset as Arrow RecordBatches.

        Args:
            batch_size (int, optional): The number of rows in each batch.
                Defaults to 1024.

        Yields:
            Generator[pa.RecordBatch, None, None]: A generator of Arrow `RecordBatch`
                objects.
        """
        with open(self.data, "r") as f:
            lines = []
            for line in f:
                lines.append(json.loads(line))
                if len(lines) == batch_size:
                    yield pa.RecordBatch.from_pylist(lines)
                    lines = []
            if lines:
                yield pa.RecordBatch.from_pylist(lines)
