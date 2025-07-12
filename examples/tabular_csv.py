import atlas
import os
import pandas as pd

# Create a temporary directory to store the data
if not os.path.exists("examples/data"):
    os.makedirs("examples/data")

# Create a dummy CSV file
data = {"col1": [1, 2, 3], "col2": ["A", "B", "C"]}
df = pd.DataFrame(data)
df.to_csv("examples/data/dummy.csv", index=False)

# Sink the CSV file to a Lance dataset
atlas.sink("examples/data/dummy.csv", "examples/data/tabular.lance")

# Visualize some samples from the dataset
atlas.visualize("examples/data/tabular.lance", num_samples=3)
