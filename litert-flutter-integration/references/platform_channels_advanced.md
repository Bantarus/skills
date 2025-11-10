# Advanced Platform Channels

Advanced patterns and optimizations for Flutter platform channels in ML applications.

## Binary Data Transfer Optimization

### Large Image Transfer

When transferring camera frames or large images, optimize data transfer:

**Flutter Side**:

```dart
import 'dart:typed_data';
import 'package:flutter/services.dart';

class OptimizedImageTransfer {
  static const platform = MethodChannel('com.app/ml');

  // Efficient: Transfer as Uint8List
  Future<List<Detection>> detectFromBytes(Uint8List bytes) async {
    final result = await platform.invokeMethod('detect', {
      'imageData': bytes, // Binary data sent directly
      'width': width,
      'height': height,
      'format': 'yuv420', // Specify format
    });
    return parseDetections(result);
  }

  // For JPEG compression
  Future<List<Detection>> detectFromJPEG(Uint8List jpegBytes) async {
    final result = await platform.invokeMethod('detectJPEG', jpegBytes);
    return parseDetections(result);
  }
}
```

**Android Side (Kotlin)**:

```kotlin
MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "com.app/ml")
    .setMethodCallHandler { call, result ->
        when (call.method) {
            "detect" -> {
                val imageData = call.argument<ByteArray>("imageData")!!
                val width = call.argument<Int>("width")!!
                val height = call.argument<Int>("height")!!
                val format = call.argument<String>("format")!!

                scope.launch {
                    val bitmap = when (format) {
                        "yuv420" -> convertYUV420toBitmap(imageData, width, height)
                        "rgb" -> convertRGBtoBitmap(imageData, width, height)
                        else -> BitmapFactory.decodeByteArray(imageData, 0, imageData.size)
                    }

                    val detections = detector.detect(bitmap)
                    result.success(detections)
                }
            }

            "detectJPEG" -> {
                val jpegBytes = call.arguments as ByteArray
                scope.launch {
                    val bitmap = BitmapFactory.decodeByteArray(jpegBytes, 0, jpegBytes.size)
                    val detections = detector.detect(bitmap)
                    result.success(detections)
                }
            }
        }
    }
```

### YUV420 to Bitmap Conversion

```kotlin
import android.graphics.ImageFormat
import android.graphics.Rect
import android.graphics.YuvImage
import java.io.ByteArrayOutputStream

fun convertYUV420toBitmap(
    yuvData: ByteArray,
    width: Int,
    height: Int
): Bitmap {
    val yuvImage = YuvImage(yuvData, ImageFormat.NV21, width, height, null)
    val out = ByteArrayOutputStream()
    yuvImage.compressToJpeg(Rect(0, 0, width, height), 100, out)
    val jpegData = out.toByteArray()
    return BitmapFactory.decodeByteArray(jpegData, 0, jpegData.size)
}

// Or use RenderScript for faster conversion
fun convertYUV420toBitmapFast(
    yuvData: ByteArray,
    width: Int,
    height: Int,
    context: Context
): Bitmap {
    val rs = RenderScript.create(context)
    val yuvType = Type.Builder(rs, Element.U8(rs))
        .setX(yuvData.size)
        .create()

    val inputAllocation = Allocation.createTyped(rs, yuvType)
    inputAllocation.copyFrom(yuvData)

    val rgbaType = Type.Builder(rs, Element.RGBA_8888(rs))
        .setX(width)
        .setY(height)
        .create()

    val outputAllocation = Allocation.createTyped(rs, rgbaType)

    val scriptYuvToRgb = ScriptIntrinsicYuvToRGB.create(rs, Element.U8_4(rs))
    scriptYuvToRgb.setInput(inputAllocation)
    scriptYuvToRgb.forEach(outputAllocation)

    val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
    outputAllocation.copyTo(bitmap)

    inputAllocation.destroy()
    outputAllocation.destroy()
    scriptYuvToRgb.destroy()

    return bitmap
}
```

## Event Channels for Streaming

For continuous data streams (camera frames, real-time detections):

**Flutter Side**:

```dart
import 'package:flutter/services.dart';

class DetectionStream {
  static const EventChannel _eventChannel =
      EventChannel('com.app/ml/detections');

  Stream<List<Detection>>? _detectionStream;

  Stream<List<Detection>> get detections {
    _detectionStream ??= _eventChannel
        .receiveBroadcastStream()
        .map((event) => _parseDetections(event));
    return _detectionStream!;
  }

  List<Detection> _parseDetections(dynamic data) {
    final list = data as List;
    return list.map((e) => Detection.fromMap(e)).toList();
  }
}

// Usage
class DetectionWidget extends StatefulWidget {
  @override
  _DetectionWidgetState createState() => _DetectionWidgetState();
}

class _DetectionWidgetState extends State<DetectionWidget> {
  final DetectionStream _stream = DetectionStream();
  List<Detection> _latestDetections = [];

  @override
  void initState() {
    super.initState();
    _stream.detections.listen((detections) {
      setState(() {
        _latestDetections = detections;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: DetectionPainter(_latestDetections),
    );
  }
}
```

**Android Side (Kotlin)**:

```kotlin
import io.flutter.plugin.common.EventChannel

class DetectionEventHandler(
    private val detector: LiteRTInferenceHelper,
    private val scope: CoroutineScope
) : EventChannel.StreamHandler {

    private var eventSink: EventChannel.EventSink? = null
    private var job: Job? = null

    override fun onListen(arguments: Any?, events: EventChannel.EventSink?) {
        eventSink = events

        // Start continuous detection
        job = scope.launch {
            while (isActive) {
                try {
                    // Get latest frame from camera
                    val frame = getLatestCameraFrame()
                    val detections = detector.detectObjects(frame)

                    // Send to Flutter
                    withContext(Dispatchers.Main) {
                        eventSink?.success(detections)
                    }
                } catch (e: Exception) {
                    withContext(Dispatchers.Main) {
                        eventSink?.error("DETECTION_ERROR", e.message, null)
                    }
                }

                delay(33) // ~30 FPS
            }
        }
    }

    override fun onCancel(arguments: Any?) {
        job?.cancel()
        eventSink = null
    }
}

// Register in MainActivity
class MainActivity : FlutterActivity() {
    override fun configureFlutterEngine(@NonNull flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        EventChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            "com.app/ml/detections"
        ).setStreamHandler(DetectionEventHandler(detector, coroutineScope))
    }
}
```

## Background Execution

Execute ML inference on background thread without blocking UI:

**Android Side**:

```kotlin
class BackgroundInferenceHandler(
    private val model: CompiledModel
) {
    private val executor = Executors.newSingleThreadExecutor()

    fun runInference(
        input: ByteBuffer,
        callback: (Result<Array<ByteBuffer>>) -> Unit
    ) {
        executor.execute {
            try {
                val output = model.run(input)
                callback(Result.success(output))
            } catch (e: Exception) {
                callback(Result.failure(e))
            }
        }
    }

    fun shutdown() {
        executor.shutdown()
    }
}

// Usage in MainActivity
private val inferenceHandler = BackgroundInferenceHandler(model)

MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
    .setMethodCallHandler { call, result ->
        when (call.method) {
            "detect" -> {
                val imageBytes = call.argument<ByteArray>("imageBytes")!!
                val bitmap = BitmapFactory.decodeByteArray(
                    imageBytes, 0, imageBytes.size
                )

                inferenceHandler.runInference(preprocessImage(bitmap)) { output ->
                    output.onSuccess { buffers ->
                        val detections = postprocess(buffers)
                        result.success(detections)
                    }.onFailure { error ->
                        result.error("INFERENCE_ERROR", error.message, null)
                    }
                }
            }
        }
    }
```

## Caching and State Management

Maintain state across method calls:

```kotlin
class StatefulMLHandler(
    private val context: Context
) {
    private var currentModel: CompiledModel? = null
    private var modelCache = mutableMapOf<String, CompiledModel>()
    private var preprocessCache = mutableMapOf<String, ByteBuffer>()

    fun loadModel(modelPath: String, options: CompiledModel.Options): Boolean {
        return try {
            // Check cache first
            currentModel = modelCache.getOrPut(modelPath) {
                CompiledModel.create(context.assets, modelPath, options)
            }
            true
        } catch (e: Exception) {
            false
        }
    }

    fun runInference(
        input: ByteBuffer,
        cacheKey: String? = null
    ): Array<ByteBuffer>? {
        val model = currentModel ?: return null

        // Use cached preprocessed input if available
        val inputBuffer = if (cacheKey != null && preprocessCache.containsKey(cacheKey)) {
            preprocessCache[cacheKey]!!
        } else {
            input.also { if (cacheKey != null) preprocessCache[cacheKey] = it }
        }

        return model.run(inputBuffer)
    }

    fun clearCache() {
        preprocessCache.clear()
    }

    fun closeAll() {
        modelCache.values.forEach { it.close() }
        modelCache.clear()
        currentModel = null
    }
}
```

## Custom Codecs for Complex Data

For complex data structures:

**Flutter Side**:

```dart
import 'package:flutter/services.dart';

class CustomMessageCodec extends StandardMessageCodec {
  const CustomMessageCodec();

  @override
  void writeValue(WriteBuffer buffer, dynamic value) {
    if (value is Detection) {
      buffer.putUint8(128); // Custom type marker
      buffer.putFloat64(value.confidence);
      buffer.putString(value.label);
      buffer.putFloat64(value.boundingBox.left);
      buffer.putFloat64(value.boundingBox.top);
      buffer.putFloat64(value.boundingBox.right);
      buffer.putFloat64(value.boundingBox.bottom);
    } else {
      super.writeValue(buffer, value);
    }
  }

  @override
  dynamic readValueOfType(int type, ReadBuffer buffer) {
    if (type == 128) {
      final confidence = buffer.getFloat64();
      final label = buffer.getString();
      final left = buffer.getFloat64();
      final top = buffer.getFloat64();
      final right = buffer.getFloat64();
      final bottom = buffer.getFloat64();

      return Detection(
        confidence: confidence,
        label: label,
        boundingBox: Rect.fromLTRB(left, top, right, bottom),
      );
    }
    return super.readValueOfType(type, buffer);
  }
}

// Use custom codec
static const MethodChannel _channel = MethodChannel(
  'com.app/ml',
  StandardMethodCodec(CustomMessageCodec()),
);
```

## Performance Monitoring

Track platform channel performance:

**Flutter Side**:

```dart
class PerformanceMonitor {
  static const platform = MethodChannel('com.app/ml');

  Future<Map<String, dynamic>> runWithMetrics(
    String method,
    Map<String, dynamic> args,
  ) async {
    final startTime = DateTime.now();

    try {
      final result = await platform.invokeMethod(method, args);
      final endTime = DateTime.now();
      final duration = endTime.difference(startTime);

      return {
        'result': result,
        'duration_ms': duration.inMilliseconds,
        'success': true,
      };
    } catch (e) {
      final endTime = DateTime.now();
      final duration = endTime.difference(startTime);

      return {
        'error': e.toString(),
        'duration_ms': duration.inMilliseconds,
        'success': false,
      };
    }
  }
}

// Usage
final metrics = await PerformanceMonitor().runWithMetrics('detect', {
  'imageBytes': bytes,
});

print('Detection took: ${metrics['duration_ms']} ms');
if (metrics['success']) {
  final detections = metrics['result'];
}
```

**Android Side**:

```kotlin
class PerformanceTracker {
    data class Metrics(
        val totalTime: Long,
        val preprocessTime: Long,
        val inferenceTime: Long,
        val postprocessTime: Long
    )

    fun <T> trackInference(block: () -> T): Pair<T, Metrics> {
        val startTotal = System.nanoTime()

        val preprocessStart = System.nanoTime()
        // Preprocessing happens in block
        val preprocessEnd = System.nanoTime()

        val inferenceStart = System.nanoTime()
        val result = block()
        val inferenceEnd = System.nanoTime()

        val postprocessStart = System.nanoTime()
        // Postprocessing happens in block
        val postprocessEnd = System.nanoTime()

        val totalEnd = System.nanoTime()

        val metrics = Metrics(
            totalTime = (totalEnd - startTotal) / 1_000_000,
            preprocessTime = (preprocessEnd - preprocessStart) / 1_000_000,
            inferenceTime = (inferenceEnd - inferenceStart) / 1_000_000,
            postprocessTime = (postprocessEnd - postprocessStart) / 1_000_000
        )

        return Pair(result, metrics)
    }
}

// Usage
val tracker = PerformanceTracker()

MethodChannel(engine.dartExecutor.binaryMessenger, CHANNEL)
    .setMethodCallHandler { call, result ->
        when (call.method) {
            "detectWithMetrics" -> {
                val (detections, metrics) = tracker.trackInference {
                    runDetection(call.argument("imageBytes")!!)
                }

                result.success(mapOf(
                    "detections" to detections,
                    "metrics" to mapOf(
                        "total_ms" to metrics.totalTime,
                        "preprocess_ms" to metrics.preprocessTime,
                        "inference_ms" to metrics.inferenceTime,
                        "postprocess_ms" to metrics.postprocessTime
                    )
                ))
            }
        }
    }
```

## Error Recovery

Implement robust error handling:

```dart
class RobustMLChannel {
  static const platform = MethodChannel('com.app/ml');
  static const maxRetries = 3;

  Future<T?> invokeWithRetry<T>(
    String method,
    Map<String, dynamic> args, {
    int retries = maxRetries,
  }) async {
    for (int attempt = 0; attempt < retries; attempt++) {
      try {
        return await platform.invokeMethod<T>(method, args);
      } on PlatformException catch (e) {
        if (attempt == retries - 1) {
          // Last attempt failed
          print('All retries failed for $method: ${e.message}');
          return null;
        }

        // Handle specific errors
        if (e.code == 'GPU_ERROR') {
          // Try again with CPU
          args['useGPU'] = false;
        }

        // Exponential backoff
        await Future.delayed(Duration(milliseconds: 100 * (attempt + 1)));
      }
    }
    return null;
  }
}
```

## Memory-Efficient Frame Processing

Process camera frames without excessive memory allocation:

```dart
import 'dart:isolate';

class IsolateMLProcessor {
  SendPort? _sendPort;
  Isolate? _isolate;

  Future<void> init() async {
    final receivePort = ReceivePort();
    _isolate = await Isolate.spawn(_isolateEntry, receivePort.sendPort);
    _sendPort = await receivePort.first as SendPort;
  }

  static void _isolateEntry(SendPort sendPort) async {
    final receivePort = ReceivePort();
    sendPort.send(receivePort.sendPort);

    await for (final message in receivePort) {
      final imageBytes = message['bytes'] as Uint8List;
      final responsePort = message['responsePort'] as SendPort;

      // Process in isolate (background thread)
      const platform = MethodChannel('com.app/ml');
      try {
        final result = await platform.invokeMethod('detect', {
          'imageBytes': imageBytes,
        });
        responsePort.send({'success': true, 'result': result});
      } catch (e) {
        responsePort.send({'success': false, 'error': e.toString()});
      }
    }
  }

  Future<List<Detection>> process(Uint8List imageBytes) async {
    final responsePort = ReceivePort();
    _sendPort!.send({
      'bytes': imageBytes,
      'responsePort': responsePort.sendPort,
    });

    final response = await responsePort.first as Map;
    if (response['success']) {
      return _parseDetections(response['result']);
    } else {
      throw Exception(response['error']);
    }
  }

  void dispose() {
    _isolate?.kill();
  }
}
```

## Best Practices Summary

1. **Use Uint8List for binary data** - More efficient than List<int>
2. **Implement EventChannel for streams** - Better than polling with MethodChannel
3. **Run inference on background thread** - Never block the UI thread
4. **Cache models and preprocessed data** - Avoid reloading
5. **Implement proper error handling** - Handle GPU failures gracefully
6. **Monitor performance** - Track inference times and bottlenecks
7. **Use appropriate data formats** - YUV420 for camera, JPEG for storage
8. **Implement frame skipping** - Don't process every frame if lagging
9. **Clean up resources** - Close models and free memory
10. **Test on real devices** - Emulators don't support GPU acceleration
