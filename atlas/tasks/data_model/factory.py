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

import os
from typing import Any, Dict, Optional, Tuple


from atlas.tasks.data_model.base import BaseDataset


def infer_dataset_type(data: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Infers the dataset type (task and format) based on the data source.

    Args:
        data (str): The data source (file path or directory).

    Returns:
        A tuple containing the inferred task and format.
    """
    if os.path.isdir(data):
        if os.path.exists(os.path.join(data, "annotations")) and any(
            f.endswith(".json") for f in os.listdir(os.path.join(data, "annotations"))
        ):
            if "instances" in str(os.listdir(os.path.join(data, "annotations"))):
                return "object_detection", "coco"
            elif "segmentation" in str(os.listdir(os.path.join(data, "annotations"))):
                return "segmentation", "coco"
        elif os.path.exists(os.path.join(data, "images")) and os.path.exists(
            os.path.join(data, "labels")
        ):
            return "object_detection", "yolo"
    elif data.endswith(".csv"):
        return "tabular", "csv"
    elif data.endswith(".parquet"):
        return "tabular", "parquet"
    elif data.endswith(".json"):
        # A json file could be a COCO dataset
        return "object_detection", "coco"

    return None, None


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

    if not task or not format:
        inferred_task, inferred_format = infer_dataset_type(data)
        task = task or inferred_task
        format = format or inferred_format
        options["task"] = task
        options["format"] = format


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
    elif task == "tabular":
        if format == "csv":
            from atlas.tasks.tabular.csv import CsvDataset
            return CsvDataset(data)
        elif format == "parquet":
            from atlas.tasks.tabular.parquet import ParquetDataset
            return ParquetDataset(data)

    raise ValueError(f"Unsupported data format or task: {data}, {options}")
