#!/usr/bin/env python3
"""
Interactive Segmentation with EdgeTAM

This script provides an interactive interface for refining segmentation masks
using mouse clicks. Useful for creating high-quality annotations.

Usage:
    python interactive_segmentation.py \
        --image ./image.jpg \
        --initial_box 100,100,500,500 \
        --output ./mask.png

Controls:
    - Left click: Add positive point (include region)
    - Right click: Add negative point (exclude region)
    - 'r': Reset to initial segmentation
    - 's': Save current mask
    - 'q': Quit

Requirements:
    pip install opencv-python matplotlib
"""

import argparse
from typing import List, Tuple
import cv2
import numpy as np
import torch
from PIL import Image
from transformers import EdgeTamModel, Sam2Processor
import matplotlib.pyplot as plt


class InteractiveSegmenter:
    def __init__(
        self,
        model: EdgeTamModel,
        processor: Sam2Processor,
        image: Image.Image,
        initial_box: List[int],
        device: str
    ):
        self.model = model
        self.processor = processor
        self.image = image
        self.image_np = np.array(image)
        self.initial_box = initial_box
        self.device = device
        
        # Click history
        self.positive_points = []
        self.negative_points = []
        
        # State
        self.current_mask = None
        self.image_embeddings = None
        self.original_sizes = None
        
        # Initialize with bounding box
        self._initialize_segmentation()
    
    def _initialize_segmentation(self):
        """Initialize segmentation with bounding box."""
        inputs = self.processor(
            images=self.image,
            input_boxes=[[self.initial_box]],
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Get best mask
        best_mask_idx = torch.argmax(outputs.iou_scores.squeeze())
        self.current_mask = outputs.pred_masks[:, :, best_mask_idx]
        self.image_embeddings = outputs.image_embeddings
        self.original_sizes = inputs["original_sizes"]
        
        # Post-process for display
        display_masks = self.processor.post_process_masks(
            self.current_mask.cpu(),
            self.original_sizes,
            binarize=True
        )[0]
        self.display_mask = display_masks[0, 0].numpy()
    
    def add_point(self, x: int, y: int, is_positive: bool):
        """Add a refinement point and update segmentation."""
        if is_positive:
            self.positive_points.append([x, y])
        else:
            self.negative_points.append([x, y])
        
        # Combine all points
        all_points = self.positive_points + self.negative_points
        all_labels = [1] * len(self.positive_points) + [0] * len(self.negative_points)
        
        if not all_points:
            return
        
        # Refine segmentation
        inputs = self.processor(
            input_points=[[[all_points]]],
            input_labels=[[[all_labels]]],
            original_sizes=self.original_sizes,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(
                **inputs,
                input_masks=self.current_mask,
                image_embeddings=self.image_embeddings,
                multimask_output=False
            )
        
        self.current_mask = outputs.pred_masks
        
        # Post-process for display
        display_masks = self.processor.post_process_masks(
            self.current_mask.cpu(),
            self.original_sizes,
            binarize=True
        )[0]
        self.display_mask = display_masks[0, 0].numpy()
    
    def reset(self):
        """Reset to initial segmentation."""
        self.positive_points = []
        self.negative_points = []
        self._initialize_segmentation()
    
    def get_visualization(self) -> np.ndarray:
        """Get visualization with mask overlay and points."""
        vis = self.image_np.copy()
        
        # Apply mask overlay
        mask_overlay = np.zeros_like(vis)
        mask_overlay[self.display_mask > 0] = [0, 255, 0]  # Green
        vis = cv2.addWeighted(vis, 0.7, mask_overlay, 0.3, 0)
        
        # Draw contours
        contours, _ = cv2.findContours(
            self.display_mask.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(vis, contours, -1, (0, 255, 0), 2)
        
        # Draw points
        for point in self.positive_points:
            cv2.circle(vis, tuple(point), 5, (0, 255, 0), -1)  # Green for positive
            cv2.circle(vis, tuple(point), 7, (255, 255, 255), 2)  # White border
        
        for point in self.negative_points:
            cv2.circle(vis, tuple(point), 5, (0, 0, 255), -1)  # Red for negative
            cv2.circle(vis, tuple(point), 7, (255, 255, 255), 2)  # White border
        
        # Add instructions
        cv2.putText(vis, "Left: Positive | Right: Negative | R: Reset | S: Save | Q: Quit",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return vis
    
    def save_mask(self, output_path: str):
        """Save current mask."""
        mask_img = (self.display_mask * 255).astype(np.uint8)
        Image.fromarray(mask_img).save(output_path)
        print(f"Mask saved to: {output_path}")


def mouse_callback(event, x, y, flags, param):
    """Handle mouse events."""
    segmenter, window_name = param
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Positive click
        segmenter.add_point(x, y, is_positive=True)
        vis = segmenter.get_visualization()
        cv2.imshow(window_name, vis)
    
    elif event == cv2.EVENT_RBUTTONDOWN:
        # Negative click
        segmenter.add_point(x, y, is_positive=False)
        vis = segmenter.get_visualization()
        cv2.imshow(window_name, vis)


def parse_box(box_str: str) -> List[int]:
    """Parse bounding box from string."""
    return [int(x) for x in box_str.split(',')]


def main():
    parser = argparse.ArgumentParser(description="Interactive segmentation with EdgeTAM")
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument("--initial_box", type=str, required=True, 
                        help="Initial bounding box as x_min,y_min,x_max,y_max")
    parser.add_argument("--output", type=str, default="mask.png", help="Output mask path")
    parser.add_argument("--model", type=str, default="yonigozlan/EdgeTAM-hf", help="Model name or path")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    
    # Load model
    print(f"Loading model: {args.model}")
    model = EdgeTamModel.from_pretrained(args.model).to(args.device)
    processor = Sam2Processor.from_pretrained(args.model)
    model.eval()
    
    # Load image
    print(f"Loading image: {args.image}")
    image = Image.open(args.image).convert("RGB")
    
    # Parse initial box
    initial_box = parse_box(args.initial_box)
    print(f"Initial box: {initial_box}")
    
    # Create segmenter
    segmenter = InteractiveSegmenter(model, processor, image, initial_box, args.device)
    
    # Setup window
    window_name = "Interactive Segmentation - EdgeTAM"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback, (segmenter, window_name))
    
    # Display initial result
    vis = segmenter.get_visualization()
    cv2.imshow(window_name, vis)
    
    print("Interactive mode started!")
    print("Controls:")
    print("  - Left click: Add positive point")
    print("  - Right click: Add negative point")
    print("  - 'r': Reset to initial segmentation")
    print("  - 's': Save current mask")
    print("  - 'q': Quit")
    
    # Main loop
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            # Quit
            break
        
        elif key == ord('r'):
            # Reset
            segmenter.reset()
            vis = segmenter.get_visualization()
            cv2.imshow(window_name, vis)
            print("Reset to initial segmentation")
        
        elif key == ord('s'):
            # Save
            segmenter.save_mask(args.output)
    
    cv2.destroyAllWindows()
    print("Done!")


if __name__ == "__main__":
    main()
