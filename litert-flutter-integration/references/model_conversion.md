# Model Conversion Guide

This reference provides comprehensive instructions for converting various ML models to TFLite format for use with LiteRT.

## Overview

TFLite (.tflite) models can be created from:
- TensorFlow/Keras models
- PyTorch models
- ONNX models
- Pre-trained models from model zoos

## Converting TensorFlow/Keras Models

### Basic Conversion

```python
import tensorflow as tf

# Load your Keras model
model = tf.keras.models.load_model('model.h5')

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the model
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

### With INT8 Quantization (Recommended)

```python
import tensorflow as tf
import numpy as np

def representative_dataset():
    """
    Generator function to provide representative dataset
    for quantization calibration
    """
    for _ in range(100):
        # Provide sample input data matching your model's input shape
        # Example: for 640x640 RGB images
        data = np.random.rand(1, 640, 640, 3).astype(np.float32)
        yield [data]

# Load model
model = tf.keras.models.load_model('model.h5')

# Configure converter for quantization
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Enable INT8 quantization
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset

# Ensure INT8 for input/output (optional, for full integer quantization)
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8

# Convert
tflite_quant_model = converter.convert()

# Save
with open('model_quantized.tflite', 'wb') as f:
    f.write(tflite_quant_model)
```

### With FP16 Quantization

```python
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]

tflite_fp16_model = converter.convert()

with open('model_fp16.tflite', 'wb') as f:
    f.write(tflite_fp16_model)
```

## Converting PyTorch Models

### Method 1: Via ONNX (Recommended)

```python
import torch
import onnx
from onnx_tf.backend import prepare
import tensorflow as tf

# Step 1: Export PyTorch model to ONNX
model = torch.load('model.pth')
model.eval()

dummy_input = torch.randn(1, 3, 640, 640)
torch.onnx.export(
    model,
    dummy_input,
    'model.onnx',
    export_params=True,
    opset_version=13,
    do_constant_folding=True,
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={
        'input': {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)

# Step 2: Convert ONNX to TensorFlow SavedModel
onnx_model = onnx.load('model.onnx')
tf_rep = prepare(onnx_model)
tf_rep.export_graph('saved_model')

# Step 3: Convert SavedModel to TFLite
converter = tf.lite.TFLiteConverter.from_saved_model('saved_model')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

### Method 2: Using AI Edge Torch (New)

```python
import torch
import ai_edge_torch

# Load PyTorch model
model = torch.load('model.pth')
model.eval()

# Sample input
sample_input = (torch.randn(1, 3, 640, 640),)

# Convert directly to TFLite
edge_model = ai_edge_torch.convert(model, sample_input)

# Save
edge_model.export('model.tflite')
```

## Converting YOLO Models

### YOLOv8 (Ultralytics)

```python
from ultralytics import YOLO

# Load model
model = YOLO('yolov8n.pt')

# Export to TFLite with INT8 quantization
model.export(
    format='tflite',
    imgsz=640,
    int8=True,
    data='coco128.yaml'  # Dataset for calibration
)

# Or without quantization
model.export(format='tflite', imgsz=640)
```

### YOLOv5

```bash
# Clone YOLOv5 repository
git clone https://github.com/ultralytics/yolov5
cd yolov5

# Install requirements
pip install -r requirements.txt

# Export to TFLite
python export.py --weights yolov5s.pt --include tflite --img 640

# With INT8 quantization
python export.py --weights yolov5s.pt --include tflite --int8 --img 640
```

## Converting Segmentation Models

### DeepLab v3

```python
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2

# Create DeepLab model (example)
def create_deeplabv3(input_shape=(257, 257, 3), num_classes=21):
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )

    # Add DeepLab head
    # ... (full architecture implementation)

    return model

model = create_deeplabv3()

# Convert with quantization
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

with open('deeplabv3.tflite', 'wb') as f:
    f.write(tflite_model)
```

### U-Net

```python
import tensorflow as tf

# Load U-Net model
model = tf.keras.models.load_model('unet_model.h5')

# Convert with INT8 quantization
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Representative dataset for medical imaging
def representative_dataset():
    for _ in range(100):
        # Provide medical image samples
        data = np.random.rand(1, 256, 256, 1).astype(np.float32)
        yield [data]

converter.representative_dataset = representative_dataset

tflite_model = converter.convert()

with open('unet.tflite', 'wb') as f:
    f.write(tflite_model)
```

## Model Metadata

Add metadata to make models more usable:

```python
from tflite_support import flatbuffers
from tflite_support import metadata as _metadata
from tflite_support import metadata_schema_py_generated as _metadata_fb

# Load the model
with open('model.tflite', 'rb') as f:
    model_buffer = f.read()

model_meta = _metadata_fb.ModelMetadataT()
model_meta.name = "Object Detection Model"
model_meta.description = "YOLOv8n model for object detection on mobile devices"
model_meta.version = "1.0.0"
model_meta.author = "Your Name"

# Input metadata
input_meta = _metadata_fb.TensorMetadataT()
input_meta.name = "image"
input_meta.description = "Input image (RGB)"
input_meta.content = _metadata_fb.ContentT()
input_meta.content.contentProperties = _metadata_fb.ImagePropertiesT()
input_meta.content.contentProperties.colorSpace = _metadata_fb.ColorSpaceType.RGB
input_meta.content.contentPropertiesType = _metadata_fb.ContentProperties.ImageProperties

# Normalization
input_normalization = _metadata_fb.ProcessUnitT()
input_normalization.optionsType = _metadata_fb.ProcessUnitOptions.NormalizationOptions
input_normalization.options = _metadata_fb.NormalizationOptionsT()
input_normalization.options.mean = [0.0]
input_normalization.options.std = [255.0]
input_meta.processUnits = [input_normalization]

# Output metadata
output_meta = _metadata_fb.TensorMetadataT()
output_meta.name = "detections"
output_meta.description = "Detected objects"

# Add to model
model_meta.subgraphMetadata = [_metadata_fb.SubGraphMetadataT()]
model_meta.subgraphMetadata[0].inputTensorMetadata = [input_meta]
model_meta.subgraphMetadata[0].outputTensorMetadata = [output_meta]

# Create metadata
b = flatbuffers.Builder(0)
b.Finish(model_meta.Pack(b), _metadata.MetadataPopulator.METADATA_FILE_IDENTIFIER)
metadata_buf = b.Output()

# Populate metadata
populator = _metadata.MetadataPopulator.with_model_buffer(model_buffer)
populator.load_metadata_buffer(metadata_buf)

# Add labels file
populator.load_associated_files(["labels.txt"])

# Export
populator.populate()
with open('model_with_metadata.tflite', 'wb') as f:
    f.write(populator.get_model_buffer())
```

## Validation

### Validate Model Structure

```python
import tensorflow as tf

# Load and inspect model
interpreter = tf.lite.Interpreter(model_path='model.tflite')
interpreter.allocate_tensors()

# Get input details
input_details = interpreter.get_input_details()
print("Input shape:", input_details[0]['shape'])
print("Input type:", input_details[0]['dtype'])

# Get output details
output_details = interpreter.get_output_details()
print("Output shape:", output_details[0]['shape'])
print("Output type:", output_details[0]['dtype'])

# Check quantization
is_quantized = input_details[0]['dtype'] == np.uint8
print("Is quantized:", is_quantized)
```

### Test Inference

```python
import numpy as np
from PIL import Image

# Load model
interpreter = tf.lite.Interpreter(model_path='model.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load and preprocess test image
image = Image.open('test.jpg').resize((640, 640))
input_data = np.array(image, dtype=np.float32)
input_data = np.expand_dims(input_data, axis=0)

# For quantized models
if input_details[0]['dtype'] == np.uint8:
    input_scale, input_zero_point = input_details[0]['quantization']
    input_data = input_data / input_scale + input_zero_point
    input_data = input_data.astype(np.uint8)

# Run inference
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()

# Get output
output_data = interpreter.get_tensor(output_details[0]['index'])
print("Output shape:", output_data.shape)
print("Sample output:", output_data[0, :5])
```

## Model Optimization Best Practices

### 1. Use Post-Training Quantization

**Benefits**:
- 4x smaller model size
- 2-4x faster inference
- < 1% accuracy loss typically

**When to use**: Almost always for mobile deployment

### 2. Dynamic Range Quantization

```python
converter.optimizations = [tf.lite.Optimize.DEFAULT]
```

**Best for**: Models without representative dataset available

### 3. Full Integer Quantization

```python
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8
```

**Best for**: Maximum performance on edge devices

### 4. Reduce Input Resolution

```python
# Instead of 640x640
model.export(format='tflite', imgsz=320)
```

**Trade-off**: Faster inference vs. accuracy for small objects

### 5. Use MobileNet Backbones

Models like MobileNetV2, EfficientNet-Lite are optimized for mobile:

```python
from tensorflow.keras.applications import MobileNetV3Small

base_model = MobileNetV3Small(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
```

## Common Issues

### Issue: Unsupported Operations

**Error**: "Some ops are not supported by the native TFLite runtime"

**Solution**: Use SELECT_TF_OPS:

```python
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,
    tf.lite.OpsSet.SELECT_TF_OPS
]
```

### Issue: Model Too Large

**Solutions**:
1. Apply quantization
2. Reduce input resolution
3. Use smaller architecture (e.g., YOLOv8n instead of YOLOv8x)
4. Prune model weights

### Issue: Poor Accuracy After Quantization

**Solutions**:
1. Use larger representative dataset (500+ samples)
2. Use FP16 instead of INT8
3. Apply Quantization-Aware Training (QAT)

## Quantization-Aware Training (QAT)

For critical applications requiring maximum accuracy:

```python
import tensorflow as tf
import tensorflow_model_optimization as tfmot

# Load model
model = tf.keras.models.load_model('model.h5')

# Apply quantization-aware training
quantize_model = tfmot.quantization.keras.quantize_model
q_aware_model = quantize_model(model)

# Compile and fine-tune
q_aware_model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

q_aware_model.fit(train_dataset, epochs=5, validation_data=val_dataset)

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(q_aware_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_qat_model = converter.convert()

with open('model_qat.tflite', 'wb') as f:
    f.write(tflite_qat_model)
```

## Pre-Trained Model Sources

### TensorFlow Hub
```python
import tensorflow_hub as hub

# Load pre-trained model
model = hub.load('https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2')

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_saved_model(model)
tflite_model = converter.convert()
```

### MediaPipe Models

Download from: https://developers.google.com/mediapipe/solutions/vision/

Available models:
- Object detection (EfficientDet-Lite)
- Image segmentation (DeepLab, Selfie segmentation)
- Pose detection
- Face detection

### Ultralytics Model Zoo

```bash
# Download YOLOv8 variants
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
```

## Tools

### TFLite Model Analyzer

```bash
# Install
pip install tensorflow

# Analyze model
python -m tensorflow.lite.tools.flatbuffer_utils \
    --input_model model.tflite \
    --output_html model_analysis.html
```

### TFLite Visualizer

Online tool: https://netron.app/

Supports drag-and-drop of .tflite files for visualization.

### Benchmark Tool

```bash
# Download Android benchmark tool
wget https://storage.googleapis.com/tensorflow-nightly-public/prod/tensorflow/release/lite/tools/nightly/latest/android_aarch64_benchmark_model.apk

# Run benchmark
adb push model.tflite /data/local/tmp/
adb shell /data/local/tmp/benchmark_model \
    --graph=/data/local/tmp/model.tflite \
    --num_threads=4 \
    --use_gpu=true
```

## Recommended Workflow

1. **Train** model in TensorFlow/PyTorch
2. **Export** to TFLite with FP32 (baseline)
3. **Test** accuracy and performance
4. **Apply** INT8 quantization
5. **Compare** accuracy vs. baseline
6. **Iterate** with QAT if accuracy drop is significant
7. **Benchmark** on target device
8. **Deploy** with metadata and labels

## Size Comparison

Typical model sizes:

| Model | FP32 | FP16 | INT8 | Accuracy Loss |
|-------|------|------|------|---------------|
| YOLOv8n | 6.2 MB | 3.2 MB | 1.6 MB | < 1% |
| YOLOv8s | 22 MB | 11 MB | 5.5 MB | < 1% |
| MobileNetV2 | 14 MB | 7 MB | 3.5 MB | < 2% |
| DeepLab v3 | 9 MB | 4.5 MB | 2.3 MB | < 2% |

INT8 quantization provides the best size-to-accuracy ratio for mobile deployment.
