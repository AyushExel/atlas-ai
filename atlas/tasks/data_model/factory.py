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

from typing import Any, Dict, Optional

from atlas.tasks.data_model.base import BaseDataset


def create_dataset(data: str, options: Optional[Dict[str, Any]] = None) -> BaseDataset:
    """
    Factory function to create a dataset object based on the given options.

    Args:
        data (str): The data source.
        options (Optional[Dict[str, Any]], optional): A dictionary of options for creating
            the dataset. Defaults to None.

    Returns:
        BaseDataset: A dataset object.
    """
    if options is None:
        options = {}

    task = options.get("task")
    format = options.get("format")

    if task == "object_detection":
        if format == "coco":
            from atlas.tasks.object_detection.coco import CocoDataset
            return CocoDataset(data, options)
        elif format == "yolo":
            from atlas.tasks.object_detection.yolo import YoloDataset
            return YoloDataset(data, options)
    elif task == "segmentation":
        if format == "coco":
            from atlas.tasks.segmentation.coco import CocoSegmentationDataset
            return CocoSegmentationDataset(data, options)
    elif data.endswith(".csv"):
        from atlas.tasks.tabular.csv import CsvDataset
        return CsvDataset(data)
    elif data.endswith(".parquet"):
        from atlas.tasks.tabular.parquet import ParquetDataset
        return ParquetDataset(data)
    elif task == "text":
        if format == "jsonl":
            from atlas.tasks.text.jsonl import JsonlDataset
            return JsonlDataset(data)
    elif task == "rag":
        if format == "json":
            from atlas.tasks.rag.json import JsonDataset
            return JsonDataset(data)

    raise ValueError(f"Unsupported data format or task: {data}, {options}")
