
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

import io
from typing import Generator, List, Dict, Any

import pyarrow as pa
from datasets import Dataset, IterableDataset
from datasets.features.features import ClassLabel, Value, Sequence, Image, Audio, Features
from PIL.Image import Image as PILImage

from atlas.tasks.data_model.base import BaseDataset
from atlas.utils.system import check_ffmpeg


class HFDataset(BaseDataset):
    """
    A dataset that wraps a Hugging Face dataset.
    """

    def __init__(self, data: Dataset, expand_level: int = 0, **kwargs):
        super().__init__(data)
        self.expand_level = expand_level
        self._expansion_map = {}
        self.metadata.decode_meta = self._get_decode_meta()
        if any(isinstance(f, Audio) for f in self.data.features.values()):
            try:
                check_ffmpeg()
            except (ImportError, RuntimeError) as e:
                print(f"Warning: FFmpeg check failed. Audio processing may be limited. Error: {e}")

    def _get_decode_meta(self) -> Dict[str, str]:
        decode_meta = {}
        for name, feature in self.data.features.items():
            if isinstance(feature, (Image, Audio)):
                decode_meta[name] = str(feature)
        return decode_meta

    def to_arrow_schema(self) -> pa.Schema:
        fields = []
        self._expansion_map.clear()
        for name, feature in self.data.features.items():
            fields.extend(self._feature_to_fields(name, feature, self.expand_level))
        return pa.schema(fields)

    def _feature_to_fields(self, name: str, feature: Any, expand_level: int) -> List[pa.Field]:
        if expand_level > 0 and isinstance(feature, dict):
            fields = []
            for sub_name, sub_feature in sorted(feature.items()):
                new_name = f"{name}_{sub_name}"
                self._expansion_map[new_name] = (name, sub_name, "dict")
                fields.extend(self._feature_to_fields(new_name, sub_feature, expand_level - 1))
            return fields

        if expand_level > 0 and isinstance(feature, Sequence) and isinstance(feature.feature, dict):
            fields = []
            for sub_name, sub_feature in sorted(feature.feature.items()):
                new_name = f"{name}_{sub_name}"
                self._expansion_map[new_name] = (name, sub_name, "list_of_dicts")
                list_of_sub_feature = Sequence(feature=sub_feature)
                fields.append(self._feature_to_field(new_name, list_of_sub_feature))
            return fields

        return [self._feature_to_field(name, feature)]

    def _feature_to_field(self, name: str, feature: Any) -> pa.Field:
        if isinstance(feature, Image):
            return pa.field(name, pa.large_binary(), metadata={"lance:encoding": "binary"})
        if isinstance(feature, Audio):
            return pa.field(name, pa.large_binary(), metadata={"lance:encoding": "binary"})
        if isinstance(feature, ClassLabel):
            return pa.field(name, pa.string())
        if isinstance(feature, Value):
            # Handle cases where the dtype is 'object' which might be an image
            if feature.dtype == 'object':
                 # We can't know for sure without data, so we'll handle serialization in _process_column
                 pass
            return pa.field(name, feature.pa_type)
        if isinstance(feature, Sequence):
            item_field = self._feature_to_field("item", feature.feature)
            return pa.field(name, pa.list_(item_field.type))
        if isinstance(feature, dict):
            struct_fields = [self._feature_to_field(k, v) for k, v in sorted(feature.items())]
            return pa.field(name, pa.struct(struct_fields))
        if isinstance(feature, list):
            # This is a case where the feature is not well-defined.
            # We'll default to a list of nulls and handle it in processing.
            return pa.field(name, pa.list_(pa.null()))

        raise TypeError(f"Unsupported feature type for column '{name}': {type(feature)}")

    def _process_column(self, column_data: list, feature: Any, arrow_type: pa.DataType = None) -> pa.Array:
        # PIL Image handling
        is_pil_column = False
        if column_data:
            for item in column_data:
                if item is not None:
                    if isinstance(item, PILImage):
                        is_pil_column = True
                    break
        
        if isinstance(feature, Image) or is_pil_column:
            serialized = []
            for img in column_data:
                if isinstance(img, PILImage):
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    serialized.append(buf.getvalue())
                elif isinstance(img, dict) and 'bytes' in img and img['bytes']:
                    serialized.append(img['bytes'])
                elif isinstance(img, dict) and 'path' in img and img['path']:
                    with open(img['path'], 'rb') as f:
                        serialized.append(f.read())
                else:
                    serialized.append(None)
            return pa.array(serialized, type=pa.large_binary())

        if isinstance(feature, Audio):
            serialized = []
            for aud in column_data:
                if isinstance(aud, dict):
                    if aud.get('path'):
                        with open(aud['path'], 'rb') as f:
                            serialized.append(f.read())
                    elif aud.get('bytes'):
                        serialized.append(aud['bytes'])
                    else:
                        serialized.append(None)
                elif hasattr(aud, 'path'): # Handle AudioDecoder object
                    with open(aud.path, 'rb') as f:
                        serialized.append(f.read())
                else:
                    serialized.append(None)
            return pa.array(serialized, type=pa.large_binary())

        if isinstance(feature, ClassLabel):
            return pa.array([feature.int2str(val) if val is not None else None for val in column_data], type=pa.string())

        if isinstance(feature, Sequence) and isinstance(feature.feature, ClassLabel):
            return pa.array([[feature.feature.int2str(v) for v in val_list] if val_list is not None else None for val_list in column_data], type=arrow_type)

        if pa.types.is_struct(arrow_type):
            cleaned_data = []
            for row in column_data:
                if row is None or not isinstance(row, dict):
                    cleaned_data.append(None)
                    continue
                
                clean_row = {}
                for field in arrow_type:
                    clean_row[field.name] = row.get(field.name)
                cleaned_data.append(clean_row)
            
            try:
                return pa.array(cleaned_data, type=arrow_type)
            except (pa.ArrowInvalid, pa.ArrowTypeError):
                 return pa.array([str(x) if x is not None else None for x in cleaned_data], type=pa.string())

        try:
            return pa.array(column_data, type=arrow_type)
        except (pa.ArrowInvalid, pa.ArrowTypeError) as e:
            # Fallback for cases where data is inconsistent and casting fails
            # print(f"Error processing column with feature {feature} and type {arrow_type}: {e}")
            # print(f"Data sample: {column_data[:5]}")
            # As a last resort, convert to string
            return pa.array([str(x) if x is not None else None for x in column_data], type=pa.string())


    def to_batches(self, batch_size: int = 1024, **kwargs) -> Generator[pa.RecordBatch, None, None]:
        schema = self.to_arrow_schema()
        
        # To prevent the torchcodec error, we must remove the Audio feature type
        # before any iteration or slicing.
        original_features = self.data.features
        new_features = original_features.copy()
        has_audio = False
        for col_name, feature in new_features.items():
            if isinstance(feature, Audio):
                has_audio = True
                # Cast to a raw type to prevent the decoder from running.
                new_features[col_name] = Value('string')

        if has_audio:
            sanitized_data = self.data.cast(new_features)
        else:
            sanitized_data = self.data

        if isinstance(sanitized_data, IterableDataset):
            # For IterableDataset, we manually create batches as lists of dicts
            batch_as_list_of_dicts = []
            for item in sanitized_data:
                batch_as_list_of_dicts.append(item)
                if len(batch_as_list_of_dicts) == batch_size:
                    # Convert the list of dicts to a dict of lists before processing
                    batch_as_dict_of_lists = {
                        key: [d.get(key) for d in batch_as_list_of_dicts]
                        for key in (batch_as_list_of_dicts[0] if batch_as_list_of_dicts else {})
                    }
                    yield self._process_batch(batch_as_dict_of_lists, schema, original_features)
                    batch_as_list_of_dicts = []
            if batch_as_list_of_dicts:
                batch_as_dict_of_lists = {
                    key: [d.get(key) for d in batch_as_list_of_dicts]
                    for key in (batch_as_list_of_dicts[0] if batch_as_list_of_dicts else {})
                }
                yield self._process_batch(batch_as_dict_of_lists, schema, original_features)
        else:
            # For regular Dataset, slicing gives us a dict of lists directly
            for i in range(0, len(sanitized_data), batch_size):
                batch_as_dict_of_lists = sanitized_data[i : i + batch_size]
                yield self._process_batch(batch_as_dict_of_lists, schema, original_features)

    def _process_batch(self, batch: Dict[str, list], schema: pa.Schema, features: Features) -> pa.RecordBatch:
        arrays = []
        for field in schema:
            if field.name in self._expansion_map:
                original_name, sub_name, expansion_type = self._expansion_map[
                    field.name
                ]
                original_feature = features[original_name]

                if expansion_type == "dict":
                    sub_feature = original_feature[sub_name]
                    column_data = [
                        row.get(sub_name) if row else None
                        for row in batch[original_name]
                    ]
                    processed_data = self._process_column(
                        column_data, sub_feature, field.type
                    )
                    arrays.append(processed_data)

                elif expansion_type == "list_of_dicts":
                    sub_feature = original_feature.feature[sub_name]
                    sub_lists = []
                    for list_of_dicts in batch[original_name]:
                        if list_of_dicts is None:
                            sub_lists.append(None)
                        else:
                            sub_lists.append(
                                [
                                    d.get(sub_name) if isinstance(d, dict) else None
                                    for d in list_of_dicts
                                ]
                            )

                    processed_data = self._process_column(
                        sub_lists, Sequence(feature=sub_feature), field.type
                    )
                    arrays.append(processed_data)

            else:
                column_data = batch[field.name]
                feature = features[field.name]
                processed_data = self._process_column(
                    column_data, feature, field.type
                )
                arrays.append(processed_data)

        return pa.RecordBatch.from_arrays(arrays, schema=schema)

    @property
    def schema(self) -> pa.Schema:
        return self.to_arrow_schema()
