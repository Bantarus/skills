---
name: litert-flutter-integration
description: Integrate LiteRT Next (v2) with Flutter applications for object detection and segmentation using platform channels on Android. Use this skill when implementing TFLite models in Flutter apps, setting up Android Kotlin native code bridges, or building real-time ML inference features with hardware acceleration support.
---

# LiteRT Flutter Integration

## Overview

This skill provides comprehensive guidance for integrating LiteRT Next (v2) - Google's successor to TensorFlow Lite - with Flutter applications on Android using platform channels. It covers the complete workflow from dependency setup through model deployment, with specific focus on object detection and segmentation tasks using hardware-accelerated inference.

LiteRT Next introduces simplified APIs with advanced GPU/NPU acceleration, async execution, and streamlined buffer handling, making it ideal for high-performance on-device ML applications.

## When to Use This Skill

Invoke this skill when:
- Integrating TFLite models (.tflite files) with Flutter applications
- Implementing object detection or image segmentation in Flutter apps
- Setting up Android platform channels for ML inference
- Migrating from TensorFlow Lite to LiteRT Next
- Building real-time camera-based ML applications in Flutter
- Optimizing ML model performance with hardware acceleration (GPU/NPU)

## Architecture Overview

The integration follows a three-layer architecture:

```
Flutter (Dart)
    ↕ Platform Channel (MethodChannel)
Android Native (Kotlin)
    ↕ LiteRT Next API
TFLite Model (.tflite)
```

## Implementation Workflow

### 1. Android Dependencies Setup

Configure the Android project with LiteRT Next dependencies. Edit `android/app/build.gradle`:

```gradle
android {
    compileSdk 34

    defaultConfig {
        minSdk 24
        targetSdk 34
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = '1.8'
    }
}

dependencies {
    // LiteRT Next (v2) - Alpha
    implementation 'com.google.ai.edge.litert:litert:2.0.0-alpha'

    // OR use stable LiteRT v1
    // implementation 'com.google.ai.edge.litert:litert:1.2.0'

    // Support library for preprocessing
    implementation 'com.google.ai.edge.litert:litert-support:0.4.4'

    // GPU acceleration (optional but recommended)
    implementation 'com.google.ai.edge.litert:litert-gpu:2.14.0'

    // Kotlin coroutines for async operations
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
}
```

Ensure `android/build.gradle` includes required repositories:

```gradle
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
```

### 2. Model Integration

Place TFLite models in the Android assets directory: `android/app/src/main/assets/`

Common model types for object detection and segmentation:
- **Object Detection**: YOLOv8/v9/v11, SSD MobileNet v2, EfficientDet
- **Segmentation**: DeepLab v3, U-Net variants

Models must be in `.tflite` format. For model conversion and optimization, refer to `references/model_conversion.md`.

### 3. Platform Channel Setup

#### 3.1 Flutter Side (Dart)

Create a platform channel in your Flutter code:

```dart
import 'package:flutter/services.dart';

class LiteRTService {
  static const platform = MethodChannel('com.yourapp.litert/inference');

  // Initialize model
  Future<bool> initializeModel({
    required String modelPath,
    bool useGPU = true,
    int numThreads = 4,
  }) async {
    try {
      final result = await platform.invokeMethod('initModel', {
        'modelPath': modelPath,
        'useGPU': useGPU,
        'numThreads': numThreads,
      });
      return result as bool;
    } on PlatformException catch (e) {
      print("Failed to initialize model: ${e.message}");
      return false;
    }
  }

  // Run object detection
  Future<List<Detection>> detectObjects(Uint8List imageBytes) async {
    try {
      final result = await platform.invokeMethod('detectObjects', {
        'imageBytes': imageBytes,
      });
      return (result as List).map((e) => Detection.fromMap(e)).toList();
    } on PlatformException catch (e) {
      print("Detection failed: ${e.message}");
      return [];
    }
  }

  // Run segmentation
  Future<Map<String, dynamic>> segmentImage(Uint8List imageBytes) async {
    try {
      final result = await platform.invokeMethod('segmentImage', {
        'imageBytes': imageBytes,
      });
      return Map<String, dynamic>.from(result);
    } on PlatformException catch (e) {
      print("Segmentation failed: ${e.message}");
      return {};
    }
  }

  // Dispose resources
  Future<void> dispose() async {
    await platform.invokeMethod('dispose');
  }
}

// Detection result model
class Detection {
  final String label;
  final double confidence;
  final Rect boundingBox;

  Detection({
    required this.label,
    required this.confidence,
    required this.boundingBox,
  });

  factory Detection.fromMap(Map<dynamic, dynamic> map) {
    return Detection(
      label: map['label'] as String,
      confidence: map['confidence'] as double,
      boundingBox: Rect.fromLTRB(
        map['left'] as double,
        map['top'] as double,
        map['right'] as double,
        map['bottom'] as double,
      ),
    );
  }
}
```

#### 3.2 Android Side (Kotlin)

Implement the platform channel handler in `android/app/src/main/kotlin/.../MainActivity.kt`:

```kotlin
package com.yourapp

import android.graphics.BitmapFactory
import android.graphics.Bitmap
import androidx.annotation.NonNull
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import kotlinx.coroutines.*

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.yourapp.litert/inference"
    private lateinit var inferenceHelper: LiteRTInferenceHelper
    private val coroutineScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    override fun configureFlutterEngine(@NonNull flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler {
            call, result ->
            when (call.method) {
                "initModel" -> {
                    val modelPath = call.argument<String>("modelPath")!!
                    val useGPU = call.argument<Boolean>("useGPU") ?: true
                    val numThreads = call.argument<Int>("numThreads") ?: 4

                    coroutineScope.launch {
                        try {
                            inferenceHelper = LiteRTInferenceHelper(
                                context = applicationContext,
                                modelPath = modelPath,
                                useGPU = useGPU,
                                numThreads = numThreads
                            )
                            result.success(true)
                        } catch (e: Exception) {
                            result.error("INIT_ERROR", e.message, null)
                        }
                    }
                }

                "detectObjects" -> {
                    val imageBytes = call.argument<ByteArray>("imageBytes")!!
                    coroutineScope.launch {
                        try {
                            val bitmap = BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
                            val detections = inferenceHelper.detectObjects(bitmap)
                            result.success(detections)
                        } catch (e: Exception) {
                            result.error("DETECTION_ERROR", e.message, null)
                        }
                    }
                }

                "segmentImage" -> {
                    val imageBytes = call.argument<ByteArray>("imageBytes")!!
                    coroutineScope.launch {
                        try {
                            val bitmap = BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
                            val segmentationResult = inferenceHelper.segmentImage(bitmap)
                            result.success(segmentationResult)
                        } catch (e: Exception) {
                            result.error("SEGMENTATION_ERROR", e.message, null)
                        }
                    }
                }

                "dispose" -> {
                    inferenceHelper.close()
                    result.success(null)
                }

                else -> result.notImplemented()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        coroutineScope.cancel()
    }
}
```

### 4. LiteRT Inference Implementation

Create `LiteRTInferenceHelper.kt` for model inference:

**For LiteRT Next (v2) API:**

```kotlin
import android.content.Context
import android.graphics.Bitmap
import com.google.ai.edge.litert.CompiledModel
import com.google.ai.edge.litert.Accelerator
import java.nio.ByteBuffer
import java.nio.ByteOrder

class LiteRTInferenceHelper(
    context: Context,
    modelPath: String,
    useGPU: Boolean = true,
    numThreads: Int = 4
) {
    private var model: CompiledModel
    private val inputSize = 640 // Common for YOLO models

    init {
        val options = CompiledModel.Options(
            accelerator = if (useGPU) Accelerator.GPU else Accelerator.CPU,
            numThreads = numThreads
        )

        model = CompiledModel.create(
            context.assets,
            modelPath,
            options
        )
    }

    fun detectObjects(bitmap: Bitmap): List<Map<String, Any>> {
        // Preprocess image
        val inputBuffer = preprocessImage(bitmap)

        // Run inference
        val outputBuffers = model.run(inputBuffer)

        // Postprocess results
        return postprocessDetections(outputBuffers)
    }

    fun segmentImage(bitmap: Bitmap): Map<String, Any> {
        val inputBuffer = preprocessImage(bitmap)
        val outputBuffers = model.run(inputBuffer)
        return postprocessSegmentation(outputBuffers)
    }

    private fun preprocessImage(bitmap: Bitmap): ByteBuffer {
        val resizedBitmap = Bitmap.createScaledBitmap(bitmap, inputSize, inputSize, true)
        val buffer = ByteBuffer.allocateDirect(4 * inputSize * inputSize * 3)
        buffer.order(ByteOrder.nativeOrder())

        val intValues = IntArray(inputSize * inputSize)
        resizedBitmap.getPixels(intValues, 0, inputSize, 0, 0, inputSize, inputSize)

        for (pixelValue in intValues) {
            buffer.putFloat(((pixelValue shr 16 and 0xFF) / 255.0f))
            buffer.putFloat(((pixelValue shr 8 and 0xFF) / 255.0f))
            buffer.putFloat(((pixelValue and 0xFF) / 255.0f))
        }

        return buffer
    }

    private fun postprocessDetections(outputBuffers: Array<ByteBuffer>): List<Map<String, Any>> {
        // Parse output tensors based on your model's output format
        // This is model-specific - YOLO, SSD, etc. have different formats
        val detections = mutableListOf<Map<String, Any>>()

        // Example for YOLO format (adjust based on your model)
        // outputBuffers typically contain: [boxes, scores, classes]

        return detections
    }

    private fun postprocessSegmentation(outputBuffers: Array<ByteBuffer>): Map<String, Any> {
        // Parse segmentation mask
        // Returns segmentation map and metadata
        return mapOf(
            "mask" to ByteArray(0), // Segmentation mask data
            "width" to inputSize,
            "height" to inputSize
        )
    }

    fun close() {
        model.close()
    }
}
```

**For Standard LiteRT v1 API (more stable):**

Refer to `references/litert_v1_implementation.md` for the Interpreter-based approach using the stable v1 API.

### 5. Real-Time Camera Integration

For real-time object detection with camera:

```dart
import 'package:camera/camera.dart';

class CameraDetectionScreen extends StatefulWidget {
  @override
  _CameraDetectionScreenState createState() => _CameraDetectionScreenState();
}

class _CameraDetectionScreenState extends State<CameraDetectionScreen> {
  CameraController? _cameraController;
  final LiteRTService _liteRTService = LiteRTService();
  List<Detection> _detections = [];
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _liteRTService.initializeModel(
      modelPath: 'yolov8n.tflite',
      useGPU: true,
    );
  }

  Future<void> _initializeCamera() async {
    final cameras = await availableCameras();
    _cameraController = CameraController(
      cameras.first,
      ResolutionPreset.medium,
      enableAudio: false,
    );

    await _cameraController!.initialize();
    _cameraController!.startImageStream(_processCameraImage);
    setState(() {});
  }

  Future<void> _processCameraImage(CameraImage image) async {
    if (_isProcessing) return;
    _isProcessing = true;

    try {
      final imageBytes = await _convertYUV420ToBytes(image);
      final detections = await _liteRTService.detectObjects(imageBytes);

      setState(() {
        _detections = detections;
      });
    } finally {
      _isProcessing = false;
    }
  }

  Future<Uint8List> _convertYUV420ToBytes(CameraImage image) async {
    // Convert YUV420 to RGB/JPEG bytes
    // Implementation depends on image format
    return Uint8List(0);
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    _liteRTService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return Center(child: CircularProgressIndicator());
    }

    return Stack(
      children: [
        CameraPreview(_cameraController!),
        CustomPaint(
          painter: DetectionPainter(_detections),
        ),
      ],
    );
  }
}

class DetectionPainter extends CustomPainter {
  final List<Detection> detections;

  DetectionPainter(this.detections);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.red
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    for (final detection in detections) {
      canvas.drawRect(detection.boundingBox, paint);

      final textPainter = TextPainter(
        text: TextSpan(
          text: '${detection.label} ${(detection.confidence * 100).toStringAsFixed(1)}%',
          style: TextStyle(color: Colors.red, fontSize: 14),
        ),
        textDirection: TextDirection.ltr,
      );

      textPainter.layout();
      textPainter.paint(canvas, detection.boundingBox.topLeft);
    }
  }

  @override
  bool shouldRepaint(DetectionPainter oldDelegate) => true;
}
```

## Performance Optimization

### Hardware Acceleration

LiteRT Next simplifies GPU/NPU acceleration:

```kotlin
// LiteRT Next v2
val options = CompiledModel.Options(
    accelerator = Accelerator.GPU,  // or Accelerator.NPU, Accelerator.CPU
    numThreads = 4
)
```

For best performance:
- Use **GPU** for image processing tasks (detection, segmentation)
- Use **NPU** when available for maximum efficiency
- Use **CPU** with multiple threads for compatibility
- Enable **async execution** for pipelined processing

### Async Execution

LiteRT Next supports true async inference:

```kotlin
coroutineScope.launch(Dispatchers.Default) {
    val result = withContext(Dispatchers.IO) {
        model.run(inputBuffer)
    }
    withContext(Dispatchers.Main) {
        // Update UI with results
    }
}
```

### Buffer Optimization

Use Android Hardware Buffers (AHWB) for zero-copy processing:

```kotlin
import android.hardware.HardwareBuffer

val hardwareBuffer = HardwareBuffer.create(
    width, height, HardwareBuffer.RGBA_8888,
    1, HardwareBuffer.USAGE_CPU_READ_OFTEN
)
```

## Model Selection Guide

### Object Detection Models

| Model | Speed | Accuracy | Size | Use Case |
|-------|-------|----------|------|----------|
| YOLOv8n | Fast | Good | 6MB | Real-time mobile apps |
| YOLOv8s | Medium | Better | 22MB | Balanced performance |
| SSD MobileNet v2 | Fast | Moderate | 10MB | Resource-constrained devices |
| EfficientDet-Lite | Medium | High | 15MB | High accuracy needed |

### Segmentation Models

| Model | Speed | Accuracy | Size | Use Case |
|-------|-------|----------|------|----------|
| DeepLab v3 MobileNet | Medium | Good | 9MB | General segmentation |
| U-Net Lite | Fast | Moderate | 5MB | Medical imaging |
| Portrait Segmentation | Very Fast | Specialized | 2MB | Background removal |

Download pre-trained models from:
- TensorFlow Hub: https://tfhub.dev/
- MediaPipe Models: https://developers.google.com/mediapipe/solutions/vision/
- Ultralytics YOLOv8: https://github.com/ultralytics/ultralytics

## Common Issues and Solutions

### Issue: Model Initialization Fails

**Solution**: Verify model is in `android/app/src/main/assets/` and path is correct (without `assets/` prefix):

```dart
await liteRTService.initializeModel(
  modelPath: 'yolov8n.tflite',  // Correct
  // NOT: 'assets/yolov8n.tflite'
);
```

### Issue: GPU Acceleration Not Working

**Solution**: Check GPU compatibility and fall back to CPU:

```kotlin
try {
    model = CompiledModel.create(context.assets, modelPath,
        CompiledModel.Options(Accelerator.GPU))
} catch (e: Exception) {
    // Fallback to CPU
    model = CompiledModel.create(context.assets, modelPath,
        CompiledModel.Options(Accelerator.CPU))
}
```

### Issue: Poor Inference Performance

**Solutions**:
1. Reduce input image size before processing
2. Use quantized models (INT8 instead of FP32)
3. Enable GPU/NPU acceleration
4. Implement frame skipping for camera streams
5. Use async processing with proper threading

### Issue: Platform Channel Communication Errors

**Solution**: Ensure proper error handling and type conversion:

```dart
try {
  final result = await platform.invokeMethod('method', args);
} on PlatformException catch (e) {
  debugPrint("Error: ${e.code}, ${e.message}");
} catch (e) {
  debugPrint("Unexpected error: $e");
}
```

## Version Information

- **LiteRT Next (v2)**: Alpha - `com.google.ai.edge.litert:litert:2.0.0-alpha`
- **LiteRT v1 (Stable)**: `com.google.ai.edge.litert:litert:1.2.0`
- **Flutter SDK**: 3.0+
- **Kotlin**: 1.8+
- **Android MinSDK**: 24 (Android 7.0)
- **Android TargetSDK**: 34 (Android 14)

## Resources

### Bundled References

- `references/litert_v1_implementation.md` - Complete Interpreter-based implementation for stable LiteRT v1
- `references/model_conversion.md` - Guide for converting PyTorch/TF models to TFLite format
- `references/api_reference.md` - Detailed LiteRT Kotlin API documentation
- `references/platform_channels_advanced.md` - Advanced platform channel patterns and optimizations

### Scripts

- `scripts/setup_android.sh` - Automated Android project configuration
- `scripts/model_validator.py` - Validate TFLite model compatibility

### External Documentation

- LiteRT Next Overview: https://ai.google.dev/edge/litert/next/overview
- LiteRT Android Kotlin: https://ai.google.dev/edge/litert/next/android_kotlin
- Flutter Platform Channels: https://docs.flutter.dev/platform-integration/platform-channels
- LiteRT Kotlin API: https://ai.google.dev/edge/api/litert/kotlin/classes
- LiteRT GitHub: https://github.com/google-ai-edge/LiteRT

## Best Practices

1. **Always dispose resources**: Call `dispose()` when done to free memory
2. **Use quantized models**: INT8 models are 4x smaller with minimal accuracy loss
3. **Implement proper error handling**: Platform channels can fail; handle gracefully
4. **Test on real devices**: Emulators may not support GPU acceleration
5. **Monitor memory usage**: Large models can cause OOM errors on low-end devices
6. **Cache model instances**: Avoid reloading models for each inference
7. **Use appropriate image sizes**: Match model's expected input dimensions
8. **Implement frame skipping**: For camera streams, skip frames if processing is slow
9. **Profile performance**: Use Android Profiler to identify bottlenecks
10. **Version compatibility**: Test with both LiteRT v1 (stable) and v2 (latest features)

## Quick Start Example

Complete minimal example for object detection:

1. Add dependencies to `android/app/build.gradle`
2. Place `yolov8n.tflite` in `android/app/src/main/assets/`
3. Implement platform channel in `MainActivity.kt`
4. Create `LiteRTInferenceHelper.kt`
5. Use `LiteRTService` from Flutter:

```dart
final service = LiteRTService();
await service.initializeModel(modelPath: 'yolov8n.tflite');
final detections = await service.detectObjects(imageBytes);
print('Found ${detections.length} objects');
```

For complete implementation examples, refer to the bundled references and scripts.
