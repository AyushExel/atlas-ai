# lance_utils/builder.py
import pyarrow as pa
import lance
from pathlib import Path
from typing import List, Dict, Generator, Any
from abc import ABC, abstractmethod
from .tasks.base import Task

class LanceWriter:
    """
    A class for writing data to a Lance dataset.
    """

    def __init__(self, output_path: str, task: Task, batch_size: int = 128):
        self.output_path = Path(output_path)
        self.task = task
        self.batch_size = batch_size

    def _batch_generator(self, data_generator: Generator[Dict[str, Any], None, None], schema: pa.Schema) -> Generator[pa.RecordBatch, None, None]:
        batch = []
        for item in data_generator:
            batch.append(item)
            if len(batch) >= self.batch_size:
                yield pa.Table.from_pylist(batch, schema=schema).to_batches()[0]
                batch = []
        if batch:
            yield pa.Table.from_pylist(batch, schema=schema).to_batches()[0]

    def write(self):
        """
        Writes the data to the Lance dataset.
        """
        schema = self.task.get_schema()
        data_generator = self.task.yield_data()
        batch_generator = self._batch_generator(data_generator, schema)

        lance.write_dataset(
            batch_generator,
            self.output_path,
            schema=schema,
            mode="overwrite"
        )
