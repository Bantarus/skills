#!/usr/bin/env python3
"""
Video Object Tracking with EdgeTAM

This script demonstrates video object tracking using EdgeTAM. Supports multiple
objects, refinement on key frames, and visualization of tracking results.

Usage:
    python video_object_tracker.py \
        --video ./input_video.mp4 \
        --prompts ./prompts.json \
        --output_dir ./tracking_results \
        --visualize

prompts.json format:
{
    "objects": [
        {
            "id": 1,
            "frame": 0,
            "box": [x_min, y_min, x_max, y_max]
        },
        {
            "id": 2,
            "frame": 0,
            "points": [[x, y]],
            "labels": [1]
        }
    ],
    "refinements": [
        {
            "object_id": 1,
            "frame": 50,
            "points": [[x, y]],
            "labels": [1]
        }
    ]
}
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import cv2
import numpy as np
import torch
from transformers import EdgeTamVideoModel, Sam2VideoProcessor
from transformers.video_utils import load_video
from tqdm import tqdm


def load_prompts(prompts_file: str) -> Dict:
    """Load prompts and refinements from JSON file."""
    with open(prompts_file, 'r') as f:
        return json.load(f)


def apply_mask_overlay(frame: np.ndarray, mask: np.ndarray, color: tuple, alpha: float = 0.5) -> np.ndarray:
    """Apply colored mask overlay to frame."""
    overlay = frame.copy()
    overlay[mask > 0] = color
    return cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)


def draw_bbox(frame: np.ndarray, mask: np.ndarray, color: tuple, label: str = ""):
    """Draw bounding box around mask."""
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        if label:
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame


def visualize_frame(
    frame: np.ndarray,
    masks: Dict[int, torch.Tensor],
    colors: Dict[int, tuple],
    frame_idx: int
) -> np.ndarray:
    """Visualize tracked objects on a frame."""
    vis_frame = frame.copy()
    
    for obj_id, mask in masks.items():
        color = colors.get(obj_id, (255, 0, 0))
        mask_np = mask.squeeze().numpy() > 0
        vis_frame = apply_mask_overlay(vis_frame, mask_np, color)
        vis_frame = draw_bbox(vis_frame, mask_np, color, f"ID:{obj_id}")
    
    # Add frame number
    cv2.putText(vis_frame, f"Frame: {frame_idx}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return vis_frame


def generate_colors(num_objects: int) -> Dict[int, tuple]:
    """Generate distinct colors for each object."""
    colors = {}
    for i in range(num_objects):
        hue = int(180 * i / num_objects)
        color = cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2BGR)[0][0]
        colors[i + 1] = tuple(map(int, color))
    return colors


def track_video(
    video_model: EdgeTamVideoModel,
    video_processor: Sam2VideoProcessor,
    video_frames: List,
    prompts: Dict,
    device: str,
    visualize: bool = False,
    output_dir: Optional[str] = None
):
    """Track objects through video."""
    # Initialize session
    inference_session = video_processor.init_video_session(
        video=video_frames,
        inference_device=device,
        torch_dtype=torch.bfloat16,
    )
    
    # Generate colors for visualization
    num_objects = len(prompts["objects"])
    colors = generate_colors(num_objects)
    
    # Add initial objects
    print("Adding initial objects...")
    for obj in prompts["objects"]:
        obj_id = obj["id"]
        frame_idx = obj["frame"]
        
        if "box" in obj:
            video_processor.add_inputs_to_inference_session(
                inference_session=inference_session,
                frame_idx=frame_idx,
                obj_ids=obj_id,
                input_boxes=[[[obj["box"]]]],
            )
        elif "points" in obj:
            video_processor.add_inputs_to_inference_session(
                inference_session=inference_session,
                frame_idx=frame_idx,
                obj_ids=obj_id,
                input_points=[[obj["points"]]],
                input_labels=[[obj["labels"]]],
            )
    
    # Add refinements if any
    if "refinements" in prompts:
        print("Adding refinements...")
        for refine in prompts["refinements"]:
            video_processor.add_inputs_to_inference_session(
                inference_session=inference_session,
                frame_idx=refine["frame"],
                obj_ids=refine["object_id"],
                input_points=[[refine["points"]]],
                input_labels=[[refine["labels"]]],
            )
    
    # Propagate through video
    print("Tracking objects through video...")
    video_segments = {}
    
    if visualize and output_dir:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_video = cv2.VideoWriter(
            os.path.join(output_dir, 'tracked_video.mp4'),
            fourcc, 30.0,
            (video_frames[0].size[0], video_frames[0].size[1])
        )
    
    for edgetam_video_output in tqdm(video_model.propagate_in_video_iterator(inference_session), 
                                      total=len(video_frames), desc="Tracking"):
        frame_idx = edgetam_video_output.frame_idx
        
        video_res_masks = video_processor.post_process_masks(
            [edgetam_video_output.pred_masks],
            original_sizes=[[inference_session.video_height, inference_session.video_width]],
            binarize=False
        )[0]
        
        # Store masks per object
        frame_masks = {
            obj_id: video_res_masks[i]
            for i, obj_id in enumerate(inference_session.obj_ids)
        }
        video_segments[frame_idx] = frame_masks
        
        # Visualize if requested
        if visualize and output_dir:
            frame_np = np.array(video_frames[frame_idx])
            frame_np = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
            vis_frame = visualize_frame(frame_np, frame_masks, colors, frame_idx)
            out_video.write(vis_frame)
            
            # Save individual frame
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{frame_idx:05d}.jpg'),
                vis_frame
            )
    
    if visualize and output_dir:
        out_video.release()
    
    return video_segments


def save_masks(video_segments: Dict, output_dir: str):
    """Save masks to disk in numpy format."""
    masks_dir = os.path.join(output_dir, 'masks')
    os.makedirs(masks_dir, exist_ok=True)
    
    for frame_idx, frame_masks in video_segments.items():
        for obj_id, mask in frame_masks.items():
            mask_np = mask.squeeze().cpu().numpy()
            output_path = os.path.join(masks_dir, f'frame_{frame_idx:05d}_obj_{obj_id}.npy')
            np.save(output_path, mask_np)
    
    print(f"Masks saved to: {masks_dir}")


def main():
    parser = argparse.ArgumentParser(description="Video object tracking with EdgeTAM")
    parser.add_argument("--video", type=str, required=True, help="Path to input video")
    parser.add_argument("--prompts", type=str, required=True, help="JSON file with prompts")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory for output")
    parser.add_argument("--model", type=str, default="yonigozlan/EdgeTAM-hf", help="Model name or path")
    parser.add_argument("--visualize", action="store_true", help="Create visualization video")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load model
    print(f"Loading model: {args.model}")
    video_model = EdgeTamVideoModel.from_pretrained(args.model).to(args.device, dtype=torch.bfloat16)
    video_processor = Sam2VideoProcessor.from_pretrained(args.model)
    video_model.eval()
    
    # Load video
    print(f"Loading video: {args.video}")
    video_frames, fps = load_video(args.video)
    print(f"Loaded {len(video_frames)} frames at {fps} FPS")
    
    # Load prompts
    print(f"Loading prompts from: {args.prompts}")
    prompts = load_prompts(args.prompts)
    
    # Track objects
    video_segments = track_video(
        video_model,
        video_processor,
        video_frames,
        prompts,
        args.device,
        visualize=args.visualize,
        output_dir=args.output_dir
    )
    
    # Save masks
    save_masks(video_segments, args.output_dir)
    
    print(f"Done! Results saved to: {args.output_dir}")
    if args.visualize:
        print(f"Visualization video: {os.path.join(args.output_dir, 'tracked_video.mp4')}")


if __name__ == "__main__":
    main()
