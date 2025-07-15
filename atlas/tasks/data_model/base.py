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

from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, Optional

import lance
import pyarrow as pa


class BaseDataset(ABC):
    """
    Abstract base class for all datasets in Atlas.

    This class defines the common interface for all datasets, whether they are from
    files (e.g., CSV, Parquet) or from task-specific formats (e.g., COCO, YOLO).
    Each subclass must implement the `to_batches` method, which is responsible for
    yielding batches of data as Arrow `RecordBatch` objects.
    """

    def __init__(self, data: str):
        self.data = data

    def to_lance(
        self,
        uri: str,
        mode: str = "create",
        batch_size: Optional[int] = None,
        **kwargs: Optional[Dict[str, Any]],
    ) -> None:
        """
        Converts the dataset to Lance format and saves it to the given URI.

        This method handles the process of reading the data in batches, dynamically
        calculating the batch size if not provided, and writing the data to a Lance
        dataset.

        Args:
            uri (str): The URI of the Lance dataset to be created.
            mode (str, optional): The write mode. Can be "create", "append", or
                "overwrite". Defaults to "create".
            batch_size (Optional[int], optional): The batch size to use when reading
                the data. If not provided, a dynamic batch size will be calculated
                based on the available system memory. Defaults to None.
        """
        from atlas.utils.system import get_dynamic_batch_size

        reader = self.to_batches(batch_size=1) # read one row to estimate size

        batches = iter(reader)
        try:
            first_batch = next(batches)
        except StopIteration:
            print("Warning: The dataset is empty. An empty Lance dataset will be created.")
            return

        row_size_in_bytes = first_batch.nbytes

        if batch_size is None:
            batch_size = get_dynamic_batch_size(row_size_in_bytes)

        reader = self.to_batches(batch_size=batch_size)

        def new_reader():
            yield first_batch
            for batch in batches:
                yield batch

        schema = first_batch.schema
        #for field in ["height", "width", "file_name"]:
        #    if field in schema.names:
        #        schema = schema.remove(schema.get_field_index(field))
        lance.write_dataset(new_reader(), uri, schema=schema, mode=mode, **kwargs)

    @abstractmethod
    def to_batches(self, batch_size: int = 1024) -> Generator[pa.RecordBatch, None, None]:
        """
        Yields batches of the dataset as Arrow RecordBatches.

        This method must be implemented by each subclass. It is responsible for
        reading the data from the source and yielding it in batches of Arrow
        `RecordBatch` objects.

        Args:
            batch_size (int, optional): The number of rows in each batch.
                Defaults to 1024.

        Yields:
            Generator[pa.RecordBatch, None, None]: A generator of Arrow `RecordBatch`
                objects.
        """
        raise NotImplementedError
