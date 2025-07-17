# Atlas

Atlas is a data-centric AI framework for curating, indexing, and analyzing massive datasets for deep learning applications. It provides a suite of tools to streamline the entire data lifecycle, from initial data ingestion to model training and analysis.

## Vision

The vision for Atlas is to provide a comprehensive solution for managing large-scale datasets in AI development. The framework is built around three core operations:

-   **Sink:** Ingest data from any source and format into an optimized Lance dataset. Atlas automatically infers the dataset type, extracts rich metadata, and stores the data in a self-contained, portable format.
-   **Index:** Create powerful, multi-modal indexes on your data to enable fast and efficient search and retrieval. Whether you're working with images, text, or other data types, Atlas will help you find the data you need in seconds.
-   **Analyse:** Analyse your datasets to gain insights, identify patterns, and debug your models. Atlas will provide tools for data visualization, embedding analysis, and model performance evaluation.

While the primary focus is currently on the `sink` operation, the long-term goal is to build a comprehensive ecosystem for data-centric AI.

## Features

-   **Automatic Data Ingestion:** The `sink` command automatically detects the dataset type (e.g., COCO, YOLO, CSV) and infers the optimal way to ingest the data into Lance.
-   **Rich Metadata Extraction:** Atlas extracts a wide range of metadata from your datasets, including image dimensions, class names, captions, and keypoints.
-   **Self-Contained Datasets:** All data, including images and other binary assets, is stored directly in the Lance dataset, making it easy to share and version your data.
-   **Extensible Architecture:** The framework is designed to be easily extensible, allowing you to add support for new data formats, tasks, and indexing strategies.
-   **Command-Line and Python API:** Atlas provides both a simple and intuitive command-line interface and a powerful Python API for programmatic access.

## Installation

```bash
pip install atlas-ai
```

## Usage

### Command-Line Interface

The `atlas` CLI provides a simple way to interact with your datasets.

#### Sinking a Dataset

To sink a dataset, simply point the `atlas sink` command to your data source. Atlas will automatically infer the dataset type and create a Lance dataset in the same directory.

<details>
<summary>Sink Syntax</summary>

#### Object Detection

-   **COCO:** Provide the path to the annotation `.json` file.
    ```bash
    atlas sink /path/to/your/coco_annotations.json
    ```
-   **YOLO:** Provide the path to the dataset directory.
    ```bash
    atlas sink /path/to/your/yolo_dataset/
    ```

#### Segmentation

-   **COCO:** Provide the path to the annotation `.json` file.
    ```bash
    atlas sink /path/to/your/coco_annotations.json
    ```

#### Tabular

-   **CSV:** Provide the path to the `.csv` file.
    ```bash
    atlas sink /path/to/your/data.csv
    ```
-   **Parquet:** Provide the path to the `.parquet` file.
    ```bash
    atlas sink /path/to/your/data.parquet
    ```

</details>

<details>
<summary>Manual Sink / Build on Top</summary>

You can also import specific task types and use them directly or even subclass them for more advanced use cases.

```python
from atlas.tasks.object_detection import COCOObjectDetection

# Initialize the task
coco_task = COCOObjectDetection(name="my_coco_task")

# Sink the dataset
coco_task.sink("/path/to/your/coco_annotations.json", "/path/to/your/dataset.lance")
```

</details>

#### Visualizing a Dataset

To visualize a few samples from your dataset, use the `atlas visualize` command:

```bash
atlas visualize /path/to/your/dataset.lance --num-samples 10
```

### Python API

The `atlas` Python API provides more control and flexibility for advanced use cases.

```python
import atlas

# Sink a dataset
atlas.sink("/path/to/your/coco_dataset/")

# Sink a dataset with specific options
atlas.sink("/path/to/your/data", uri="/path/to/your/dataset.lance", options={"task": "object_detection", "format": "coco"})

# Visualize a dataset
atlas.visualize("/path/to/your/dataset.lance", num_samples=10)
```

## Future Development

Atlas is under active development, with a focus on expanding its capabilities to support a wider range of tasks and data modalities. Future plans include:

-   **LLM/VLM Dataset Support:** Adding support for pre-training and post-training datasets for Large Language Models (LLMs) and Vision-Language Models (VLMs).
-   **Advanced Indexing:** Implementing advanced indexing strategies, such as vector search and metadata filtering, to enable fast and efficient data retrieval.
-   **Data Analysis and Visualization:** Building a suite of tools for analyzing and visualizing datasets, including embedding analysis, data distribution analysis, and model performance evaluation.

## Contributing

Contributions are welcome! Please see the contributing guide for more information.

## License

Atlas is licensed under the Apache License, Version 2.0. See the LICENSE file for more information.
