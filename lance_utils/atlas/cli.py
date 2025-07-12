# lance_utils/cli.py
import click
from .builder import LanceWriter
from .visualizer import LanceVisualizer
from .tasks.base import Task
from .tasks.object_detection.base import ObjectDetectionTask

@click.group()
def cli():
    """A CLI for building, inspecting, and visualizing Lance datasets."""
    pass

@cli.command()
@click.option("-i", "--input-path", required=True, help="Path to the source data directory.")
@click.option("-o", "--output-path", required=True, help="Path to save the Lance dataset.")
@click.option("-b", "--batch-size", default=128, type=int, help="Batch size for conversion.")
def build(input_path: str, output_path: str, batch_size: int):
    """Builds a Lance dataset from a source directory by auto-detecting all supported annotations."""
    # For now, we'll just assume the task is object detection
    task = ObjectDetectionTask(input_path)
    writer = LanceWriter(output_path, task, batch_size)
    writer.write()

@cli.command()
@click.option("-i", "--input-path", required=True, help="Path to the Lance dataset.")
def inspect(input_path: str):
    """Inspects a Lance dataset and prints its schema."""
    visualizer = LanceVisualizer(input_path)
    visualizer.inspect()

@cli.command()
@click.option("-i", "--input-path", required=True, help="Path to the Lance dataset.")
@click.option("-n", "--num-rows", default=10, type=int, help="Number of rows to visualize.")
def visualize(input_path: str, num_rows: int):
    """Visualizes a sample of a Lance dataset."""
    visualizer = LanceVisualizer(input_path)
    visualizer.visualize(num_rows)

if __name__ == "__main__":
    cli()