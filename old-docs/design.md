# Atlas Design Document

## 1. Introduction

This document outlines the design of the Atlas library, a Python library for sinking data from various sources into the Lance format. The goal of Atlas is to provide a simple, efficient, and extensible way to convert datasets into self-contained Lance datasets, enabling users to leverage the power of Lance for their data-centric AI workflows.

## 2. Core Concepts

### 2.1. Sink

The `sink` function is the main entry point of the library. It takes a data source, a destination URI, and an optional set of options, and it sinks the data from the source to the destination. The data source can be a file path or a `BaseDataset` object.

### 2.2. BaseDataset

The `BaseDataset` class is an abstract base class that represents a dataset. It defines a common interface for all datasets, including methods for converting the dataset to Lance format and for iterating over the dataset in batches of Arrow `RecordBatch` objects.

### 2.3. Dataset Factory

The `create_dataset` function is a factory that creates a `BaseDataset` object based on the given data source and options. This allows for a flexible and extensible way to add support for new data formats and tasks.

### 2.4. Tasks

Atlas supports various data-centric AI tasks. For each task, there can be multiple data formats. The currently supported tasks and formats are:

- **Tabular:**
    - CSV (`.csv`)
    - Parquet (`.parquet`)
- **Object Detection:**
    - COCO (`.json`)
    - YOLO (directory with `.jpg`, `.png`, `.jpeg`, and `.txt` files)
- **Segmentation:**
    - COCO (`.json`)

### 2.5. Visualizer

The `visualize` function allows users to inspect and visualize a few samples from a Lance dataset. It can display images with bounding boxes and segmentation masks.

## 3. Architecture

The Atlas library is designed with a modular and extensible architecture. The core components of the library are:

- **Data Sinks:** The `data_sinks` module contains the `sink` function, which is the main entry point of the library.
- **Tasks:** The `tasks` module contains the data models and parsers for the supported tasks and formats. Each supported format has its own `BaseDataset` subclass.
- **Visualizers:** The `visualizers` module contains the `visualize` function for inspecting and visualizing datasets.
- **Utils:** The `utils` module contains utility functions, such as the dynamic batch size calculator.
- **CLI:** The `cli` module provides a command-line interface for the `sink` and `visualize` functions.

## 4. Data Ingestion

Atlas uses Apache Arrow's `RecordBatch` generator streams for ingesting data into Lance. This approach allows for the processing of datasets that are larger than memory, as the data is read and written in batches. The batch size is dynamically calculated based on the available system memory to optimize performance and stability. For file formats that do not natively support batching (e.g., CSV), the data is read into a pandas DataFrame and then converted to a Lance dataset.

## 5. Self-Contained Datasets

To ensure that the created Lance datasets are self-contained and portable, Atlas stores images and other binary data directly within the dataset using the `pa.binary()` type. This eliminates the need to keep the original data source available after the dataset has been created.

## 6. Extensibility

The Atlas library is designed to be easily extensible. To add support for a new data format, you need to:

1. Create a new `BaseDataset` subclass in the appropriate `tasks` submodule.
2. Implement the `to_batches` method in the new subclass.
3. Update the `create_dataset` factory function in `atlas/tasks/data_model/factory.py` to recognize the new format.

## 7. Future Work

- **More data formats:** Add support for more data formats, such as JSON, Avro, and ORC.
- **More tasks:** Add support for more data-centric AI tasks, such as classification and natural language processing.
- **Cloud storage:** Add support for reading and writing data from cloud storage services, such as Amazon S3 and Google Cloud Storage.
- **Data transformations:** Add support for performing data transformations, such as resizing images and augmenting data, before sinking the data to Lance.
- **More robust mask creation:** Improve the mask creation for segmentation tasks to handle more complex scenarios, such as RLE encoded masks.
