import os
import json
import unittest

import lance
import pyarrow as pa

from atlas.data_sinks import sink


class TestTextSink(unittest.TestCase):
    def test_sink_jsonl(self):
        # Create a dummy JSONL file
        with open("text.jsonl", "w") as f:
            f.write(json.dumps({"text": "This is a test."}) + "\n")
            f.write(json.dumps({"text": "This is another test."}) + "\n")

        # Sink the data
        sink("text.jsonl", "text.lance", options={"task": "text", "format": "jsonl"})

        # Check that the data was sunk correctly
        dataset = lance.dataset("text.lance")
        self.assertEqual(dataset.count_rows(), 2)
        self.assertEqual(
            dataset.to_table().to_pydict(),
            {
                "text": ["This is a test.", "This is another test."],
            },
        )

        # Clean up
        os.remove("text.jsonl")
        os.remove("text.lance")
