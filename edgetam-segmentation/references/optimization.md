# EdgeTAM Optimization Guide

This document covers advanced optimization techniques for deploying EdgeTAM on edge devices, including CoreML export, quantization, and performance tuning.

## Table of Contents

1. [CoreML Export for iOS](#coreml-export-for-ios)
2. [Quantization Strategies](#quantization-strategies)
3. [Performance Profiling](#performance-profiling)
4. [Memory Optimization](#memory-optimization)
5. [Batching Strategies](#batching-strategies)
6. [Platform-Specific Optimizations](#platform-specific-optimizations)

## CoreML Export for iOS

EdgeTAM can be exported to CoreML format for deployment on iOS devices.

### Prerequisites

```bash
pip install -e ".[coreml]"  # Install CoreML dependencies
```

### Export Script

```bash
python ./tools/export_to_coreml.py \
  --sam2_cfg configs/edgetam.yaml \
  --sam2_checkpoint ./checkpoints/edgetam.pt \
  --output_dir ./coreml_models \
  --validate
```

### Export Options

```python
# Custom export with specific options
python ./tools/export_to_coreml.py \
  --sam2_cfg configs/edgetam.yaml \
  --sam2_checkpoint ./checkpoints/edgetam.pt \
  --output_dir ./coreml_models \
  --compute_units CPU_AND_GPU \  # CPU_ONLY, CPU_AND_GPU, ALL
  --quantize INT8 \               # INT8 or FLOAT16
  --validate
```

### CoreML Model Structure

The export creates three separate CoreML models:

1. **ImageEncoder.mlpackage** (~9.6MB)
   - Input: Image (RGB, H×W×3)
   - Output: Feature embeddings (H/16×W/16×256)

2. **PromptEncoder.mlpackage** (~2MB)
   - Input: Points/Boxes/Masks
   - Output: Prompt embeddings (N×256)

3. **MaskDecoder.mlpackage** (~8MB)
   - Input: Image embeddings + Prompt embeddings
   - Output: Masks + IoU scores

### iOS Integration Example

```swift
import CoreML

// Load models
let imageEncoder = try EdgeTAM_ImageEncoder(configuration: MLModelConfiguration())
let promptEncoder = try EdgeTAM_PromptEncoder(configuration: MLModelConfiguration())
let maskDecoder = try EdgeTAM_MaskDecoder(configuration: MLModelConfiguration())

// Encode image once
let imageFeatures = try imageEncoder.prediction(image: inputImage)

// Process multiple prompts efficiently
for prompt in userPrompts {
    let promptFeatures = try promptEncoder.prediction(prompt: prompt)
    let masks = try maskDecoder.prediction(
        imageFeatures: imageFeatures,
        promptFeatures: promptFeatures
    )
    // Use masks...
}
```

### Performance on iOS

| Device | Image Encoder | Prompt + Decode | Total FPS |
|--------|--------------|-----------------|-----------|
| iPhone 15 Pro Max | 18ms | 8ms | 40.4 FPS |
| iPhone 14 Pro | 25ms | 10ms | 28.6 FPS |
| iPhone 13 | 35ms | 15ms | 20.0 FPS |
| iPad Pro M2 | 12ms | 6ms | 55.6 FPS |

## Quantization Strategies

Quantization reduces model size and improves inference speed with minimal accuracy loss.

### INT8 Quantization

**Benefits:**
- 4× smaller model size
- 2-3× faster inference on mobile
- Minimal accuracy loss (<1% J&F drop)

**PyTorch Post-Training Quantization:**

```python
import torch
from transformers import EdgeTamModel

# Load model
model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf")
model.eval()

# Prepare for quantization
model.qconfig = torch.quantization.get_default_qconfig('qnnpack')
torch.quantization.prepare(model, inplace=True)

# Calibrate with representative data
with torch.no_grad():
    for image in calibration_dataset:
        inputs = processor(images=image, return_tensors="pt")
        model(**inputs)

# Convert to quantized model
torch.quantization.convert(model, inplace=True)

# Save quantized model
torch.save(model.state_dict(), "edgetam_int8.pt")
```

### FLOAT16 (Half Precision)

**Benefits:**
- 2× smaller model size
- 1.5-2× faster on modern GPUs
- Negligible accuracy loss

**Usage:**

```python
import torch
from transformers import EdgeTamModel

model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf")
model = model.half()  # Convert to float16
model = model.to("cuda")

# Inference with float16
with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16):
    inputs = processor(images=image, input_boxes=boxes, return_tensors="pt").to("cuda")
    outputs = model(**inputs)
```

### Dynamic Quantization

Quantize weights but keep activations in float32:

```python
import torch
from transformers import EdgeTamModel

model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf")

# Apply dynamic quantization
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear, torch.nn.Conv2d},
    dtype=torch.qint8
)

# Use normally
outputs = quantized_model(**inputs)
```

### Quantization Comparison

| Method | Size | CPU Speed | GPU Speed | Accuracy |
|--------|------|-----------|-----------|----------|
| FP32 (baseline) | 20MB | 1.0× | 1.0× | 72.3 J&F |
| FP16 | 10MB | 1.2× | 1.8× | 72.2 J&F |
| INT8 (PTQ) | 5MB | 1.8× | 1.1× | 71.5 J&F |
| INT8 (QAT) | 5MB | 2.1× | 1.3× | 72.0 J&F |

*PTQ = Post-Training Quantization, QAT = Quantization-Aware Training

## Performance Profiling

### PyTorch Profiler

Profile model performance to identify bottlenecks:

```python
import torch
from torch.profiler import profile, ProfilerActivity

model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf").to("cuda")

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True,
    with_stack=True
) as prof:
    with torch.no_grad():
        for _ in range(10):
            inputs = processor(images=image, input_boxes=boxes, return_tensors="pt").to("cuda")
            outputs = model(**inputs)

# Print summary
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))

# Export trace
prof.export_chrome_trace("edgetam_trace.json")
```

### Benchmark Script

```python
import torch
import time
from transformers import EdgeTamModel, Sam2Processor

def benchmark(model, processor, image, boxes, num_runs=100):
    model.eval()
    model = model.to("cuda")
    
    # Warmup
    for _ in range(10):
        inputs = processor(images=image, input_boxes=boxes, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = model(**inputs)
    
    # Benchmark
    torch.cuda.synchronize()
    start = time.time()
    
    for _ in range(num_runs):
        inputs = processor(images=image, input_boxes=boxes, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = model(**inputs)
        torch.cuda.synchronize()
    
    elapsed = time.time() - start
    fps = num_runs / elapsed
    latency = elapsed / num_runs * 1000  # ms
    
    print(f"FPS: {fps:.2f}")
    print(f"Latency: {latency:.2f}ms")
    
    return fps, latency

model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf")
processor = Sam2Processor.from_pretrained("yonigozlan/EdgeTAM-hf")
benchmark(model, processor, test_image, test_boxes)
```

## Memory Optimization

### Gradient Checkpointing

Reduce memory usage during training (or fine-tuning):

```python
from transformers import EdgeTamModel

model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf")
model.gradient_checkpointing_enable()

# Now training uses less memory but is slightly slower
```

### Embedding Caching

Cache image embeddings when processing multiple prompts on same image:

```python
# Process image once
inputs = processor(images=image, input_boxes=[box1], return_tensors="pt").to(device)
with torch.no_grad():
    outputs = model(**inputs)
    image_embeddings = outputs.image_embeddings

# Reuse embeddings for additional prompts
for new_box in [box2, box3, box4]:
    inputs = processor(
        input_boxes=[[new_box]],
        original_sizes=inputs["original_sizes"],
        return_tensors="pt"
    ).to(device)
    
    with torch.no_grad():
        refined_outputs = model(
            **inputs,
            image_embeddings=image_embeddings,  # Reuse!
            multimask_output=False
        )
```

**Memory Savings:**
- Image encoding: ~60% of total computation
- Cache size: ~50MB per 1024×1024 image
- Useful for interactive annotation workflows

### Video Memory Management

For long videos, manage memory by processing in chunks:

```python
def process_long_video(video_frames, chunk_size=100):
    results = {}
    
    for start_idx in range(0, len(video_frames), chunk_size):
        end_idx = min(start_idx + chunk_size, len(video_frames))
        chunk = video_frames[start_idx:end_idx]
        
        # Process chunk
        inference_session = video_processor.init_video_session(
            video=chunk,
            inference_device=device,
            torch_dtype=torch.bfloat16
        )
        
        # Add prompts on first frame of chunk
        video_processor.add_inputs_to_inference_session(
            inference_session=inference_session,
            frame_idx=0,
            obj_ids=1,
            input_boxes=[[[100, 100, 300, 300]]],
        )
        
        # Propagate through chunk
        for output in video_model.propagate_in_video_iterator(inference_session):
            results[start_idx + output.frame_idx] = output.pred_masks
        
        # Clear memory
        del inference_session
        torch.cuda.empty_cache()
    
    return results
```

## Batching Strategies

### Static Batching

Fixed batch size for predictable performance:

```python
def batch_inference_fixed(images, boxes, batch_size=8):
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

### Dynamic Batching

Adjust batch size based on image sizes:

```python
def batch_inference_dynamic(images, boxes, target_pixels=1024*1024*8):
    results = []
    current_batch = []
    current_boxes = []
    current_pixels = 0
    
    for img, box in zip(images, boxes):
        img_pixels = img.size[0] * img.size[1]
        
        if current_pixels + img_pixels > target_pixels and current_batch:
            # Process current batch
            inputs = processor(images=current_batch, input_boxes=current_boxes, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model(**inputs, multimask_output=False)
            masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])
            results.extend(masks)
            
            # Reset
            current_batch = []
            current_boxes = []
            current_pixels = 0
        
        current_batch.append(img)
        current_boxes.append(box)
        current_pixels += img_pixels
    
    # Process remaining
    if current_batch:
        inputs = processor(images=current_batch, input_boxes=current_boxes, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs, multimask_output=False)
        masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])
        results.extend(masks)
    
    return results
```

### Optimal Batch Sizes by Device

| Device | Image Size | Recommended Batch Size | Memory Usage |
|--------|-----------|------------------------|--------------|
| A100 (40GB) | 1024×1024 | 32 | ~35GB |
| RTX 3090 (24GB) | 1024×1024 | 16 | ~20GB |
| RTX 4060 (8GB) | 1024×1024 | 4 | ~6GB |
| CPU (32GB RAM) | 1024×1024 | 2 | ~4GB |

## Platform-Specific Optimizations

### CUDA Optimizations

**Enable TF32 on Ampere GPUs:**

```python
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
```

**Use Torch Compile (PyTorch 2.0+):**

```python
import torch
from transformers import EdgeTamModel

model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf").to("cuda")
model = torch.compile(model, mode="max-autotune")

# First run is slow (compilation)
# Subsequent runs are faster
```

**Results:** ~40% speedup on A100, ~25% on consumer GPUs

### CPU Optimizations

**Use OpenMP:**

```bash
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
```

**Enable Inference Mode:**

```python
import torch

with torch.inference_mode():  # Faster than torch.no_grad()
    outputs = model(**inputs)
```

**Use ONNX Runtime:**

```python
# Export to ONNX
torch.onnx.export(
    model,
    dummy_input,
    "edgetam.onnx",
    opset_version=14,
    input_names=['pixel_values', 'input_boxes'],
    output_names=['pred_masks', 'iou_scores'],
    dynamic_axes={
        'pixel_values': {0: 'batch', 2: 'height', 3: 'width'},
        'input_boxes': {0: 'batch', 1: 'num_objects'},
        'pred_masks': {0: 'batch', 1: 'num_objects'},
    }
)

# Run with ONNX Runtime
import onnxruntime as ort
session = ort.InferenceSession("edgetam.onnx", providers=['CPUExecutionProvider'])
outputs = session.run(None, {'pixel_values': pixel_values, 'input_boxes': input_boxes})
```

### Mobile Optimizations

**Reduce Input Resolution:**

```python
# Instead of 1024×1024, use 512×512 for mobile
image = image.resize((512, 512))
inputs = processor(images=image, input_boxes=scaled_boxes, return_tensors="pt")
```

**Use Asymmetric Quantization:**

Better for mobile NPUs/DSPs:

```python
# During CoreML export
--quantize INT8 --per_channel_quantization
```

**Limit Concurrent Operations:**

```swift
// iOS: Process one frame at a time
let serialQueue = DispatchQueue(label: "com.app.edgetam")
serialQueue.async {
    let masks = try model.prediction(inputs: inputs)
}
```

## Advanced Techniques

### Model Pruning

Remove unnecessary weights:

```python
import torch
import torch.nn.utils.prune as prune

model = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf")

# Prune 30% of weights in conv layers
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Conv2d):
        prune.l1_unstructured(module, name='weight', amount=0.3)
        prune.remove(module, 'weight')

# Fine-tune pruned model...
```

### Knowledge Distillation from Larger Models

Further improve EdgeTAM by distilling from SAM 2 Large:

```python
# Pseudo-code for distillation
teacher = Sam2Model.from_pretrained("facebook/sam2-large")
student = EdgeTamModel.from_pretrained("yonigozlan/EdgeTAM-hf")

for batch in dataloader:
    # Get teacher predictions
    with torch.no_grad():
        teacher_outputs = teacher(**batch)
    
    # Student forward pass
    student_outputs = student(**batch)
    
    # Distillation loss
    loss = (
        F.mse_loss(student_outputs.image_embeddings, teacher_outputs.image_embeddings) +
        F.binary_cross_entropy(student_outputs.pred_masks, teacher_outputs.pred_masks) +
        F.l1_loss(student_outputs.iou_scores, teacher_outputs.iou_scores)
    )
    
    loss.backward()
    optimizer.step()
```

### Neural Architecture Search (NAS)

Automatically find optimal architecture for specific hardware:

```python
# Use tools like Neural Network Intelligence (NNI)
# to search over:
# - Number of layers
# - Hidden dimensions
# - Attention window sizes
# - Activation functions
```

## Deployment Checklist

- [ ] Choose target platform (iOS, Android, Edge device, Server)
- [ ] Select appropriate quantization (FP16, INT8, none)
- [ ] Benchmark on target hardware
- [ ] Profile memory usage
- [ ] Test with representative data
- [ ] Implement error handling for OOM scenarios
- [ ] Add telemetry for production monitoring
- [ ] Document expected performance characteristics
- [ ] Set up CI/CD for model updates
- [ ] Plan for model versioning

## Performance Monitoring in Production

```python
import time
import logging

class EdgeTAMMonitor:
    def __init__(self):
        self.latencies = []
        self.memory_usage = []
    
    def log_inference(self, start_time, end_time, peak_memory):
        latency = (end_time - start_time) * 1000  # ms
        self.latencies.append(latency)
        self.memory_usage.append(peak_memory)
        
        # Log if performance degrades
        if latency > 100:  # threshold
            logging.warning(f"Slow inference: {latency:.2f}ms")
    
    def get_stats(self):
        return {
            'p50_latency': np.median(self.latencies),
            'p95_latency': np.percentile(self.latencies, 95),
            'p99_latency': np.percentile(self.latencies, 99),
            'avg_memory': np.mean(self.memory_usage)
        }
```

## Troubleshooting Performance Issues

### Issue: Slow inference on GPU

**Solutions:**
1. Enable TF32: `torch.backends.cuda.matmul.allow_tf32 = True`
2. Use `torch.compile()`
3. Check batch size (too small = inefficient)
4. Verify GPU utilization: `nvidia-smi dmon`

### Issue: Out of memory

**Solutions:**
1. Reduce batch size
2. Use FP16 or INT8
3. Enable gradient checkpointing (training)
4. Clear cache: `torch.cuda.empty_cache()`
5. Process video in chunks

### Issue: Poor accuracy after quantization

**Solutions:**
1. Use more calibration data
2. Try quantization-aware training instead of post-training
3. Use per-channel quantization
4. Keep batch norm layers in FP32

### Issue: Slow CoreML inference on iOS

**Solutions:**
1. Ensure using ANE (Apple Neural Engine): `compute_units=ALL`
2. Reduce input resolution
3. Use INT8 quantization
4. Check for unsupported ops forcing CPU fallback

## Resources

- **CoreML Tools**: https://github.com/apple/coremltools
- **ONNX Runtime**: https://onnxruntime.ai/
- **PyTorch Quantization**: https://pytorch.org/docs/stable/quantization.html
- **TensorRT**: https://developer.nvidia.com/tensorrt
- **Mobile Deployment Guide**: https://pytorch.org/mobile/home/
