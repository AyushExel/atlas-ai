# Atlas

Atlas is a Python library for sinking data from various sources into the Lance format. It provides a simple and efficient way to convert your existing datasets, whether they are in file formats like CSV and Parquet or in task-specific formats like COCO and YOLO, into self-contained Lance datasets.

## Features

- **Sink from various sources:** Convert data from CSV, Parquet, COCO (object detection and segmentation), and YOLO into Lance format.
- **Self-contained datasets:** Images and other binary data are stored directly in the Lance dataset, making them portable and self-sufficient.
- **Efficient data ingestion:** Uses Apache Arrow's `RecordBatch` generator streams for ingesting data into Lance, with dynamic batch size calculation for optimal performance.
- **Extensible API:** The library is designed to be easily extendable, allowing you to add support for new data formats and tasks.
- **Data visualization:** A built-in visualizer allows you to inspect and visualize your datasets, including images with bounding boxes and segmentation masks.
- **Command-line interface:** A simple and intuitive CLI for sinking and visualizing datasets.

## Installation

```bash
pip install atlas-ai
```

## Usage

### Python API

```python
import atlas

# Sink a CSV file to a Lance dataset
atlas.sink("my_data.csv", "my_dataset.lance")

# Sink a COCO object detection dataset to a Lance dataset
atlas.sink("coco_annotations.json", "my_dataset.lance", options={"task": "object_detection", "format": "coco"})

# Sink a COCO segmentation dataset to a Lance dataset
atlas.sink("coco_annotations.json", "my_dataset.lance", options={"task": "segmentation", "format": "coco"})

# Sink a YOLO dataset to a Lance dataset
atlas.sink("yolo_data_dir", "my_dataset.lance", options={"task": "object_detection", "format": "yolo"})
```

### Command-Line Interface

```bash
# Sink a CSV file
atlas sink my_data.csv my_dataset.lance

# Sink a COCO object detection dataset
atlas sink coco_annotations.json my_dataset.lance --task object_detection --format coco

# Sink a COCO segmentation dataset
atlas sink coco_annotations.json my_dataset.lance --task segmentation --format coco

# Sink a YOLO dataset
atlas sink yolo_data_dir my_dataset.lance --task object_detection --format yolo

# Visualize a dataset
atlas visualize my_dataset.lance --num-samples 10
```

## Examples

The `examples` directory contains scripts that demonstrate how to use the `atlas-ai` library for various tasks. To run the examples, you will need to install the required dependencies:

```bash
pip install pandas pyarrow requests
```

Then, you can run the example scripts from the root of the repository:

```bash
python examples/tabular_csv.py
python examples/tabular_parquet.py
python examples/object_detection_coco.py
python examples/segmentation_coco.py
python examples/object_detection_yolo.py
```

## Contributing

Contributions are welcome! Please see the [contributing guide](CONTRIBUTING.md) for more information.

## License

Atlas is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for more information.
