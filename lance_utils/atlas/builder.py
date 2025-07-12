# lance_utils/builder.py
import pyarrow as pa
import lance
from pathlib import Path
from typing import List, Dict
from PIL import Image
import io
from tqdm import tqdm
import importlib
import pkgutil
import atlas
from .tasks.base import DataItem, Annotation
from .system import get_auto_batch_size, estimate_image_memory_footprint

class LanceBuilder:
    def __init__(self, input_path: str, output_path: str, batch_size: int = 0, max_rows_per_file: int = 1024):
        self.input_path = Path(input_path)
        self.output_path = output_path
        self.batch_size = batch_size
        self.max_rows_per_file = max_rows_per_file

    def _discover_extractors(self):
        import atlas.tasks as tasks_package
        extractors = []
        for importer, modname, ispkg in pkgutil.walk_packages(path=tasks_package.__path__, prefix=tasks_package.__name__+'.'):
            if "extractors" in modname:
                module = importlib.import_module(modname)
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if isinstance(attribute, type) and issubclass(attribute, tasks_package.base.Extractor) and attribute is not tasks_package.base.Extractor:
                        extractors.append(attribute())
        return extractors

    def _build_schema(self, all_annotations: Dict[str, Annotation], item_props: Dict[str, bool]) -> pa.Schema:
        fields = [pa.field("item_id", pa.string())]
        if item_props.get("has_images"):
            fields.extend([
                pa.field("image", pa.binary()),
                pa.field("filename", pa.string())
            ])
        if item_props.get("has_text") and "text" not in [ann.arrow_field().name for ann in all_annotations.values()]:
            fields.append(pa.field("text", pa.string()))
        
        for key, ann_type in all_annotations.items():
            fields.append(ann_type.arrow_field())
        
        return pa.schema(fields)

    def _data_generator(self, items: Dict[str, DataItem], schema: pa.Schema, current_batch_size: int):
        batch_data = []
        for item in tqdm(items.values(), desc="Processing items"):
            record = {"item_id": item.item_id}
            
            if item.image_path and item.image_path.exists():
                record["image"] = item.image_path.read_bytes()
                record["filename"] = item.image_path.name
            elif "image" in schema.names:
                record["image"] = None
                record["filename"] = None
            
            if item.text_content:
                record["text"] = item.text_content
            elif "text" in schema.names:
                record["text"] = None

            for field in schema:
                field_name = field.name
                if field_name in record: continue

                if field_name in item.annotations:
                    annotations = item.annotations[field_name]
                    if pa.types.is_list(field.type) or pa.types.is_struct(field.type):
                        record[field_name] = [ann.to_dict() for ann in annotations]
                        if not pa.types.is_list(field.type):
                             record[field_name] = record[field_name][0]
                    elif annotations:
                        record[field_name] = annotations[0].to_dict().get(field_name)
                else:
                    record[field_name] = None
            
            batch_data.append(record)
            if len(batch_data) >= current_batch_size:
                yield pa.Table.from_pylist(batch_data, schema=schema).to_batches()
                batch_data = []
        
        if batch_data:
            yield pa.Table.from_pylist(batch_data, schema=schema).to_batches()

    def convert(self):
        print("Discovering annotation extractors...")
        extractors = self._discover_extractors()
        print(f"Found {len(extractors)} extractors: {[e.__class__.__name__ for e in extractors]}")

        items: Dict[str, DataItem] = {}
        all_annotation_types: Dict[str, type] = {}
        item_props = {"has_images": False, "has_text": False}

        print("Extracting annotations...")
        for extractor in extractors:
            extracted_data = extractor.extract(self.input_path)
            for item_id, annotations in extracted_data.items():
                if not annotations: continue
                
                # If item doesn't exist, create it. Otherwise, just add annotations.
                if item_id not in items:
                    # Try to find the image in a few common locations, then search recursively
                    possible_paths = [
                        self.input_path / "images" / item_id,
                        self.input_path / "PNGImages" / item_id,
                        self.input_path / item_id,
                    ]
                    image_path = None
                    for p in possible_paths:
                        if p.exists():
                            image_path = p
                            break
                    
                    # If not found in common paths, search recursively
                    if not image_path:
                        for found_path in self.input_path.rglob(item_id):
                            image_path = found_path
                            break

                    text_content = None
                    if isinstance(annotations[0], atlas.tasks.base.RawText):
                        text_content = annotations[0].text
                        item_props["has_text"] = True
                        # This is a text item, so it shouldn't have an image path
                        image_path = None

                    items[item_id] = DataItem(item_id, image_path if image_path and image_path.exists() else None, text_content)
                
                if items[item_id].image_path: item_props["has_images"] = True

                # Add annotations to the (new or existing) item
                ann_type = annotations[0].__class__
                field_name = ann_type.arrow_field().name
                items[item_id].add_annotations(field_name, annotations)
                if field_name not in all_annotation_types:
                    all_annotation_types[field_name] = ann_type

        if not items:
            raise ValueError("No processable items found. Check input path and extractor logic.")

        print("Building dynamic schema...")
        schema = self._build_schema(all_annotation_types, item_props)
        print(f"Schema: {schema}")

        if self.batch_size == 0:
            footprint = 1024
            if item_props["has_images"]:
                image_paths = [item.image_path for item in items.values() if item.image_path]
                footprint = estimate_image_memory_footprint(image_paths) + 2048
            current_batch_size = get_auto_batch_size(footprint)
        else:
            current_batch_size = self.batch_size
        
        print(f"Using batch size: {current_batch_size}")

        data_generator = (batch for batch_list in self._data_generator(items, schema, current_batch_size) for batch in batch_list)

        lance.write_dataset(
            data_generator,
            self.output_path,
            schema=schema,
            max_rows_per_file=self.max_rows_per_file,
            mode="overwrite"
        )
        print("Conversion complete.")
