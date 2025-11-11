# EdgeTAM API Reference

This document provides comprehensive API documentation for EdgeTAM models and processors in the HuggingFace Transformers library.

## Table of Contents

1. [EdgeTamModel](#edgetammodel)
2. [EdgeTamVideoModel](#edgetamvideomodel)
3. [Sam2Processor](#sam2processor)
4. [Sam2VideoProcessor](#sam2videoprocessor)
5. [Model Outputs](#model-outputs)
6. [Input Format Specifications](#input-format-specifications)

## EdgeTamModel

Image segmentation model for promptable object segmentation.

### Initialization

```python
from transformers import EdgeTamModel

model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf")
model = model.to(device, dtype=torch.bfloat16)  # Optional: move to GPU and set dtype
```

### forward()

Main inference method for image segmentation.

```python
outputs = model(
    pixel_values: torch.FloatTensor,
    input_points: Optional[torch.FloatTensor] = None,
    input_labels: Optional[torch.LongTensor] = None,
    input_boxes: Optional[torch.FloatTensor] = None,
    input_masks: Optional[torch.FloatTensor] = None,
    image_embeddings: Optional[torch.FloatTensor] = None,
    multimask_output: bool = True,
    attention_similarity: Optional[torch.FloatTensor] = None,
    target_embedding: Optional[torch.FloatTensor] = None,
    return_dict: bool = True,
)
```

#### Parameters

- **pixel_values** (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`)
  - Image tensor from processor. Required if `image_embeddings` is not provided.

- **input_points** (`torch.FloatTensor` of shape `(batch_size, num_objects, num_points, 2)`, *optional*)
  - Point coordinates in [x, y] format. Use with `input_labels`.

- **input_labels** (`torch.LongTensor` of shape `(batch_size, num_objects, num_points)`, *optional*)
  - Labels for each point: `1` for positive (foreground), `0` for negative (background).

- **input_boxes** (`torch.FloatTensor` of shape `(batch_size, num_objects, 4)`, *optional*)
  - Bounding boxes in [x_min, y_min, x_max, y_max] format.

- **input_masks** (`torch.FloatTensor` of shape `(batch_size, num_objects, height, width)`, *optional*)
  - Previous mask predictions to refine. Use with `image_embeddings`.

- **image_embeddings** (`torch.FloatTensor`, *optional*)
  - Pre-computed image embeddings from previous forward pass. Enables refinement without re-encoding.

- **multimask_output** (`bool`, *optional*, defaults to `True`)
  - If `True`, returns 3 masks per object ranked by quality. If `False`, returns 1 mask per object.
  - **Important:** Set to `False` when segmenting multiple specific objects.

- **return_dict** (`bool`, *optional*, defaults to `True`)
  - Whether to return a `Sam2ImageSegmentationOutput` object or a tuple.

#### Returns

`Sam2ImageSegmentationOutput` object containing:

- **pred_masks** (`torch.FloatTensor` of shape `(batch_size, num_objects, num_mask_predictions, height, width)`)
  - Predicted segmentation masks. `num_mask_predictions` is 3 if `multimask_output=True`, else 1.

- **iou_scores** (`torch.FloatTensor` of shape `(batch_size, num_objects, num_mask_predictions)`)
  - Predicted IoU quality scores for each mask. Higher is better.

- **image_embeddings** (`torch.FloatTensor`)
  - Image feature embeddings. Can be reused for refinement.

#### Example Usage

```python
# Single object with bounding box
inputs = processor(images=image, input_boxes=[[[100, 100, 500, 500]]], return_tensors="pt").to(device)
outputs = model(**inputs)
masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])[0]

# Multiple objects with points
input_points = [[[[300, 200]], [[600, 400]]]]  # 2 objects
input_labels = [[[1], [1]]]  # Both positive
inputs = processor(images=image, input_points=input_points, input_labels=input_labels, return_tensors="pt").to(device)
outputs = model(**inputs, multimask_output=False)

# Refinement with previous mask
mask_input = outputs.pred_masks[:, :, torch.argmax(outputs.iou_scores.squeeze())]
new_inputs = processor(input_points=new_points, input_labels=new_labels, original_sizes=inputs["original_sizes"], return_tensors="pt").to(device)
refined_outputs = model(**new_inputs, input_masks=mask_input, image_embeddings=outputs.image_embeddings, multimask_output=False)
```

## EdgeTamVideoModel

Video object tracking model for temporal segmentation.

### Initialization

```python
from transformers import EdgeTamVideoModel

video_model = EdgeTamVideoModel.from_pretrained("yonigozlan/EdgeTAM-hf")
video_model = video_model.to(device, dtype=torch.bfloat16)  # Recommended for efficiency
```

### forward()

Process a single frame in video tracking context.

```python
outputs = video_model(
    inference_session: InferenceSession,
    frame_idx: Optional[int] = None,
    frame: Optional[torch.FloatTensor] = None,
)
```

#### Parameters

- **inference_session** (`InferenceSession`)
  - Video inference session initialized by `Sam2VideoProcessor.init_video_session()`.

- **frame_idx** (`int`, *optional*)
  - Frame index to process. Required for batch video mode (when session initialized with video).

- **frame** (`torch.FloatTensor`, *optional*)
  - Single frame tensor. Required for streaming video mode (when session initialized without video).

#### Returns

`EdgeTamVideoOutput` object containing:

- **pred_masks** (`torch.FloatTensor` of shape `(num_objects, 1, height, width)`)
  - Predicted masks for all tracked objects on this frame.

- **frame_idx** (`int`)
  - The frame index that was processed.

- **obj_ids** (`List[int]`)
  - Object IDs for the predicted masks.

### propagate_in_video_iterator()

Propagate tracked objects through all video frames.

```python
for output in video_model.propagate_in_video_iterator(inference_session):
    # Process each frame's output
    masks = processor.post_process_masks([output.pred_masks], ...)
```

#### Parameters

- **inference_session** (`InferenceSession`)
  - Video inference session with objects already added.

#### Yields

`EdgeTamVideoOutput` for each frame in the video.

#### Example Usage

```python
# Initialize session
inference_session = video_processor.init_video_session(
    video=video_frames,
    inference_device=device,
    torch_dtype=torch.bfloat16,
)

# Add objects on first frame
video_processor.add_inputs_to_inference_session(
    inference_session=inference_session,
    frame_idx=0,
    obj_ids=[1, 2],
    input_boxes=[[[100, 100, 300, 300], [400, 200, 600, 500]]],
)

# Segment first frame
outputs = video_model(inference_session=inference_session, frame_idx=0)

# Propagate through video
for output in video_model.propagate_in_video_iterator(inference_session):
    video_res_masks = video_processor.post_process_masks(
        [output.pred_masks],
        original_sizes=[[inference_session.video_height, inference_session.video_width]],
        binarize=False
    )[0]
    # Save or visualize masks
```

## Sam2Processor

Processor for preparing inputs and post-processing outputs for EdgeTamModel.

### Initialization

```python
from transformers import Sam2Processor

processor = Sam2Processor.from_pretrained("yonigozlan/EdgeTAM-hf")
```

### __call__()

Prepare inputs for the model.

```python
inputs = processor(
    images: Union[PIL.Image.Image, np.ndarray, torch.Tensor, List[...]],
    input_points: Optional[List] = None,
    input_labels: Optional[List] = None,
    input_boxes: Optional[List] = None,
    return_tensors: str = "pt",
)
```

#### Parameters

- **images** (PIL Image, numpy array, torch Tensor, or list of these)
  - Input image(s) to process. Can be single image or batch.

- **input_points** (`List`, *optional*)
  - Point prompts. Format: `[batch_dim][object_dim][point_dim][2]`
  - Example: `[[[[300, 200], [350, 250]]]]` = 1 image, 1 object, 2 points

- **input_labels** (`List`, *optional*)
  - Labels for points. Format: `[batch_dim][object_dim][point_dim]`
  - Values: `1` (positive), `0` (negative)

- **input_boxes** (`List`, *optional*)
  - Bounding boxes. Format: `[batch_dim][object_dim][4]`
  - Coordinates: `[x_min, y_min, x_max, y_max]`

- **return_tensors** (`str`, defaults to `"pt"`)
  - Return format: `"pt"` (PyTorch), `"np"` (NumPy), or `"tf"` (TensorFlow)

#### Returns

`BatchFeature` dictionary containing:

- **pixel_values** (`torch.FloatTensor`)
  - Processed image tensors ready for model input.

- **original_sizes** (`torch.LongTensor`)
  - Original image dimensions before resizing. Used for post-processing.

- **input_points** (`torch.FloatTensor`, *optional*)
  - Processed point coordinates (if provided).

- **input_labels** (`torch.LongTensor`, *optional*)
  - Processed point labels (if provided).

- **input_boxes** (`torch.FloatTensor`, *optional*)
  - Processed bounding boxes (if provided).

### post_process_masks()

Convert model output masks to original image size.

```python
final_masks = processor.post_process_masks(
    masks: torch.FloatTensor,
    original_sizes: torch.LongTensor,
    reshaped_input_sizes: Optional[torch.LongTensor] = None,
    mask_threshold: float = 0.0,
    binarize: bool = True,
)
```

#### Parameters

- **masks** (`torch.FloatTensor`)
  - Raw mask predictions from model (logits).

- **original_sizes** (`torch.LongTensor`)
  - Original image sizes from processor output.

- **reshaped_input_sizes** (`torch.LongTensor`, *optional*)
  - Intermediate resize dimensions (usually not needed).

- **mask_threshold** (`float`, defaults to `0.0`)
  - Threshold for binarization. Pixels > threshold become 1, else 0.

- **binarize** (`bool`, defaults to `True`)
  - Whether to convert to binary masks or keep as probabilities.

#### Returns

List of `torch.BoolTensor` (if binarized) or `torch.FloatTensor` (if not binarized), one per image in batch.

#### Example

```python
# Get masks from model
outputs = model(**inputs)

# Post-process to original size
final_masks = processor.post_process_masks(
    outputs.pred_masks.cpu(),
    inputs["original_sizes"],
    binarize=True
)

# Access masks for first image
masks_image_0 = final_masks[0]  # Shape: (num_objects, num_masks, height, width)
```

## Sam2VideoProcessor

Processor for video segmentation and tracking.

### Initialization

```python
from transformers import Sam2VideoProcessor

video_processor = Sam2VideoProcessor.from_pretrained("yonigozlan/EdgeTAM-hf")
```

### init_video_session()

Initialize a video tracking session.

```python
inference_session = video_processor.init_video_session(
    video: Optional[List[PIL.Image.Image]] = None,
    inference_device: Union[str, torch.device] = "cpu",
    torch_dtype: torch.dtype = torch.float32,
)
```

#### Parameters

- **video** (`List[PIL.Image.Image]`, *optional*)
  - List of video frames. If provided, enables batch video mode. If None, enables streaming mode.

- **inference_device** (`str` or `torch.device`, defaults to `"cpu"`)
  - Device for inference: `"cuda"`, `"cpu"`, etc.

- **torch_dtype** (`torch.dtype`, defaults to `torch.float32`)
  - Data type for inference. Use `torch.bfloat16` for efficiency.

#### Returns

`InferenceSession` object containing:

- **video_width** (`int`) - Video frame width
- **video_height** (`int`) - Video frame height
- **num_frames** (`int`) - Total number of frames (batch mode only)
- **obj_ids** (`List[int]`) - Currently tracked object IDs
- Internal state for temporal propagation

### add_inputs_to_inference_session()

Add object prompts to a video inference session.

```python
video_processor.add_inputs_to_inference_session(
    inference_session: InferenceSession,
    frame_idx: int,
    obj_ids: Union[int, List[int]],
    input_points: Optional[List] = None,
    input_labels: Optional[List] = None,
    input_boxes: Optional[List] = None,
    original_size: Optional[Tuple[int, int]] = None,
)
```

#### Parameters

- **inference_session** (`InferenceSession`)
  - Session to add prompts to.

- **frame_idx** (`int`)
  - Frame index to add prompts on.

- **obj_ids** (`int` or `List[int]`)
  - Object ID(s) for the prompts. Can be new or existing objects.

- **input_points** (`List`, *optional*)
  - Point prompts. Format: `[batch_dim][object_dim][point_dim][2]`

- **input_labels** (`List`, *optional*)
  - Labels for points.

- **input_boxes** (`List`, *optional*)
  - Bounding boxes. Format: `[batch_dim][object_dim][4]`

- **original_size** (`Tuple[int, int]`, *optional*)
  - Original frame size `(height, width)`. Required for streaming mode.

#### Example

```python
# Add 2 objects on frame 0 with bounding boxes
video_processor.add_inputs_to_inference_session(
    inference_session=inference_session,
    frame_idx=0,
    obj_ids=[1, 2],
    input_boxes=[[[100, 100, 300, 300], [400, 200, 600, 500]]],
)

# Add refinement click for object 1 on frame 25
video_processor.add_inputs_to_inference_session(
    inference_session=inference_session,
    frame_idx=25,
    obj_ids=1,
    input_points=[[[[200, 200]]]],
    input_labels=[[[1]]],
)
```

### reset_inference_session()

Reset a video session to start new tracking.

```python
inference_session.reset_inference_session()
```

Clears all tracked objects and temporal state while keeping the video frames.

### post_process_masks()

Same as `Sam2Processor.post_process_masks()` but adapted for video outputs.

## Model Outputs

### Sam2ImageSegmentationOutput

Output from `EdgeTamModel.forward()`.

**Attributes:**

- `pred_masks` (`torch.FloatTensor` of shape `(batch_size, num_objects, num_masks, H, W)`)
  - Predicted segmentation masks (logits).

- `iou_scores` (`torch.FloatTensor` of shape `(batch_size, num_objects, num_masks)`)
  - Quality scores for each mask prediction.

- `image_embeddings` (`torch.FloatTensor`)
  - Image feature embeddings for potential reuse.

- `loss` (`torch.FloatTensor`, *optional*)
  - Segmentation loss (only during training).

### EdgeTamVideoOutput

Output from `EdgeTamVideoModel.forward()` and iterator.

**Attributes:**

- `pred_masks` (`torch.FloatTensor` of shape `(num_objects, 1, H, W)`)
  - Predicted masks for all objects on this frame.

- `frame_idx` (`int`)
  - The processed frame index.

- `obj_ids` (`List[int]`)
  - Object IDs corresponding to the masks.

## Input Format Specifications

### Point Coordinates

**Format:** `[batch_dim][object_dim][point_dim][2]`

```python
# Single image, single object, single point
input_points = [[[[300, 200]]]]

# Single image, single object, multiple points
input_points = [[[[300, 200], [350, 250], [320, 220]]]]

# Single image, multiple objects, varying points
input_points = [
    [[[300, 200]], [[600, 400], [650, 450]]]  # Object 1: 1 point, Object 2: 2 points
]

# Multiple images, multiple objects
input_points = [
    [[[300, 200]], [[600, 400]]],  # Image 1: 2 objects, 1 point each
    [[[150, 100]]]                  # Image 2: 1 object, 1 point
]
```

### Point Labels

**Format:** `[batch_dim][object_dim][point_dim]`

```python
# Must match the structure of input_points
input_labels = [[[1]]]           # Single positive point
input_labels = [[[1, 1, 0]]]     # 2 positive, 1 negative
input_labels = [[[1], [1, 1]]]   # Object 1: 1 point, Object 2: 2 points
```

**Values:**
- `1` = Positive click (include this region in mask)
- `0` = Negative click (exclude this region from mask)

### Bounding Boxes

**Format:** `[batch_dim][object_dim][4]`

**Coordinates:** `[x_min, y_min, x_max, y_max]` where:
- `x_min` = left edge
- `y_min` = top edge
- `x_max` = right edge
- `y_max` = bottom edge

```python
# Single image, single box
input_boxes = [[[100, 100, 500, 500]]]

# Single image, multiple boxes
input_boxes = [[[100, 100, 300, 300], [400, 200, 600, 500]]]

# Multiple images, multiple boxes per image
input_boxes = [
    [[100, 100, 300, 300], [400, 200, 600, 500]],  # Image 1: 2 boxes
    [[50, 50, 200, 200]]                           # Image 2: 1 box
]
```

### Video-Specific Formats

For video, inputs follow the same format but are added per frame:

```python
# Add objects on frame 0
video_processor.add_inputs_to_inference_session(
    inference_session=inference_session,
    frame_idx=0,
    obj_ids=[1, 2],  # Track 2 objects
    input_boxes=[[[100, 100, 300, 300], [400, 200, 600, 500]]],  # One box per object
)

# Refine object 1 on frame 30
video_processor.add_inputs_to_inference_session(
    inference_session=inference_session,
    frame_idx=30,
    obj_ids=1,  # Single object
    input_points=[[[[200, 200]]]],  # Additional point
    input_labels=[[[1]]],
)
```

## Advanced Usage Patterns

### Efficient Batch Processing

```python
# Process large dataset in batches
def batch_inference(images, boxes, batch_size=8):
    results = []
    for i in range(0, len(images), batch_size):
        batch_imgs = images[i:i+batch_size]
        batch_boxes = boxes[i:i+batch_size]

        inputs = processor(images=batch_imgs, input_boxes=batch_boxes, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model(**inputs, multimask_output=False)

        masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])
        results.extend(masks)

    return results
```

### Iterative Refinement

```python
def refine_mask(image, initial_box, max_iterations=3):
    # Initial segmentation
    inputs = processor(images=image, input_boxes=[[initial_box]], return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)

    # Get best mask
    best_mask_idx = torch.argmax(outputs.iou_scores.squeeze())
    mask_input = outputs.pred_masks[:, :, best_mask_idx]
    image_embeddings = outputs.image_embeddings

    # Iterative refinement loop
    for iteration in range(max_iterations):
        # Get user feedback points (in practice, from UI)
        refinement_points, refinement_labels = get_user_feedback(mask_input)

        inputs = processor(
            input_points=[[refinement_points]],
            input_labels=[[refinement_labels]],
            original_sizes=inputs["original_sizes"],
            return_tensors="pt"
        ).to(device)

        with torch.no_grad():
            outputs = model(
                **inputs,
                input_masks=mask_input,
                image_embeddings=image_embeddings,
                multimask_output=False
            )

        mask_input = outputs.pred_masks

    final_mask = processor.post_process_masks(mask_input.cpu(), inputs["original_sizes"])[0]
    return final_mask
```

### Video with Dynamic Object Addition

```python
# Track objects that appear at different times
inference_session = video_processor.init_video_session(
    video=video_frames,
    inference_device=device,
    torch_dtype=torch.bfloat16
)

# Add first object on frame 0
video_processor.add_inputs_to_inference_session(
    inference_session=inference_session,
    frame_idx=0,
    obj_ids=1,
    input_boxes=[[[100, 100, 300, 300]]],
)

# Add second object when it appears on frame 50
video_processor.add_inputs_to_inference_session(
    inference_session=inference_session,
    frame_idx=50,
    obj_ids=2,
    input_boxes=[[[400, 200, 600, 500]]],
)

# Propagate through entire video (both objects tracked)
for output in video_model.propagate_in_video_iterator(inference_session):
    # Object 2 will only have masks from frame 50 onwards
    masks = video_processor.post_process_masks(
        [output.pred_masks],
        original_sizes=[[inference_session.video_height, inference_session.video_width]],
        binarize=False
    )[0]
```

## Performance Tips

1. **Use bfloat16 for video models**: `model.to(dtype=torch.bfloat16)` significantly reduces memory and improves speed
2. **Reuse image embeddings**: When refining, pass `image_embeddings` to avoid re-encoding
3. **Set multimask_output=False**: When you know which object you want, avoid generating 3 masks per object
4. **Batch when possible**: Process multiple images/objects in one forward pass
5. **Use torch.no_grad()**: Always disable gradients during inference
6. **CPU vs GPU**: EdgeTAM is optimized for edge devices but still benefits greatly from GPU acceleration

## Troubleshooting

### Dimension Mismatch Errors

**Problem:** `RuntimeError: The size of tensor a (X) must match the size of tensor b (Y)`

**Solution:** Check input format dimensions:
- Points: `[batch][obj][points][2]`
- Labels: `[batch][obj][points]`
- Boxes: `[batch][obj][4]`

All dimensions except the last must match.

### OOM (Out of Memory)

**Problem:** CUDA out of memory during batch processing

**Solutions:**
- Reduce batch size
- Use `dtype=torch.bfloat16`
- Process images at lower resolution
- Use gradient checkpointing (for training)

### Poor Mask Quality

**Problem:** Masks don't accurately segment the object

**Solutions:**
- Use tighter bounding boxes
- Add positive points inside object
- Add negative points outside object
- Iterate with `input_masks` and `image_embeddings`
- Check if `multimask_output=True` gives better results among the 3 options

### Video Tracking Drift

**Problem:** Object tracking degrades over time

**Solutions:**
- Add refinement clicks on frames where drift occurs
- Use tighter initial bounding boxes
- Add objects on multiple key frames
- Reduce video temporal resolution if possible
