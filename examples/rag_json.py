import os
import json

from atlas.data_sinks import sink

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

# Clean up
os.remove("rag.json")
