import os
import json

from atlas.data_sinks import sink

# Create a dummy JSONL file
with open("text.jsonl", "w") as f:
    f.write(json.dumps({"text": "This is a test."}) + "\n")
    f.write(json.dumps({"text": "This is another test."}) + "\n")

# Sink the data
sink("text.jsonl", "text.lance", options={"task": "text", "format": "jsonl"})

# Clean up
os.remove("text.jsonl")
