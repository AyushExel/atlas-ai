import click

@click.group()
def main():
    pass

@main.command()
@click.argument('data', type=click.Path(exists=True))
@click.argument('uri', required=False)
@click.option('--task', help="The task type (e.g., 'object_detection', 'segmentation').")
@click.option('--format', help="The data format (e.g., 'coco', 'yolo').")
def sink(data, uri, task, format):
    """
    Sinks data from a given source to a specified destination in Lance format.

    DATA: The path to the data source (e.g., a CSV file, a COCO annotation file, or a directory for YOLO).
    URI: The destination URI for the Lance dataset. If not provided, it will be inferred from the data source path.
    """
    options = {}
    if task:
        options['task'] = task
    if format:
        options['format'] = format

    from atlas.data_sinks import sink as sink_func
    sink_func(data, uri, options=options)

@main.command()
@click.argument('uri')
@click.option('--num-samples', default=5)
def visualize(uri, num_samples):
    """Visualizes a few samples from a Lance dataset."""
    from atlas.visualizers.visualizer import visualize as visualize_func
    visualize_func(uri, num_samples)

if __name__ == '__main__':
    main()
