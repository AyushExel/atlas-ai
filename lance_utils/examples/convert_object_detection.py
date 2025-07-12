# examples/convert_object_detection.py

import os
import json
from pathlib import Path
import urllib.request
import zipfile
import shutil
from PIL import Image
import numpy as np
import argparse
from atlas.builder import LanceWriter
from atlas.tasks.object_detection.base import ObjectDetection
import lance
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import io

def download_and_extract(url: str, download_path: Path, extract_path: Path, reuse: bool = False):
    """Downloads and extracts a zip file."""
    if not shutil.which("unzip"):
        print("Error: 'unzip' command not found. Please install it.")
        return
    
    if not download_path.exists():
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, download_path)
    else:
        print("Download file already exists. Skipping download.")

    if extract_path.exists():
        if reuse:
            print(f"Extract path {extract_path} already exists. Reusing.")
            return
        else:
            print(f"Removing existing directory {extract_path}...")
            shutil.rmtree(extract_path)
    print(f"Extracting to {extract_path}...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

def create_coco_annotations_from_masks(data_path: Path):
    """
    Creates a COCO-style annotations.json file from the raw masks
    provided in the Penn-Fudan dataset.
    """
    annotations_file = data_path / "annotations.json"
    if annotations_file.exists():
        print("annotations.json already exists. Skipping creation.")
        return

    print("Generating COCO-style annotations from masks...")
    images_dir = data_path / "PNGImages"
    masks_dir = data_path / "PedMasks"
    
    coco_data = {
        "images": [],
        "annotations": [],
        "categories": [{"id": 1, "name": "pedestrian"}]
    }
    
    ann_id = 1
    for img_id, img_path in enumerate(sorted(images_dir.glob("*.png"))):
        mask_path = masks_dir / f"{img_path.stem}_mask.png"
        if not mask_path.exists():
            continue

        with Image.open(img_path) as img:
            width, height = img.size
        
        coco_data["images"].append({
            "id": img_id,
            "file_name": img_path.name,
            "width": width,
            "height": height
        })

        mask = np.array(Image.open(mask_path))
        obj_ids = np.unique(mask)[1:]

        for obj_id in obj_ids:
            pos = np.where(mask == obj_id)
            xmin = int(np.min(pos[1]))
            xmax = int(np.max(pos[1]))
            ymin = int(np.min(pos[0]))
            ymax = int(np.max(pos[0]))
            
            bbox = [xmin, ymin, xmax - xmin, ymax - ymin]
            
            coco_data["annotations"].append({
                "id": ann_id,
                "image_id": img_id,
                "category_id": 1,
                "bbox": bbox,
                "area": bbox[2] * bbox[3],
                "iscrowd": 0
            })
            ann_id += 1
            
    with open(annotations_file, "w") as f:
        json.dump(coco_data, f, indent=2)

def debug_read_lance_dataset(path: Path):
    print(f"--- DEBUG: Reading Lance dataset from {path} ---")
    if not path.exists():
        print("DEBUG: Dataset path does not exist.")
        return
    dataset = lance.dataset(str(path))
    print(f"DEBUG: Num rows: {dataset.count_rows()}")
    print(f"DEBUG: Schema: {dataset.schema}")
    
    try:
        table = dataset.to_table(limit=5)
        print("DEBUG: First 5 rows:")
        print(table.to_pydict())
    except Exception as e:
        print(f"DEBUG: Error reading table: {e}")
    print("--- END DEBUG ---")

def manual_visualize(dataset_path: Path, num_images: int = 4):
    """Manually visualizes a few images and their bounding boxes from the dataset."""
    print(f"--- Starting Manual Visualization ---")
    dataset = lance.dataset(str(dataset_path))
    
    sample = dataset.to_table(limit=num_images).to_pylist()
    if not sample:
        print("No data to visualize.")
        return

    num_cols = 2
    num_rows_plot = math.ceil(len(sample) / num_cols)
    fig, axs = plt.subplots(num_rows_plot, num_cols, figsize=(12, 6 * num_rows_plot), squeeze=False)

    for i, item in enumerate(sample):
        row = i // num_cols
        col = i % num_cols
        ax = axs[row, col]

        image_bytes = item.get("image")
        if not image_bytes:
            ax.text(0.5, 0.5, "No Image Data", ha='center')
            ax.axis("off")
            continue

        try:
            image = Image.open(io.BytesIO(image_bytes))
            ax.imshow(image)
            ax.set_title(item.get("filename") or f"Image {i+1}", fontsize=10)
            
            if "bounding_boxes" in item and item["bounding_boxes"]:
                for ann in item["bounding_boxes"]:
                    box = ann['bbox']
                    rect = patches.Rectangle(
                        (box[0], box[1]), box[2], box[3],
                        linewidth=2, edgecolor='lime', facecolor='none'
                    )
                    ax.add_patch(rect)
                    if 'category_id' in ann:
                        ax.text(box[0], box[1] - 10, f"ID: {ann['category_id']}", 
                                color='white', backgroundcolor='lime', fontsize=8)

        except Exception as e:
            ax.text(0.5, 0.5, f"Error loading image\n{e}", ha='center')
        
        ax.axis("off")

    for i in range(len(sample), num_cols * num_rows_plot):
        axs.flat[i].axis("off")

    plt.tight_layout()
    
    output_path = dataset_path.parent / "manual_visualization.png"
    plt.savefig(output_path)
    plt.close(fig)
    
    print(f"Manual visualization saved to: {output_path}")
    print(f"--- Finished Manual Visualization ---")


def main():
    parser = argparse.ArgumentParser(description="Convert Penn-Fudan dataset for object detection.")
    parser.add_argument('--reuse', action='store_true', help='Reuse existing extracted data and images directory if present (default: overwrite)')
    args = parser.parse_args()
    reuse = args.reuse
    # Setup
    temp_dir = Path("temp_data")
    temp_dir.mkdir(exist_ok=True)
    
    dataset_url = "https://www.cis.upenn.edu/~jshi/ped_html/PennFudanPed.zip"
    zip_path = temp_dir / "PennFudanPed.zip"
    extract_path = temp_dir / "PennFudanPed_extracted"
    
    # Download and extract
    download_and_extract(dataset_url, zip_path, extract_path, reuse=reuse)
    
    # The actual data is in a subdirectory
    penn_fudan_path = extract_path / "PennFudanPed"
    if not penn_fudan_path.exists():
        print(f"Error: {penn_fudan_path} not found after extraction.")
        return

    # Prepare data (convert masks to COCO bboxes)
    create_coco_annotations_from_masks(penn_fudan_path)
    
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "penn_fudan_detection.lance"

    # Use lance_utils to build the dataset
    print("\nBuilding Lance dataset...")
    task = ObjectDetection(input_path=str(penn_fudan_path))
    writer = LanceWriter(output_path=str(output_path), task=task)
    writer.write()
    
    print(f"\nConversion complete!")
    print(f"Dataset saved to {output_path}")
    
    # --- Manual Visualization ---
    manual_visualize(output_path)

    # --- Debug Print ---
    debug_read_lance_dataset(output_path)

    # Clean up
    # shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
