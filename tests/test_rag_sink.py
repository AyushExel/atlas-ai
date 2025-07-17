import os
import json
import unittest

import lance
import pyarrow as pa

from atlas.data_sinks import sink


class TestRagSink(unittest.TestCase):
    def test_sink_json(self):
        # Create a dummy JSON file
        with open("rag.json", "w") as f:
            json.dump(
                [
                    {
                        "question": "What is the capital of France?",
                        "context": "Paris is the capital of France.",
                        "answer": "Paris",
                    },
                    {
                        "question": "What is the capital of Germany?",
                        "context": "Berlin is the capital of Germany.",
                        "answer": "Berlin",
                    },
                ],
                f,
            )

        # Sink the data
        sink("rag.json", "rag.lance", options={"task": "rag", "format": "json"})

        # Check that the data was sunk correctly
        dataset = lance.dataset("rag.lance")
        self.assertEqual(dataset.count_rows(), 2)
        self.assertEqual(
            dataset.to_table().to_pydict(),
            {
                "question": [
                    "What is the capital of France?",
                    "What is the capital of Germany?",
                ],
                "context": [
                    "Paris is the capital of France.",
                    "Berlin is the capital of Germany.",
                ],
                "answer": ["Paris", "Berlin"],
            },
        )

        # Clean up
        os.remove("rag.json")
        os.remove("rag.lance")
