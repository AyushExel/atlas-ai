

import os
import shutil
import unittest
import lance
from datasets import Dataset, Features, Value, load_dataset
import pyarrow as pa
import pandas as pd

import atlas
from atlas.data_sinks import sink

def test_dict_expansion():
    print("--- Running test: test_dict_expansion ---")
    test_dir = "test_hf_expansion"
    os.makedirs(test_dir, exist_ok=True)
    data = [
        {"nested": {"a": 1, "b": "one"}},
        {"nested": {"a": 2, "b": "two", "c": True}},
        {"nested": {"a": 3}},
        {"nested": {}},
        {},
        {"nested": {"a": None, "b": "four"}},
    ]
    features = Features({
        "nested": {
            "a": Value("int64"),
            "b": Value("string"),
            "c": Value("bool"),
        }
    })
    dataset = Dataset.from_list(data, features=features)

    uri = os.path.join(test_dir, "expansion_robust.lance")
    sink(dataset, uri, task="hf", expand_level=1, handle_nested_nulls=True)

    retrieved_data = lance.dataset(uri)
    assert retrieved_data.count_rows() == len(data)
    
    expected_schema_names = {"nested_a", "nested_b", "nested_c"}
    assert set(retrieved_data.schema.names) == expected_schema_names

    table = retrieved_data.to_table()
    assert table.column("nested_a").to_pylist() == [1, 2, 3, None, None, None]
    assert table.column("nested_b").to_pylist() == ["one", "two", None, None, None, "four"]
    assert table.column("nested_c").to_pylist() == [None, True, None, None, None, None]
    
    shutil.rmtree(test_dir)
    print("--- Test finished: test_dict_expansion ---\n")


def test_list_of_dicts_expansion():
    print("--- Running test: test_list_of_dicts_expansion ---")
    output_dir = "hf_nested_expansion.lance"
    db_path = "lancedb"
    
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    os.makedirs(db_path, exist_ok=True)

    dummy_data = [
        {
            "id": 1,
            "image_path": "/path/to/image1.jpg",
            "objects": [
                {"id": 101, "category": "cat"},
                {"id": 102, "category": "dog"},
            ],
        },
        {
            "id": 2,
            "image_path": "/path/to/image2.jpg",
            "objects": [
                {"id": 201, "category": "cat"},
            ],
        },
        {
            "id": 3,
            "image_path": "/path/to/image3.jpg",
            "objects": [], # Empty list
        },
        {
            "id": 4,
            "image_path": "/path/to/image4.jpg",
            "objects": None, # Null list
        },
    ]

    df = pd.DataFrame(dummy_data)
    dataset = Dataset.from_pandas(df)

    lance_file_path = os.path.join(db_path, output_dir)
    atlas.sink(dataset, lance_file_path, task="hf", expand_level=1, handle_nested_nulls=True)

    output_dataset = lance.dataset(lance_file_path)
    final_schema = output_dataset.schema
    
    expected_fields = {
        "id", "image_path", 
        "objects_id", "objects_category"
    }
    final_field_names = set(final_schema.names)
    
    assert expected_fields.issubset(final_field_names)
    
    shutil.rmtree(db_path)
    print("--- Test finished: test_list_of_dicts_expansion ---\n")


def test_failing_list_of_dicts_expansion():
    print("--- Running test: test_failing_list_of_dicts_expansion ---")
    output_dir = "cova_coco_v2.lance"
    db_path = "lancedb_fail"

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    os.makedirs(db_path, exist_ok=True)

    print("Loading dataset in streaming mode...")
    base_dataset = load_dataset("CreatlV/cova-coco-v2", split="train", streaming=True)
    print("Taking first 100 elements...")
    streamed_dataset = base_dataset.take(100)
    print("Dataset loaded.")

    print("Sinking data...")
    lance_file_path = os.path.join(db_path, output_dir)
    atlas.sink(streamed_dataset, lance_file_path, task="hf", expand_level=1)
    print("Sinking complete.")

    output_dataset = lance.dataset(lance_file_path)
    final_schema = output_dataset.schema
    print(final_schema)

    # Basic check, can be improved after the fix
    assert 'objects_id' in final_schema.names
    assert 'objects_bbox' in final_schema.names
    assert 'objects_category' in final_schema.names

    shutil.rmtree(db_path)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    print("--- Test finished: test_failing_list_of_dicts_expansion ---\n")


def create_extensive_test_data():
    return [
        # Case 1: Regular data
        {
            "id": 1,
            "metadata": {"source": "web", "quality": 95},
            "items": [
                {"item_id": "a", "value": 1.0},
                {"item_id": "b", "value": 2.0},
            ],
        },
        # Case 2: Missing nested dict
        {
            "id": 2,
            "metadata": None,
            "items": [
                {"item_id": "c", "value": 3.0},
            ],
        },
        # Case 3: Empty list of dicts
        {
            "id": 3,
            "metadata": {"source": "internal", "quality": 99},
            "items": [],
        },
        # Case 4: Null list of dicts
        {
            "id": 4,
            "metadata": {"source": "web", "quality": 80},
            "items": None,
        },
        # Case 5: List of dicts with missing keys
        {
            "id": 5,
            "metadata": {"source": "partner", "quality": 92, "partner_id": 123},
            "items": [
                {"item_id": "d"},
                {"value": 5.0},
            ],
        },
        # Case 6: Empty dict in list
        {
            "id": 6,
            "metadata": {"source": "web", "quality": 70},
            "items": [{}],
        },
        # Case 7: All fields missing
        {
            "id": 7,
            "metadata": None,
            "items": None,
        },
        # Case 8: Nested list of dicts (level 2) - expansion should only go to level 1
        {
            "id": 8,
            "metadata": {"source": "test"},
            "items": [
                {"item_id": "e", "value": 6.0, "sub_items": [{"sub_id": "x"}, {"sub_id": "y"}]}
            ]
        }
    ]

def test_extensive_expansion():
    print("--- Running test: test_extensive_expansion ---")
    output_dir = "extensive_expansion.lance"
    db_path = "lancedb_extensive"

    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    os.makedirs(db_path, exist_ok=True)

    data = create_extensive_test_data()
    df = pd.DataFrame(data)
    dataset = Dataset.from_pandas(df)

    lance_file_path = os.path.join(db_path, output_dir)
    atlas.sink(dataset, lance_file_path, task="hf", expand_level=1, handle_nested_nulls=True)

    output_dataset = lance.dataset(lance_file_path)
    final_schema = output_dataset.schema
    
    expected_fields = {
        "id",
        "metadata_source",
        "metadata_quality",
        "metadata_partner_id",
        "items_item_id",
        "items_value",
        "items_sub_items" # This should remain nested
    }
    final_field_names = set(final_schema.names)
    
    assert expected_fields.issubset(final_field_names)

    table = output_dataset.to_table()
    
    # Add more specific assertions here based on expected output after fix
    assert table.column("id").to_pylist() == [1, 2, 3, 4, 5, 6, 7, 8]
    assert table.column("metadata_source").to_pylist() == ["web", None, "internal", "web", "partner", "web", None, "test"]
    
    shutil.rmtree(db_path)
    print("--- Test finished: test_extensive_expansion ---\n")


def main():
    test_dict_expansion()
    test_list_of_dicts_expansion()
    test_extensive_expansion()
    
    # The failing test is expected to fail, so only run it if you are actively debugging it.
    try:
        test_failing_list_of_dicts_expansion()
    except Exception as e:
        print(f"Failing test failed as expected: {e}")

if __name__ == "__main__":
    main()
