# Atlas

<p align="center">
  <img src="https://storage.googleapis.com/atlas-resources/logo.png" alt="Atlas Logo" width="200"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/atlas-ai/">
    <img src="https://img.shields.io/pypi/v/atlas-ai.svg" alt="PyPI Version">
  </a>
  <a href="https://github.com/your-repo/atlas/actions">
    <img src="https://github.com/your-repo/atlas/workflows/CI/badge.svg" alt="CI">
  </a>
  <a href="https://codecov.io/gh/your-repo/atlas">
    <img src="https://codecov.io/gh/your-repo/atlas/branch/main/graph/badge.svg" alt="Codecov">
  </a>
</p>

Atlas is a data-centric AI framework for curating, indexing, and analyzing massive datasets for deep learning applications. It provides a suite of tools to streamline the entire data lifecycle, from initial data ingestion to model training and analysis.

## Core Operations

The vision for Atlas is to provide a comprehensive solution for managing large-scale datasets in AI development. The framework is built around three core operations:

-   **Sink:** Ingest data from any source and format into an optimized Lance dataset.
-   **Index:** Create powerful, multi-modal indexes on your data to enable fast and efficient search and retrieval.
-   **Analyse:** Analyse your datasets to gain insights, identify patterns, and debug your models.

---

# Sink

The **Sink** operation allows you to ingest data from any source and format into an optimized [Lance](https://lancedb.github.io/lance/) dataset. Atlas automatically infers the dataset type, extracts rich metadata, and stores the data in a self-contained, portable format.

Here's a high-level overview of the sinking process:

```
        +-----------------------+      +----------------------+      +---------------------+
        |   Raw Data Sources    |      |      Atlas Sink      |      |   Lance Dataset     |
        |  (COCO, YOLO, CSV)    |----->|  (Auto-detection,    |----->|  (Optimized Storage)|
        |                       |      |   Metadata Extraction)|      |                     |
        +-----------------------+      +----------------------+      +---------------------+
```

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

### CLI

The `atlas` CLI provides a simple way to interact with your datasets.

**Object Detection (COCO)**

```bash
atlas sink examples/data/coco/annotations/instances_val2017_small.json
```

<p align="center">
  <img src="examples/data/coco_visualization.png" alt="COCO Visualization" width="500"/>
</p>

<details>
<summary>Click to see schema and sample data</summary>

**Schema:**
```
- image: binary
- bbox: list<item: list<item: float>>
- label: list<item: int64>
- keypoints: list<item: list<item: float>>
- captions: list<item: string>
- height: int64
- width: int64
- file_name: string
```

**Sample Data:**
```
+------------------------------------+------------------+---------+----------+------------------------------------------------------------+----------------------------------------------------------+
| image                              | file_name        |   width |   height | label                                                      | bbox                                                     |
+====================================+==================+=========+==========+============================================================+==========================================================+
| b'\xff\xd8\xff\xe0\x00\x10JFIF'... | 000000397133.jpg |     640 |      427 | [44 67  1 49 51 51 79  1 47 47 51 51 56 50 56 56 79 57 81] | [array([217.62, 240.54,  38.99,  57.75], dtype=float32)  |
+------------------------------------+------------------+---------+----------+------------------------------------------------------------+----------------------------------------------------------+
```
</details>

<details>
<summary>Object Detection (YOLO)</summary>

```bash
atlas sink examples/data/yolo/coco128
```
<p align="center">
  <img src="examples/data/yolo_visualization.png" alt="YOLO Visualization" width="500"/>
</p>

</details>

<details>
<summary>Segmentation (COCO)</summary>

```bash
atlas sink examples/data/coco/annotations/instances_val2017_small.json --task segmentation
```
<p align="center">
  <img src="examples/data/coco_segmentation_visualization.png" alt="COCO Segmentation Visualization" width="500"/>
</p>

</details>

<details>
<summary>Tabular (CSV)</summary>

```bash
atlas sink examples/data/dummy.csv
```

</details>

### Python API

The `atlas` Python API provides more control and flexibility for advanced use cases.

**Object Detection (COCO)**
```python
import atlas
atlas.sink("examples/data/coco/annotations/instances_val2017_small.json")
```

<details>
<summary>Object Detection (YOLO)</summary>

```python
import atlas
atlas.sink("examples/data/yolo/coco128")
```
</details>

<details>
<summary>Segmentation (COCO)</summary>

```python
import atlas
atlas.sink("examples/data/coco/annotations/instances_val2017_small.json", options={"task": "segmentation"})
```
</details>

<details>
<summary>Tabular (CSV)</summary>

```python
import atlas
atlas.sink("examples/data/dummy.csv")
```
</details>

<details>
<summary>Manual Sink / Build on Top</summary>

You can also import specific task types and use them directly or even subclass them for more advanced use cases. For example, let's create a custom sink that adds an `image_url` to the COCO dataset.

```python
from atlas.tasks.object_detection.coco import CocoDataset
import pyarrow as pa

class CocoDatasetWithImageURL(CocoDataset):
    def __init__(self, data: str, options: dict = None):
        super().__init__(data, options)
        self.base_url = "http://images.cocodataset.org/val2017/"

    def to_batches(self, batch_size: int = 1024):
        for batch in super().to_batches(batch_size):
            file_names = batch.column("file_name").to_pylist()
            image_urls = [self.base_url + file_name for file_name in file_names]
            yield batch.add_column(0, pa.field("image_url", pa.string()), pa.array(image_urls, type=pa.string()))

# Usage
from atlas.data_sinks import sink
sink(data_class=CocoDatasetWithImageURL, data="examples/data/coco/annotations/instances_val2017_small.json", uri="coco_with_url.lance")
```

</details>

```