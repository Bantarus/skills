---
name: edgetam-segmentation
description: Comprehensive skill for EdgeTAM (Edge Track Anything Model) integration focusing on promptable image and video segmentation with multiple bounding box instances, point-based prompts, and real-time object tracking. This skill should be used when implementing efficient on-device segmentation, tracking objects across video frames, or performing batch segmentation with multiple objects using the yonigozlan/EdgeTAM-hf HuggingFace model.
license: Complete terms in LICENSE.txt
---

# EdgeTAM Segmentation

## Overview

EdgeTAM (Edge Track Anything Model) is an optimized variant of SAM 2 designed for efficient on-device execution, achieving 22× faster performance than SAM 2 with 16 FPS on iPhone 15 Pro Max. This skill provides comprehensive guidance for implementing EdgeTAM for promptable segmentation and tracking in both images and videos, with special focus on multiple object instances using bounding boxes.

**Key Architecture:** EdgeTAM introduces a 2D Spatial Perceiver architecture that optimizes memory attention mechanisms for real-time video segmentation on edge devices. The model uses knowledge distillation from SAM 2 to achieve high accuracy with minimal inference overhead.

**Model:** Use `yonigozlan/EdgeTAM-hf` from HuggingFace Transformers library.

## When to Use This Skill

Use this skill when the task involves:

- Segmenting objects in images or videos using point clicks or bounding boxes
- Tracking multiple objects across video frames simultaneously
- Implementing real-time segmentation for edge devices or mobile applications
- Batch processing images or videos with multiple object instances
- Refining segmentation masks with iterative prompting
- Building applications requiring efficient on-device AI segmentation
- Converting bounding box annotations to precise segmentation masks

## Core Capabilities

### 1. Image Segmentation with Multiple Prompts

EdgeTAM supports various prompt types for image segmentation:

- **Point clicks** (positive/negative) for object selection
- **Bounding boxes** for region-based segmentation
- **Multiple objects** simultaneously in a single image
- **Mask refinement** using previous predictions as input

### 2. Video Object Tracking

Real-time tracking capabilities:

- **Multi-object tracking** across video frames
- **Temporal consistency** through memory attention mechanisms
- **Refinement on any frame** to improve tracking quality
- **Streaming inference** for real-time applications

### 3. Batch Processing

Efficient batch operations:

- **Batched images** with different prompts per image
- **Multiple objects per image** in batch mode
- **Variable numbers of points** per object
- **Mixed prompt types** (boxes and points) in same batch

## Installation and Setup

### Required Dependencies

Install transformers with EdgeTAM support:

```python
pip install transformers>=4.46.0 torch>=2.3.1 torchvision>=0.18.1
```

### Model Loading

```python
from transformers import EdgeTamModel, Sam2Processor
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

# For image segmentation
model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf").to(device)
processor = Sam2Processor.from_pretrained("yonigozlan/EdgeTAM-hf")

# For video tracking (use bfloat16 for efficiency)
from transformers import EdgeTamVideoModel, Sam2VideoProcessor

video_model = EdgeTamVideoModel.from_pretrained("yonigozlan/EdgeTAM-hf").to(device, dtype=torch.bfloat16)
video_processor = Sam2VideoProcessor.from_pretrained("yonigozlan/EdgeTAM-hf")
```

## Image Segmentation

### Single Bounding Box Prompt

For simple object segmentation with a bounding box:

```python
from PIL import Image
import requests

# Load image
image_url = "https://huggingface.co/datasets/hf-internal-testing/sam2-fixtures/resolve/main/truck.jpg"
raw_image = Image.open(requests.get(image_url, stream=True).raw).convert("RGB")

# Define bounding box as [x_min, y_min, x_max, y_max]
input_boxes = [[[75, 275, 1725, 850]]]

inputs = processor(images=raw_image, input_boxes=input_boxes, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model(**inputs)

# Post-process to get final masks
masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])[0]
```

**Input format:** `input_boxes` shape is `[batch_size, num_objects, 4]` where coordinates are `[x_min, y_min, x_max, y_max]`.

### Multiple Bounding Boxes for Multiple Objects

To segment multiple objects in the same image:

```python
# Define multiple bounding boxes for different objects
input_boxes = [[[75, 275, 1725, 850], [425, 600, 700, 875], [1375, 550, 1650, 800]]]

inputs = processor(images=raw_image, input_boxes=input_boxes, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model(**inputs, multimask_output=False)

masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])[0]
print(f"Generated {masks.shape[0]} masks for {len(input_boxes[0])} objects")
```

**Key point:** Set `multimask_output=False` when segmenting multiple specific objects to get one mask per object.

### Point-Based Prompts

For interactive segmentation with point clicks:

```python
# Define points for multiple objects with labels
# Dimensions: [batch_size, num_objects, num_points_per_object, 2]
input_points = [[[[500, 375]], [[650, 750]]]]  # Two objects, one point each
input_labels = [[[1], [1]]]  # Both are positive clicks (1=positive, 0=negative)

inputs = processor(images=raw_image, input_points=input_points, input_labels=input_labels, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model(**inputs, multimask_output=False)

masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])[0]
```

**Labels:**
- `1` = positive click (include this region)
- `0` = negative click (exclude this region)

### Refining Masks with Multiple Points

To refine segmentation by adding points:

```python
# Multiple points per object for refinement
input_points = [[[[500, 375], [450, 300], [550, 400]]]]  # Three points for same object
input_labels = [[[1, 1, 0]]]  # Two positive, one negative

inputs = processor(images=raw_image, input_points=input_points, input_labels=input_labels, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model(**inputs)

masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])[0]
```

### Using Previous Masks as Input

To iteratively refine segmentation:

```python
# Get initial segmentation
input_points = [[[[500, 375]]]]
input_labels = [[[1]]]
inputs = processor(images=raw_image, input_points=input_points, input_labels=input_labels, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model(**inputs)

# Select best mask based on IoU scores
mask_input = outputs.pred_masks[:, :, torch.argmax(outputs.iou_scores.squeeze())]

# Refine with additional points and mask input
new_input_points = [[[[500, 375], [450, 300]]]]
new_input_labels = [[[1, 1]]]
inputs = processor(
    input_points=new_input_points,
    input_labels=new_input_labels,
    original_sizes=inputs["original_sizes"],
    return_tensors="pt",
).to(device)

with torch.no_grad():
    refined_outputs = model(
        **inputs,
        input_masks=mask_input,
        image_embeddings=outputs.image_embeddings,
        multimask_output=False,
    )
```

## Batch Image Processing

### Batched Images with Multiple Objects

Process multiple images simultaneously, each with multiple objects:

```python
from PIL import Image
import requests

# Load multiple images
image_urls = [
    "https://huggingface.co/datasets/hf-internal-testing/sam2-fixtures/resolve/main/truck.jpg",
    "https://huggingface.co/datasets/hf-internal-testing/sam2-fixtures/resolve/main/groceries.jpg"
]
raw_images = [Image.open(requests.get(url, stream=True).raw).convert("RGB") for url in image_urls]

# Different numbers of objects per image
input_boxes = [
    [[75, 275, 1725, 850], [425, 600, 700, 875]],  # Truck image: 2 boxes
    [[450, 170, 520, 350], [350, 190, 450, 350]]   # Groceries image: 2 boxes
]

inputs = processor(images=raw_images, input_boxes=input_boxes, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model(**inputs, multimask_output=False)

all_masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])
print(f"Processed {len(all_masks)} images with {all_masks[0].shape[0]} and {all_masks[1].shape[0]} objects")
```

### Mixed Prompts in Batch

Combine points and boxes with varying numbers per object:

```python
# Complex batching: multiple images, multiple objects, multiple points per object
input_points = [
    [[[500, 375]], [[650, 750]]],  # Image 1: 2 objects with 1 point each
    [[[400, 300]], [[630, 300], [550, 300]]]  # Image 2: obj1 has 1 point, obj2 has 2 points
]
input_labels = [
    [[1], [1]],  # Image 1: positive clicks
    [[1], [1, 1]]  # Image 2: positive clicks for refinement
]

inputs = processor(images=raw_images, input_points=input_points, input_labels=input_labels, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model(**inputs, multimask_output=False)

all_masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])
```

## Video Object Tracking

### Basic Single Object Tracking

Track an object across all video frames:

```python
from transformers import EdgeTamVideoModel, Sam2VideoProcessor
from transformers.video_utils import load_video
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
video_model = EdgeTamVideoModel.from_pretrained("yonigozlan/EdgeTAM-hf").to(device, dtype=torch.bfloat16)
video_processor = Sam2VideoProcessor.from_pretrained("yonigozlan/EdgeTAM-hf")

# Load video
video_url = "https://huggingface.co/datasets/hf-internal-testing/sam2-fixtures/resolve/main/bedroom.mp4"
video_frames, _ = load_video(video_url)

# Initialize video inference session
inference_session = video_processor.init_video_session(
    video=video_frames,
    inference_device=device,
    torch_dtype=torch.bfloat16,
)

# Add object on first frame
ann_frame_idx = 0
ann_obj_id = 1
points = [[[[210, 350]]]]
labels = [[[1]]]

video_processor.add_inputs_to_inference_session(
    inference_session=inference_session,
    frame_idx=ann_frame_idx,
    obj_ids=ann_obj_id,
    input_points=points,
    input_labels=labels,
)

# Segment on first frame
outputs = video_model(
    inference_session=inference_session,
    frame_idx=ann_frame_idx,
)

# Propagate through entire video
video_segments = {}
for edgetam_video_output in video_model.propagate_in_video_iterator(inference_session):
    video_res_masks = video_processor.post_process_masks(
        [edgetam_video_output.pred_masks],
        original_sizes=[[inference_session.video_height, inference_session.video_width]],
        binarize=False
    )[0]
    video_segments[edgetam_video_output.frame_idx] = video_res_masks

print(f"Tracked object through {len(video_segments)} frames")
```

### Multi-Object Video Tracking

Track multiple objects simultaneously:

```python
# Reset for new tracking session
inference_session.reset_inference_session()

# Add multiple objects on first frame with bounding boxes
ann_frame_idx = 0
obj_ids = [2, 3]
input_boxes = [[[100, 150, 300, 400], [500, 200, 700, 500]]]  # Two bounding boxes

video_processor.add_inputs_to_inference_session(
    inference_session=inference_session,
    frame_idx=ann_frame_idx,
    obj_ids=obj_ids,
    input_boxes=input_boxes,
)

# Get masks for both objects on first frame
outputs = video_model(
    inference_session=inference_session,
    frame_idx=ann_frame_idx,
)

# Propagate both objects through video
video_segments = {}
for edgetam_video_output in video_model.propagate_in_video_iterator(inference_session):
    video_res_masks = video_processor.post_process_masks(
        [edgetam_video_output.pred_masks],
        original_sizes=[[inference_session.video_height, inference_session.video_width]],
        binarize=False
    )[0]
    video_segments[edgetam_video_output.frame_idx] = {
        obj_id: video_res_masks[i]
        for i, obj_id in enumerate(inference_session.obj_ids)
    }

print(f"Tracked {len(inference_session.obj_ids)} objects through {len(video_segments)} frames")
```

### Refining Video Tracking

Add clicks on later frames to refine tracking:

```python
# Add refinement click on frame 50
refine_frame_idx = 50
ann_obj_id = 2  # Refining object ID 2
points = [[[[220, 280]]]]
labels = [[[1]]]

video_processor.add_inputs_to_inference_session(
    inference_session=inference_session,
    frame_idx=refine_frame_idx,
    obj_ids=ann_obj_id,
    input_points=points,
    input_labels=labels,
)

# Re-propagate with additional information
video_segments = {}
for edgetam_video_output in video_model.propagate_in_video_iterator(inference_session):
    video_res_masks = video_processor.post_process_masks(
        [edgetam_video_output.pred_masks],
        original_sizes=[[inference_session.video_height, inference_session.video_width]],
        binarize=False
    )[0]
    video_segments[edgetam_video_output.frame_idx] = video_res_masks
```

### Streaming Video Inference

For real-time applications processing frames as they arrive:

```python
# Initialize session for streaming
inference_session = video_processor.init_video_session(
    inference_device=device,
    torch_dtype=torch.bfloat16,
)

# Process frames one by one
for frame_idx, frame in enumerate(video_frames[:10]):  # Process first 10 frames
    inputs = video_processor(images=frame, device=device, return_tensors="pt")

    if frame_idx == 0:
        # Add initial prompts on first frame
        video_processor.add_inputs_to_inference_session(
            inference_session=inference_session,
            frame_idx=0,
            obj_ids=1,
            input_points=[[[[210, 350]]]],
            input_labels=[[[1]]],
            original_size=inputs.original_sizes[0],
        )

    # Process current frame
    edgetam_video_output = video_model(inference_session=inference_session, frame=inputs.pixel_values[0])

    video_res_masks = video_processor.post_process_masks(
        [edgetam_video_output.pred_masks],
        original_sizes=inputs.original_sizes,
        binarize=False
    )[0]
    print(f"Frame {frame_idx}: mask shape {video_res_masks.shape}")
```

## Automatic Mask Generation

For automatic segmentation of all objects without prompts:

```python
from transformers import pipeline

generator = pipeline("mask-generation", model="yonigozlan/EdgeTAM-hf", device=0)
image_url = "https://huggingface.co/datasets/hf-internal-testing/sam2-fixtures/resolve/main/truck.jpg"
outputs = generator(image_url, points_per_batch=64)

print(f"Generated {len(outputs['masks'])} masks automatically")
```

## Performance Optimization

### Device Selection and Precision

```python
# For GPU with mixed precision
device = "cuda"
dtype = torch.bfloat16  # Recommended for video models

# For CPU
device = "cpu"
dtype = torch.float32

model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf").to(device, dtype=dtype)
```

### Inference Context

Always use no_grad and autocast for optimal performance:

```python
with torch.no_grad(), torch.autocast(device, dtype=torch.bfloat16):
    outputs = model(**inputs)
```

### Batch Size Tuning

Adjust batch size based on available memory:

```python
# For large batches, process in chunks
def process_large_batch(images, boxes, batch_size=4):
    all_masks = []
    for i in range(0, len(images), batch_size):
        batch_images = images[i:i+batch_size]
        batch_boxes = boxes[i:i+batch_size]
        inputs = processor(images=batch_images, input_boxes=batch_boxes, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs, multimask_output=False)
        masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])
        all_masks.extend(masks)
    return all_masks
```

## Common Patterns and Best Practices

### 1. Multiple Instance Segmentation Pattern

For segmenting all instances of a specific object type (e.g., all people, all cars):

```python
# Step 1: Use automatic mask generation or object detection to get bounding boxes
generator = pipeline("mask-generation", model="yonigozlan/EdgeTAM-hf", device=0)
outputs = generator(image, points_per_batch=64)

# Step 2: Filter masks by area, confidence, or other criteria
filtered_boxes = [box for box, score in zip(outputs['boxes'], outputs['scores']) if score > 0.8]

# Step 3: Refine with EdgeTAM using filtered boxes
inputs = processor(images=image, input_boxes=[filtered_boxes], return_tensors="pt").to(device)
with torch.no_grad():
    refined_outputs = model(**inputs, multimask_output=False)
refined_masks = processor.post_process_masks(refined_outputs.pred_masks.cpu(), inputs["original_sizes"])[0]
```

### 2. Interactive Refinement Pattern

For user-driven segmentation refinement:

```python
def interactive_segmentation(image, initial_prompt, refinement_prompts):
    """
    initial_prompt: dict with 'points' and 'labels' or 'boxes'
    refinement_prompts: list of dicts with additional 'points' and 'labels'
    """
    # Initial segmentation
    if 'boxes' in initial_prompt:
        inputs = processor(images=image, input_boxes=initial_prompt['boxes'], return_tensors="pt").to(device)
    else:
        inputs = processor(images=image, input_points=initial_prompt['points'],
                          input_labels=initial_prompt['labels'], return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    # Iterative refinement
    mask_input = outputs.pred_masks[:, :, torch.argmax(outputs.iou_scores.squeeze())]
    image_embeddings = outputs.image_embeddings

    for refinement in refinement_prompts:
        inputs = processor(
            input_points=refinement['points'],
            input_labels=refinement['labels'],
            original_sizes=inputs["original_sizes"],
            return_tensors="pt",
        ).to(device)

        with torch.no_grad():
            outputs = model(
                **inputs,
                input_masks=mask_input,
                image_embeddings=image_embeddings,
                multimask_output=False,
            )
        mask_input = outputs.pred_masks

    final_masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])[0]
    return final_masks
```

### 3. Video Object Annotation Pattern

For annotating specific objects across video:

```python
def annotate_video_objects(video_frames, object_annotations):
    """
    object_annotations: dict mapping frame_idx to list of (obj_id, box/points, labels)
    """
    inference_session = video_processor.init_video_session(
        video=video_frames,
        inference_device=device,
        torch_dtype=torch.bfloat16,
    )

    # Add all initial annotations
    for frame_idx, annotations in object_annotations.items():
        for obj_id, prompt, labels in annotations:
            if isinstance(prompt, dict) and 'boxes' in prompt:
                video_processor.add_inputs_to_inference_session(
                    inference_session=inference_session,
                    frame_idx=frame_idx,
                    obj_ids=obj_id,
                    input_boxes=prompt['boxes'],
                )
            else:
                video_processor.add_inputs_to_inference_session(
                    inference_session=inference_session,
                    frame_idx=frame_idx,
                    obj_ids=obj_id,
                    input_points=prompt['points'],
                    input_labels=labels,
                )

    # Propagate through video
    video_segments = {}
    for edgetam_video_output in video_model.propagate_in_video_iterator(inference_session):
        video_res_masks = video_processor.post_process_masks(
            [edgetam_video_output.pred_masks],
            original_sizes=[[inference_session.video_height, inference_session.video_width]],
            binarize=False
        )[0]
        video_segments[edgetam_video_output.frame_idx] = {
            obj_id: video_res_masks[i]
            for i, obj_id in enumerate(inference_session.obj_ids)
        }

    return video_segments
```

## Troubleshooting

### Common Issues

**Issue:** Out of memory errors with large batches
**Solution:** Reduce batch size, use bfloat16 precision, or process in chunks

**Issue:** Poor segmentation quality
**Solution:** Add more point prompts (especially negative clicks), use bounding boxes for initial rough segmentation, or refine masks iteratively

**Issue:** Video tracking loses object
**Solution:** Add refinement clicks on frames where tracking degrades, use tighter initial bounding boxes, or increase temporal resolution

**Issue:** Slow inference on CPU
**Solution:** Use GPU if available, reduce image resolution, or consider quantization (see references/optimization.md)

## Resources

### References

This skill includes detailed reference documentation:

- **references/api_reference.md** - Complete API documentation for EdgeTamModel, EdgeTamVideoModel, Sam2Processor, and Sam2VideoProcessor classes
- **references/architecture.md** - Technical details about 2D Spatial Perceiver architecture and model design
- **references/optimization.md** - Advanced optimization techniques for edge devices including CoreML export and quantization

To access reference material during implementation, use the Read tool:
```
Read: references/api_reference.md
Read: references/architecture.md
```

### Scripts

Example scripts for common workflows:

- **scripts/bbox_batch_segmentation.py** - Batch processing multiple images with bounding box prompts
- **scripts/video_object_tracker.py** - Complete video tracking implementation with visualization
- **scripts/interactive_segmentation.py** - Interactive refinement workflow with user input

### External Resources

- **GitHub Repository:** https://github.com/facebookresearch/EdgeTAM
- **HuggingFace Model:** https://huggingface.co/yonigozlan/EdgeTAM-hf
- **Research Paper:** [EdgeTAM: On-Device Track Anything Model](https://arxiv.org/abs/2501.07256)
- **Transformers Docs:** https://huggingface.co/docs/transformers/model_doc/edgetam

## Citation

If using EdgeTAM in research or production:

```bibtex
@article{zhou2025edgetam,
  title={EdgeTAM: On-Device Track Anything Model},
  author={Zhou, Chong and Zhu, Chenchen and Xiong, Yunyang and Suri, Saksham and Xiao, Fanyi and Wu, Lemeng and Krishnamoorthi, Raghuraman and Dai, Bo and Loy, Chen Change and Chandra, Vikas and Soran, Bilge},
  journal={arXiv preprint arXiv:2501.07256},
  year={2025}
}
```

## Additional Notes

- EdgeTAM achieves 150.9 FPS on A100 GPU with torch compile
- Supports CoreML export for iOS deployment (see references/optimization.md)
- Model uses Apache 2.0 license for both code and checkpoints
- Input dimensions format: `[batch_size, num_objects, num_points, coordinates]`
- Always use `multimask_output=False` when segmenting multiple specific objects to avoid ambiguity
