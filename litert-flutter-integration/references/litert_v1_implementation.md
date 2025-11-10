# LiteRT v1 Implementation (Stable)

This reference provides a complete implementation using the stable LiteRT v1 API with the Interpreter-based approach.

## Dependencies

```gradle
dependencies {
    // Stable LiteRT v1
    implementation 'com.google.ai.edge.litert:litert:1.2.0'
    implementation 'com.google.ai.edge.litert:litert-support:0.4.4'
    implementation 'com.google.ai.edge.litert:litert-gpu:2.14.0'

    // Kotlin coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
}
```

## LiteRTInferenceHelper.kt (Interpreter-based)

```kotlin
import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.CompatibilityList
import org.tensorflow.lite.gpu.GpuDelegate
import org.tensorflow.lite.support.common.FileUtil
import org.tensorflow.lite.support.common.ops.NormalizeOp
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer
import java.nio.ByteBuffer
import java.nio.ByteOrder

class LiteRTInferenceHelper(
    private val context: Context,
    modelPath: String,
    useGPU: Boolean = true,
    numThreads: Int = 4
) {
    private var interpreter: Interpreter
    private var gpuDelegate: GpuDelegate? = null
    private val inputSize: Int
    private val outputSize: Int
    private var labels: List<String> = emptyList()

    init {
        // Load model
        val modelBuffer = FileUtil.loadMappedFile(context, modelPath)

        // Configure interpreter options
        val options = Interpreter.Options()
        options.setNumThreads(numThreads)

        // Setup GPU delegate if requested and available
        if (useGPU && CompatibilityList().isDelegateSupportedOnThisDevice) {
            gpuDelegate = GpuDelegate(
                GpuDelegate.Options().apply {
                    setPrecisionLossAllowed(true)
                    setInferencePreference(GpuDelegate.Options.INFERENCE_PREFERENCE_FAST_SINGLE_ANSWER)
                }
            )
            options.addDelegate(gpuDelegate)
        }

        interpreter = Interpreter(modelBuffer, options)

        // Get input/output tensor info
        val inputShape = interpreter.getInputTensor(0).shape()
        inputSize = inputShape[1] // Assuming [1, height, width, channels]

        val outputShape = interpreter.getOutputTensor(0).shape()
        outputSize = outputShape[1]

        // Load labels if available
        try {
            labels = FileUtil.loadLabels(context, "labels.txt")
        } catch (e: Exception) {
            // Labels file not found, will use indices
        }
    }

    fun detectObjects(bitmap: Bitmap): List<Map<String, Any>> {
        // Preprocess image
        val tensorImage = preprocessImage(bitmap)

        // Prepare output buffers
        val outputBuffers = prepareOutputBuffers()

        // Run inference
        interpreter.runForMultipleInputsOutputs(
            arrayOf(tensorImage.buffer),
            outputBuffers
        )

        // Postprocess detections
        return postprocessDetections(outputBuffers)
    }

    fun segmentImage(bitmap: Bitmap): Map<String, Any> {
        val tensorImage = preprocessImage(bitmap)

        // Output buffer for segmentation mask
        val outputBuffer = ByteBuffer.allocateDirect(4 * inputSize * inputSize)
        outputBuffer.order(ByteOrder.nativeOrder())

        interpreter.run(tensorImage.buffer, outputBuffer)

        return postprocessSegmentation(outputBuffer)
    }

    private fun preprocessImage(bitmap: Bitmap): TensorImage {
        val imageProcessor = ImageProcessor.Builder()
            .add(ResizeOp(inputSize, inputSize, ResizeOp.ResizeMethod.BILINEAR))
            .add(NormalizeOp(0f, 255f)) // Normalize to [0, 1]
            .build()

        var tensorImage = TensorImage.fromBitmap(bitmap)
        tensorImage = imageProcessor.process(tensorImage)

        return tensorImage
    }

    private fun prepareOutputBuffers(): Map<Int, Any> {
        // For YOLO-style models, typical outputs are:
        // 0: locations (num_detections, 4) - bounding boxes
        // 1: classes (num_detections) - class indices
        // 2: scores (num_detections) - confidence scores
        // 3: num_detections - number of valid detections

        return mapOf(
            0 to Array(1) { Array(10) { FloatArray(4) } }, // boxes
            1 to Array(1) { FloatArray(10) },               // classes
            2 to Array(1) { FloatArray(10) },               // scores
            3 to FloatArray(1)                               // num detections
        )
    }

    private fun postprocessDetections(outputs: Map<Int, Any>): List<Map<String, Any>> {
        val detections = mutableListOf<Map<String, Any>>()

        val boxes = outputs[0] as Array<Array<FloatArray>>
        val classes = outputs[1] as Array<FloatArray>
        val scores = outputs[2] as Array<FloatArray>
        val numDetections = (outputs[3] as FloatArray)[0].toInt()

        val confidenceThreshold = 0.5f

        for (i in 0 until numDetections.coerceAtMost(10)) {
            val score = scores[0][i]
            if (score < confidenceThreshold) continue

            val classIndex = classes[0][i].toInt()
            val label = if (labels.isNotEmpty() && classIndex < labels.size) {
                labels[classIndex]
            } else {
                "Class $classIndex"
            }

            val box = boxes[0][i]

            detections.add(mapOf(
                "label" to label,
                "confidence" to score.toDouble(),
                "top" to box[0].toDouble(),
                "left" to box[1].toDouble(),
                "bottom" to box[2].toDouble(),
                "right" to box[3].toDouble()
            ))
        }

        return detections
    }

    private fun postprocessSegmentation(outputBuffer: ByteBuffer): Map<String, Any> {
        outputBuffer.rewind()

        val maskData = FloatArray(inputSize * inputSize)
        outputBuffer.asFloatBuffer().get(maskData)

        // Convert float mask to byte array for transfer
        val byteArray = ByteArray(maskData.size)
        for (i in maskData.indices) {
            byteArray[i] = (maskData[i] * 255).toInt().coerceIn(0, 255).toByte()
        }

        return mapOf(
            "mask" to byteArray,
            "width" to inputSize,
            "height" to inputSize,
            "format" to "grayscale"
        )
    }

    fun getInputSize(): Int = inputSize

    fun getModelInfo(): Map<String, Any> {
        return mapOf(
            "inputShape" to interpreter.getInputTensor(0).shape(),
            "outputShape" to interpreter.getOutputTensor(0).shape(),
            "inputDataType" to interpreter.getInputTensor(0).dataType().name,
            "outputDataType" to interpreter.getOutputTensor(0).dataType().name,
            "numLabels" to labels.size
        )
    }

    fun close() {
        interpreter.close()
        gpuDelegate?.close()
    }
}
```

## Object Detection with YOLO Models

For YOLO models (v5, v8, v9, v11), the output format is typically different:

```kotlin
private fun postprocessYOLODetections(outputBuffer: ByteBuffer): List<Map<String, Any>> {
    outputBuffer.rewind()
    val detections = mutableListOf<Map<String, Any>>()

    // YOLO output shape: [1, 25200, 85] for 80 classes (COCO)
    // Format: [x, y, w, h, objectness, class_0_prob, ..., class_79_prob]

    val numPredictions = 25200
    val numClasses = 80
    val confidenceThreshold = 0.5f
    val iouThreshold = 0.45f

    val rawDetections = mutableListOf<Detection>()

    for (i in 0 until numPredictions) {
        val baseIndex = i * (5 + numClasses)

        val centerX = outputBuffer.getFloat(baseIndex * 4)
        val centerY = outputBuffer.getFloat((baseIndex + 1) * 4)
        val width = outputBuffer.getFloat((baseIndex + 2) * 4)
        val height = outputBuffer.getFloat((baseIndex + 3) * 4)
        val objectness = outputBuffer.getFloat((baseIndex + 4) * 4)

        if (objectness < confidenceThreshold) continue

        // Find best class
        var maxClassScore = 0f
        var maxClassIndex = 0

        for (c in 0 until numClasses) {
            val classScore = outputBuffer.getFloat((baseIndex + 5 + c) * 4)
            if (classScore > maxClassScore) {
                maxClassScore = classScore
                maxClassIndex = c
            }
        }

        val confidence = objectness * maxClassScore
        if (confidence < confidenceThreshold) continue

        rawDetections.add(Detection(
            classIndex = maxClassIndex,
            confidence = confidence,
            left = centerX - width / 2f,
            top = centerY - height / 2f,
            right = centerX + width / 2f,
            bottom = centerY + height / 2f
        ))
    }

    // Apply Non-Maximum Suppression (NMS)
    val finalDetections = applyNMS(rawDetections, iouThreshold)

    return finalDetections.map { det ->
        mapOf(
            "label" to (labels.getOrNull(det.classIndex) ?: "Class ${det.classIndex}"),
            "confidence" to det.confidence.toDouble(),
            "top" to det.top.toDouble(),
            "left" to det.left.toDouble(),
            "bottom" to det.bottom.toDouble(),
            "right" to det.right.toDouble()
        )
    }
}

data class Detection(
    val classIndex: Int,
    val confidence: Float,
    val left: Float,
    val top: Float,
    val right: Float,
    val bottom: Float
)

private fun applyNMS(detections: List<Detection>, iouThreshold: Float): List<Detection> {
    val sortedDetections = detections.sortedByDescending { it.confidence }
    val selectedDetections = mutableListOf<Detection>()

    for (detection in sortedDetections) {
        var shouldSelect = true

        for (selectedDetection in selectedDetections) {
            if (detection.classIndex == selectedDetection.classIndex) {
                val iou = calculateIOU(detection, selectedDetection)
                if (iou > iouThreshold) {
                    shouldSelect = false
                    break
                }
            }
        }

        if (shouldSelect) {
            selectedDetections.add(detection)
        }
    }

    return selectedDetections
}

private fun calculateIOU(box1: Detection, box2: Detection): Float {
    val intersectionLeft = maxOf(box1.left, box2.left)
    val intersectionTop = maxOf(box1.top, box2.top)
    val intersectionRight = minOf(box1.right, box2.right)
    val intersectionBottom = minOf(box1.bottom, box2.bottom)

    if (intersectionRight < intersectionLeft || intersectionBottom < intersectionTop) {
        return 0f
    }

    val intersectionArea = (intersectionRight - intersectionLeft) * (intersectionBottom - intersectionTop)

    val box1Area = (box1.right - box1.left) * (box1.bottom - box1.top)
    val box2Area = (box2.right - box2.left) * (box2.bottom - box2.top)

    val unionArea = box1Area + box2Area - intersectionArea

    return intersectionArea / unionArea
}
```

## Image Segmentation with DeepLab

```kotlin
class DeepLabSegmentation(
    context: Context,
    modelPath: String = "deeplabv3.tflite"
) {
    private val interpreter: Interpreter
    private val inputSize = 257 // DeepLab standard input size
    private val numClasses = 21 // PASCAL VOC classes

    init {
        val modelBuffer = FileUtil.loadMappedFile(context, modelPath)
        interpreter = Interpreter(modelBuffer)
    }

    fun segment(bitmap: Bitmap): SegmentationResult {
        val tensorImage = preprocessImage(bitmap)

        // Output: [1, height, width, numClasses]
        val outputBuffer = Array(1) {
            Array(inputSize) {
                Array(inputSize) {
                    FloatArray(numClasses)
                }
            }
        }

        interpreter.run(tensorImage.buffer, outputBuffer)

        return postprocessSegmentation(outputBuffer[0])
    }

    private fun preprocessImage(bitmap: Bitmap): TensorImage {
        val imageProcessor = ImageProcessor.Builder()
            .add(ResizeOp(inputSize, inputSize, ResizeOp.ResizeMethod.BILINEAR))
            .add(NormalizeOp(127.5f, 127.5f)) // Normalize to [-1, 1]
            .build()

        var tensorImage = TensorImage.fromBitmap(bitmap)
        tensorImage = imageProcessor.process(tensorImage)

        return tensorImage
    }

    private fun postprocessSegmentation(output: Array<Array<FloatArray>>): SegmentationResult {
        val maskData = ByteArray(inputSize * inputSize)
        val colorMap = IntArray(inputSize * inputSize)

        for (y in 0 until inputSize) {
            for (x in 0 until inputSize) {
                var maxProb = 0f
                var maxClass = 0

                for (c in 0 until numClasses) {
                    if (output[y][x][c] > maxProb) {
                        maxProb = output[y][x][c]
                        maxClass = c
                    }
                }

                val index = y * inputSize + x
                maskData[index] = maxClass.toByte()
                colorMap[index] = getColorForClass(maxClass)
            }
        }

        return SegmentationResult(
            mask = maskData,
            colorMap = colorMap,
            width = inputSize,
            height = inputSize
        )
    }

    private fun getColorForClass(classIndex: Int): Int {
        val colors = arrayOf(
            0xFF000000.toInt(), // Background - black
            0xFFFF0000.toInt(), // Class 1 - red
            0xFF00FF00.toInt(), // Class 2 - green
            0xFF0000FF.toInt(), // Class 3 - blue
            // ... more colors for other classes
        )
        return colors.getOrElse(classIndex) { 0xFFFFFFFF.toInt() }
    }

    fun close() {
        interpreter.close()
    }
}

data class SegmentationResult(
    val mask: ByteArray,
    val colorMap: IntArray,
    val width: Int,
    val height: Int
)
```

## Performance Tips

1. **Reuse TensorImage objects** to avoid allocation overhead:

```kotlin
private var tensorImage: TensorImage? = null

private fun preprocessImageEfficient(bitmap: Bitmap): TensorImage {
    if (tensorImage == null) {
        tensorImage = TensorImage.fromBitmap(bitmap)
    } else {
        tensorImage!!.load(bitmap)
    }

    return imageProcessor.process(tensorImage!!)
}
```

2. **Use quantized models** for better performance:

```kotlin
// INT8 quantized models are automatically handled by the interpreter
// Check if model is quantized:
val isQuantized = interpreter.getInputTensor(0).dataType() == DataType.UINT8
```

3. **Batch processing** for multiple images:

```kotlin
fun detectObjectsBatch(bitmaps: List<Bitmap>): List<List<Map<String, Any>>> {
    val batchSize = bitmaps.size
    val inputArray = Array(batchSize) { i ->
        preprocessImage(bitmaps[i]).buffer
    }

    val outputBuffers = Array(batchSize) {
        prepareOutputBuffers()
    }

    // Run batch inference
    interpreter.runForMultipleInputsOutputs(inputArray, outputBuffers)

    return outputBuffers.map { postprocessDetections(it) }
}
```

## Migration from TensorFlow Lite

If migrating from `org.tensorflow:tensorflow-lite`, the main changes are:

```kotlin
// Old
import org.tensorflow.lite.Interpreter

// New
import org.tensorflow.lite.Interpreter  // Same import, different package

// Dependencies changed from:
// implementation 'org.tensorflow:tensorflow-lite:2.13.0'

// To:
// implementation 'com.google.ai.edge.litert:litert:1.2.0'
```

The API remains largely compatible, with minimal code changes required.
