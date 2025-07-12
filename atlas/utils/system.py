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

import psutil


def get_available_memory():
    """
    Returns the available memory in bytes.
    """
    return psutil.virtual_memory().available


def get_dynamic_batch_size(row_size_in_bytes: int, fraction: float = 0.1):
    """
    Calculates a dynamic batch size based on the available memory.

    Args:
        row_size_in_bytes (int): The size of a single row in bytes.
        fraction (float, optional): The fraction of available memory to use.
            Defaults to 0.1.

    Returns:
        int: The calculated batch size.
    """
    if row_size_in_bytes <= 0:
        return 1024  # default batch size

    available_memory = get_available_memory()
    target_memory = available_memory * fraction
    batch_size = int(target_memory / row_size_in_bytes)
    return max(1, batch_size)  # ensure batch size is at least 1
