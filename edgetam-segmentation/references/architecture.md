# EdgeTAM Architecture

This document provides technical details about the EdgeTAM architecture, including the 2D Spatial Perceiver design and model optimizations.

## Overview

EdgeTAM (Edge Track Anything Model) is an optimized variant of SAM 2 specifically designed for edge device execution. The key innovation is the 2D Spatial Perceiver architecture that replaces the Global Perceiver in SAM 2, enabling 22× faster inference while maintaining competitive accuracy.

## Key Architecture Components

### 1. 2D Spatial Perceiver

The 2D Spatial Perceiver is the core architectural innovation in EdgeTAM, designed to address limitations of the Global Perceiver approach for video object segmentation.

#### Motivation

As a dense prediction task, video object segmentation requires:
- **Explicit positional information**: Unlike global attention, local spatial relationships are critical
- **Local features**: Fine-grained details matter more than global context
- **Memory efficiency**: Edge devices have limited computational resources

The Global Perceiver in SAM 2 compresses all spatial information into learned queries, which loses important positional information needed for accurate segmentation.

#### Design

The 2D Spatial Perceiver maintains spatial structure through:

1. **Spatial Grid Organization**: Instead of learned queries, uses a 2D spatial grid that preserves relative positions
2. **Local Attention Windows**: Restricts attention to local neighborhoods for efficiency
3. **Hierarchical Feature Aggregation**: Progressively combines features at multiple scales

#### Benefits

- **22× faster inference** compared to SAM 2
- **Lower memory footprint**: Reduced from ~500MB to ~20MB for model weights
- **Better edge device performance**: 16 FPS on iPhone 15 Pro Max
- **Maintained accuracy**: 72.3 J&F on SA-V validation dataset

### 2. Three-Module Architecture

EdgeTAM consists of three modular components, each exportable separately for mobile deployment:

#### Image Encoder (~9.6MB)

- Converts input images to feature embeddings
- Based on efficient ConvNet backbone
- Optimized for mobile execution
- Can be cached for multiple prompts on same image

#### Prompt Encoder (~2MB)

- Processes user inputs:
  - Point coordinates (x, y)
  - Bounding boxes [x_min, y_min, x_max, y_max]
  - Previous masks for refinement
- Lightweight and fast
- Generates prompt embeddings compatible with mask decoder

#### Mask Decoder (~8MB)

- Takes image embeddings and prompt embeddings
- Generates segmentation masks
- Produces IoU quality scores
- Can output multiple mask predictions ranked by confidence

### 3. Knowledge Distillation Pipeline

EdgeTAM uses distillation to transfer knowledge from SAM 2 teacher to the efficient student model.

#### Distillation Strategy

1. **Feature Alignment**: Align memory attention outputs between teacher and student
2. **Mask Supervision**: Supervise final mask predictions with teacher masks
3. **IoU Score Matching**: Match quality prediction scores

#### Training Process

```
SAM 2 (Teacher)           EdgeTAM (Student)
       │                         │
       ├─> Memory Features       │
       │          │               │
       │          └───────────────┤ L2 Loss
       │                          │
       ├─> Mask Predictions       │
       │          │               │
       │          └───────────────┤ BCE Loss
       │                          │
       └─> IoU Scores             │
                  │               │
                  └───────────────┤ L1 Loss
                                  │
                            Final Model
```

## Model Specifications

### EdgeTAM Model Sizes

| Component | Parameters | Size (MB) | Description |
|-----------|-----------|-----------|-------------|
| Image Encoder | ~5M | 9.6 | Feature extraction backbone |
| Prompt Encoder | ~0.5M | 2.0 | Prompt embedding network |
| Mask Decoder | ~4M | 8.0 | Mask prediction head |
| **Total** | **~10M** | **~20MB** | Complete model |

Compare to SAM 2 Base: ~80M parameters, ~500MB

### Input/Output Specifications

**Image Encoder:**
- Input: RGB image (H×W×3)
- Output: Feature maps (H/16×W/16×256)

**Prompt Encoder:**
- Input: Points [N×2], Boxes [N×4], or Masks [H×W]
- Output: Prompt embeddings [N×256]

**Mask Decoder:**
- Input: Image features + Prompt embeddings
- Output: Masks [N×H×W] + IoU scores [N]

## Video Object Tracking

### Memory Attention Mechanism

EdgeTAM maintains temporal consistency through memory attention:

1. **Frame Encoding**: Each frame is encoded to feature representation
2. **Memory Bank**: Store features from key frames
3. **Cross-Frame Attention**: Current frame attends to memory bank
4. **Mask Propagation**: Predicted masks guide attention in next frame

### 2D Spatial Memory

Unlike SAM 2's global memory, EdgeTAM uses spatial memory:

```
Frame 0: [Feature Map H/16 × W/16 × 256]
         ↓ Store spatial features
Memory:  [Spatial Grid H/16 × W/16 × 256]
         ↓ Cross-attention with Frame 1
Frame 1: [Feature Map H/16 × W/16 × 256]
         ↓ Update memory selectively
Memory:  [Updated Spatial Grid]
```

### Temporal Propagation

**Initialization**: User provides prompts (boxes/points) on first frame

**Propagation Loop**:
1. Encode current frame
2. Retrieve relevant memory features (spatially localized)
3. Predict masks using combined features
4. Update memory bank with high-confidence regions
5. Repeat for next frame

**Refinement**: User can add clicks on any frame to improve tracking

## Performance Characteristics

### Inference Speed

**Image Segmentation:**
- iPhone 15 Pro Max: 40.4 FPS
- A100 GPU: 150.9 FPS (with torch compile)
- CPU (Intel i9): ~8 FPS

**Video Tracking:**
- iPhone 15 Pro Max: 15.7 FPS
- A100 GPU: 72.3 FPS
- Includes propagation through time

### Memory Usage

**Peak Memory (Image Mode):**
- Mobile (iOS): ~150MB
- GPU: ~1GB
- CPU: ~300MB

**Peak Memory (Video Mode):**
- Mobile (iOS): ~300MB (caching 10 frames)
- GPU: ~2GB (batch processing)
- CPU: ~500MB

### Accuracy Metrics

**SA-V Dataset (Video Object Segmentation):**
- J&F Score: 72.3
- J (Region Similarity): 69.1
- F (Contour Accuracy): 75.5

**MOSE Dataset:**
- J&F Score: 65.8

Compare to SAM 2 Base: 73.0 J&F on SA-V (EdgeTAM is 0.7 points lower but 22× faster)

## Optimization Techniques

### 1. Efficient Attention

**Local Windowed Attention**: Restrict attention to local windows instead of global
- Window size: 7×7 spatial grid
- Reduces complexity from O(N²) to O(N×W²)

**Deformable Attention**: Learn offset positions for more flexible receptive fields
- 3×3 deformable grid
- Adapts to object shape

### 2. Depthwise Separable Convolutions

Replace standard convolutions with depthwise separable:
- Reduces parameters by ~8× 
- Maintains representational capacity
- Enables mobile deployment

### 3. Quantization-Aware Training

Train with quantization in mind:
- Simulate INT8 operations during training
- Learn quantization-robust features
- Enables CoreML INT8 export without accuracy loss

### 4. Feature Caching

Cache intermediate features when appropriate:
- **Image embeddings**: Reuse for multiple prompts on same image
- **Memory features**: Reuse across video frames
- Reduces redundant computation

## Implementation Details

### Backbone Architecture

```
Input Image (3×H×W)
    ↓
Stem Conv (3→64)
    ↓
Stage 1: 4× DepthwiseSeparable Blocks (64)
    ↓ (Downsample 2×)
Stage 2: 6× DepthwiseSeparable Blocks (128)
    ↓ (Downsample 2×)
Stage 3: 12× DepthwiseSeparable Blocks (256)
    ↓ (Downsample 2×)
Stage 4: 4× DepthwiseSeparable Blocks (512)
    ↓
Feature Map (256×H/16×W/16)
```

### Prompt Encoder Details

**Point Encoding**:
```python
# Positional encoding with learned embeddings
pos_embed = learned_positional_embedding[y, x]  # 256-dim
label_embed = point_label_embedding[label]      # 256-dim (foreground/background)
point_embed = pos_embed + label_embed
```

**Box Encoding**:
```python
# Encode as 4 corner points
top_left = encode_point(x_min, y_min, label=2)     # Top-left corner
bottom_right = encode_point(x_max, y_max, label=3) # Bottom-right corner
box_embed = concatenate([top_left, bottom_right])
```

### Mask Decoder Details

**Architecture**:
```
Image Features (256×H/16×W/16) + Prompt Embeds (N×256)
    ↓
Cross-Attention Block
    ↓
Self-Attention Block
    ↓
MLP Block
    ↓
Repeat 2×
    ↓
Upsampling (→H/4×W/4)
    ↓
Conv Layers
    ↓
Final Masks (N×H×W)
```

**IoU Prediction Head**:
```
Mask Features (N×256)
    ↓
MLP (256→128→64→1)
    ↓
Sigmoid
    ↓
IoU Scores (N×1)
```

## Comparison with SAM 2

| Aspect | SAM 2 | EdgeTAM | Improvement |
|--------|-------|---------|-------------|
| Parameters | 80M | 10M | **8× smaller** |
| Model Size | 500MB | 20MB | **25× smaller** |
| Inference Speed | 7 FPS | 150 FPS | **22× faster** |
| Memory Usage | 2GB | 1GB | **2× lower** |
| Mobile FPS | 0.7 FPS | 16 FPS | **23× faster** |
| SA-V J&F | 73.0 | 72.3 | -0.7 |

## Design Principles

### 1. Spatial Locality

Prioritize local features over global context:
- Dense prediction tasks benefit from explicit spatial structure
- Local attention is more efficient for high-resolution outputs

### 2. Modular Design

Separate encoder/decoder enables:
- Independent optimization of each component
- Flexible deployment (e.g., server-side encoder, on-device decoder)
- Caching strategies to reduce computation

### 3. Mobile-First

Design choices favor mobile execution:
- Depthwise separable convolutions
- Quantization-aware training
- CoreML export support
- Small model size (<25MB)

### 4. Distillation Over Pre-training

Transfer knowledge from powerful teacher:
- Leverage SAM 2's extensive pre-training
- No need for massive dataset/compute for training
- Faster convergence and better accuracy

## Future Directions

### Potential Improvements

1. **Dynamic Architectur**e: Adapt model size based on device capabilities
2. **Multi-Scale Features**: Better handle objects at different scales
3. **Temporal Modeling**: More sophisticated video understanding beyond frame-to-frame propagation
4. **Few-Shot Adaptation**: Quickly adapt to new object categories with minimal examples

### Research Applications

- Real-time augmented reality
- Mobile video editing
- Autonomous systems (drones, robots)
- Medical imaging on edge devices
- Interactive annotation tools

## References

- **Paper**: [EdgeTAM: On-Device Track Anything Model](https://arxiv.org/abs/2501.07256)
- **GitHub**: https://github.com/facebookresearch/EdgeTAM
- **HuggingFace Model**: https://huggingface.co/yonigozlan/EdgeTAM-hf
- **SAM 2 Paper**: [Segment Anything in Images and Videos](https://arxiv.org/abs/2408.00714)

## Acknowledgments

EdgeTAM builds upon the groundbreaking work of SAM and SAM 2 from Meta's FAIR team. The 2D Spatial Perceiver architecture represents a significant contribution to efficient vision transformers for dense prediction tasks.
