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

from typing import Any, Dict, Optional, Union

import lance
import pyarrow as pa

from atlas.tasks.data_model.base import BaseDataset
from atlas.tasks.data_model.factory import create_dataset


def sink(
    data: Union[str, BaseDataset],
    uri: str,
    options: Optional[Dict[str, Any]] = None,
):
    """
    Sinks data from a given source to a specified destination in Lance format.

    This function provides a high-level API for converting and sinking data from various
    sources into a Lance dataset. The source can be a file path (e.g., a CSV file, a
    COCO annotation file) or a `BaseDataset` object.

    Args:
        data (Union[str, BaseDataset]): The data to be sunk. This can be a file path (str)
            or a `BaseDataset` object.
        uri (str): The destination URI where the Lance dataset will be created.
        options (Optional[Dict[str, Any]], optional): A dictionary of options for the sink
            operation. The available options depend on the data source. For example, when
            sinking a COCO dataset, you can specify the `task` and `format` in the
            options. Defaults to None.
    """
    if options is None:
        options = {}

    if isinstance(data, str):
        dataset = create_dataset(data, options)
    else:
        dataset = data

    lance_options = options.copy()
    if "task" in lance_options:
        del lance_options["task"]
    if "format" in lance_options:
        del lance_options["format"]

    image_root = lance_options.pop("image_root", None)
    dataset.to_lance(uri, **lance_options)
