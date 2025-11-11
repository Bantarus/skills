#!/usr/bin/env python3
"""
Batch Segmentation with Bounding Box Prompts

This script demonstrates efficient batch processing of multiple images with
bounding box prompts using EdgeTAM. Useful for processing large datasets of
annotated images.

Usage:
    python bbox_batch_segmentation.py \
        --images_dir ./images \
        --boxes_file ./boxes.json \
        --output_dir ./masks \
        --batch_size 8

boxes.json format:
{
    "image1.jpg": [[x_min, y_min, x_max, y_max], ...],
    "image2.jpg": [[x_min, y_min, x_max, y_max], ...],
    ...
}
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List
import numpy as np
from PIL import Image
import torch
from transformers import EdgeTamModel, Sam2Processor
from tqdm import tqdm


def load_boxes(boxes_file: str) -> Dict[str, List[List[int]]]:
    """Load bounding boxes from JSON file."""
    with open(boxes_file, 'r') as f:
        return json.load(f)


def process_batch(
    model: EdgeTamModel,
    processor: Sam2Processor,
    images: List[Image.Image],
    boxes: List[List[List[int]]],
    device: str
) -> List[torch.Tensor]:
    """Process a batch of images with their bounding boxes."""
    inputs = processor(images=images, input_boxes=boxes, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model(**inputs, multimask_output=False)
    
    masks = processor.post_process_masks(
        outputs.pred_masks.cpu(),
        inputs["original_sizes"],
        binarize=True
    )
    
    return masks


def save_masks(masks: torch.Tensor, output_path: str, image_name: str):
    """Save segmentation masks to disk."""
    # masks shape: (num_objects, 1, H, W)
    num_objects = masks.shape[0]
    
    if num_objects == 1:
        # Single object: save as single mask
        mask = masks[0, 0].numpy().astype(np.uint8) * 255
        Image.fromarray(mask).save(output_path)
    else:
        # Multiple objects: save separately
        base_name = Path(image_name).stem
        output_dir = Path(output_path).parent
        
        for i in range(num_objects):
            mask = masks[i, 0].numpy().astype(np.uint8) * 255
            obj_output_path = output_dir / f"{base_name}_obj{i}.png"
            Image.fromarray(mask).save(obj_output_path)


def main():
    parser = argparse.ArgumentParser(description="Batch segmentation with bounding boxes")
    parser.add_argument("--images_dir", type=str, required=True, help="Directory containing input images")
    parser.add_argument("--boxes_file", type=str, required=True, help="JSON file with bounding boxes")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory for output masks")
    parser.add_argument("--model", type=str, default="yonigozlan/EdgeTAM-hf", help="Model name or path")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size for processing")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load model
    print(f"Loading model: {args.model}")
    model = EdgeTamModel.from_pretrained(args.model).to(args.device)
    processor = Sam2Processor.from_pretrained(args.model)
    model.eval()
    
    # Load bounding boxes
    print(f"Loading bounding boxes from: {args.boxes_file}")
    all_boxes = load_boxes(args.boxes_file)
    
    # Prepare batch data
    image_names = list(all_boxes.keys())
    total_images = len(image_names)
    print(f"Processing {total_images} images in batches of {args.batch_size}")
    
    # Process in batches
    for i in tqdm(range(0, total_images, args.batch_size), desc="Processing batches"):
        batch_names = image_names[i:i+args.batch_size]
        
        # Load images and boxes for this batch
        batch_images = []
        batch_boxes = []
        
        for name in batch_names:
            img_path = os.path.join(args.images_dir, name)
            if not os.path.exists(img_path):
                print(f"Warning: Image not found: {img_path}")
                continue
            
            img = Image.open(img_path).convert("RGB")
            batch_images.append(img)
            batch_boxes.append(all_boxes[name])
        
        if not batch_images:
            continue
        
        # Process batch
        try:
            batch_masks = process_batch(model, processor, batch_images, batch_boxes, args.device)
            
            # Save results
            for name, masks in zip(batch_names, batch_masks):
                output_path = os.path.join(args.output_dir, name.replace('.jpg', '.png').replace('.jpeg', '.png'))
                save_masks(masks, output_path, name)
        
        except Exception as e:
            print(f"Error processing batch starting at {batch_names[0]}: {e}")
            continue
    
    print(f"Done! Masks saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
