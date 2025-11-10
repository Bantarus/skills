# LiteRT Kotlin API Reference

Comprehensive reference for LiteRT Next (v2) and LiteRT v1 Kotlin APIs.

## LiteRT Next (v2) API

Package: `com.google.ai.edge.litert`

### CompiledModel

Main class for model loading and inference in LiteRT Next.

```kotlin
class CompiledModel {
    companion object {
        fun create(
            assets: AssetManager,
            modelPath: String,
            options: Options
        ): CompiledModel

        fun create(
            modelFile: File,
            options: Options
        ): CompiledModel

        fun create(
            byteBuffer: ByteBuffer,
            options: Options
        ): CompiledModel
    }

    fun run(inputBuffer: ByteBuffer): Array<ByteBuffer>
    fun run(inputBuffers: Array<ByteBuffer>): Array<ByteBuffer>

    fun runAsync(inputBuffer: ByteBuffer): Future<Array<ByteBuffer>>

    fun getInputTensorInfo(index: Int): TensorInfo
    fun getOutputTensorInfo(index: Int): TensorInfo

    fun close()
}
```

**Usage Example**:

```kotlin
val model = CompiledModel.create(
    context.assets,
    "model.tflite",
    CompiledModel.Options(Accelerator.GPU)
)

val output = model.run(inputBuffer)
model.close()
```

### CompiledModel.Options

Configuration options for model creation.

```kotlin
data class Options(
    val accelerator: Accelerator = Accelerator.CPU,
    val numThreads: Int = 4,
    val allowFp16Precision: Boolean = true,
    val enableAsyncExecution: Boolean = false
)
```

**Parameters**:
- `accelerator`: Hardware accelerator to use (CPU, GPU, NPU)
- `numThreads`: Number of CPU threads (CPU accelerator only)
- `allowFp16Precision`: Allow FP16 precision for GPU
- `enableAsyncExecution`: Enable true async execution with sync fences

**Example**:

```kotlin
val options = CompiledModel.Options(
    accelerator = Accelerator.GPU,
    allowFp16Precision = true,
    enableAsyncExecution = true
)
```

### Accelerator

Enum for hardware acceleration options.

```kotlin
enum class Accelerator {
    CPU,
    GPU,
    NPU,
    NNAPI  // Neural Networks API
}
```

**Selection Guidelines**:
- **CPU**: Universal compatibility, good for complex operations
- **GPU**: Best for image processing (detection, segmentation, classification)
- **NPU**: Maximum efficiency on supported devices (Pixel, Samsung flagship)
- **NNAPI**: Android's unified ML acceleration API

**Device Support Check**:

```kotlin
fun getBestAccelerator(context: Context): Accelerator {
    return when {
        isNPUAvailable() -> Accelerator.NPU
        isGPUCompatible() -> Accelerator.GPU
        else -> Accelerator.CPU
    }
}

fun isGPUCompatible(): Boolean {
    val compatibilityList = CompatibilityList()
    return compatibilityList.isDelegateSupportedOnThisDevice
}

fun isNPUAvailable(): Boolean {
    // Check device model for NPU support
    val device = Build.MODEL.lowercase()
    return device.contains("pixel 6") ||
           device.contains("pixel 7") ||
           device.contains("pixel 8") ||
           device.contains("s22") ||
           device.contains("s23")
}
```

### TensorInfo

Information about input/output tensors.

```kotlin
data class TensorInfo(
    val shape: IntArray,
    val dataType: DataType,
    val name: String,
    val quantizationParams: QuantizationParams?
)

enum class DataType {
    FLOAT32,
    INT32,
    UINT8,
    INT8,
    INT64,
    STRING,
    BOOL,
    INT16,
    FLOAT16
}

data class QuantizationParams(
    val scale: Float,
    val zeroPoint: Int
)
```

**Example**:

```kotlin
val inputInfo = model.getInputTensorInfo(0)
println("Input shape: ${inputInfo.shape.contentToString()}")
println("Input type: ${inputInfo.dataType}")
println("Is quantized: ${inputInfo.quantizationParams != null}")
```

For complete API reference including LiteRT v1 APIs, threading, performance profiling, and migration guides, please refer to the full documentation.
