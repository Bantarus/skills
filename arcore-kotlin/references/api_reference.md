# ARCore API Reference

Complete API reference for ARCore Android SDK (version 1.51+) with Kotlin implementations.

## Core Classes

### Session

The main entry point to ARCore API, managing AR system state and session lifecycle.

**Constructor:**
```kotlin
Session(context: Context)
Session(context: Context, features: Set<Session.Feature>)
```

**Methods:**
```kotlin
// Lifecycle management
fun configure(config: Config)
fun resume()
fun pause()
fun close()

// Frame updates
fun update(): Frame
fun setCameraTextureName(textureId: Int)
fun setDisplayGeometry(rotation: Int, width: Int, height: Int)

// Anchor management
fun createAnchor(pose: Pose): Anchor
fun getAllAnchors(): Collection<Anchor>
fun getAllTrackables(filterType: Class<T>): Collection<T>

// Recording and playback
fun startRecording(recordingConfig: RecordingConfig)
fun stopRecording(): RecordingStatus
fun setPlaybackDatasetUri(datasetUri: Uri): PlaybackStatus

// Cloud anchors
fun hostCloudAnchorAsync(
    anchor: Anchor,
    ttlDays: Int,
    onSuccess: (String) -> Unit,
    onError: (CloudAnchorState) -> Unit
): Future<String>

fun resolveCloudAnchorAsync(
    cloudAnchorId: String,
    onSuccess: (Anchor) -> Unit,
    onError: (CloudAnchorState) -> Unit
): Future<Anchor>

// Feature support
fun isDepthModeSupported(mode: Config.DepthMode): Boolean
fun isGeospatialModeSupported(mode: Config.GeospatialMode): Boolean
fun getSupportedCameraConfigs(): List<CameraConfig>
fun getSupportedCameraConfigs(filter: CameraConfigFilter): List<CameraConfig>

// Properties
val config: Config
val earth: Earth?
val cameraConfig: CameraConfig
```

**Features (Session.Feature):**
- `FRONT_CAMERA` - Use front-facing camera for face tracking
- `SHARED_CAMERA` - Share camera with other apps

**Example:**
```kotlin
val session = Session(context)
val config = Config(session).apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
}
session.configure(config)
session.resume()
```

---

### Config

Configuration settings for ARCore session behavior.

**Constructor:**
```kotlin
Config(session: Session)
```

**Properties:**
```kotlin
// Plane detection
var planeFindingMode: Config.PlaneFindingMode

// Depth
var depthMode: Config.DepthMode

// Light estimation
var lightEstimationMode: Config.LightEstimationMode

// Instant placement
var instantPlacementMode: Config.InstantPlacementMode

// Augmented images
var augmentedImageDatabase: AugmentedImageDatabase?

// Augmented faces
var augmentedFaceMode: Config.AugmentedFaceMode

// Cloud anchors
var cloudAnchorMode: Config.CloudAnchorMode

// Geospatial
var geospatialMode: Config.GeospatialMode

// Focus mode
var focusMode: Config.FocusMode

// Update mode
var updateMode: Config.UpdateMode
```

**Enums:**

**PlaneFindingMode:**
- `DISABLED` - Plane detection disabled
- `HORIZONTAL` - Detect only horizontal planes
- `VERTICAL` - Detect only vertical planes
- `HORIZONTAL_AND_VERTICAL` - Detect both horizontal and vertical planes

**DepthMode:**
- `DISABLED` - Depth estimation disabled
- `AUTOMATIC` - Enable depth estimation (if supported)

**LightEstimationMode:**
- `DISABLED` - Light estimation disabled
- `AMBIENT_INTENSITY` - Simple ambient intensity estimation
- `ENVIRONMENTAL_HDR` - Full HDR lighting estimation with reflections

**InstantPlacementMode:**
- `DISABLED` - Instant placement disabled
- `LOCAL_Y_UP` - Enable instant placement with Y-axis pointing up

**AugmentedFaceMode:**
- `DISABLED` - Face tracking disabled
- `MESH3D` - Enable 3D face mesh tracking

**CloudAnchorMode:**
- `DISABLED` - Cloud anchors disabled
- `ENABLED` - Enable cloud anchor hosting and resolving

**GeospatialMode:**
- `DISABLED` - Geospatial API disabled
- `ENABLED` - Enable geospatial positioning

**FocusMode:**
- `AUTO` - Automatic camera focus
- `FIXED` - Fixed focus

**UpdateMode:**
- `BLOCKING` - Frame updates block until new data available
- `LATEST_CAMERA_IMAGE` - Return latest available frame immediately

**Example:**
```kotlin
val config = Config(session).apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    depthMode = Config.DepthMode.AUTOMATIC
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
    instantPlacementMode = Config.InstantPlacementMode.LOCAL_Y_UP
    focusMode = Config.FocusMode.AUTO
}
session.configure(config)
```

---

### Frame

Represents a single frame of AR tracking data.

**Methods:**
```kotlin
// Hit testing
fun hitTest(x: Float, y: Float): List<HitResult>
fun hitTest(ray: Ray): List<HitResult>
fun hitTestInstantPlacement(x: Float, y: Float, approximateDistance: Float): List<HitResult>

// Trackables
fun <T : Trackable> getUpdatedTrackables(filterType: Class<T>): Collection<T>

// Images
fun acquireCameraImage(): Image
fun acquireDepthImage16Bits(): Image

// Light estimation
val lightEstimate: LightEstimate

// Point cloud
fun acquirePointCloud(): PointCloud

// Properties
val camera: Camera
val timestamp: Long
val androidSensorPose: Pose?
```

**Example:**
```kotlin
fun onDrawFrame() {
    val frame = session.update()

    if (frame.camera.trackingState == TrackingState.TRACKING) {
        // Process frame
        val planes = frame.getUpdatedTrackables(Plane::class.java)
        val lightEstimate = frame.lightEstimate
    }
}
```

---

### Camera

Provides information about the physical camera and its tracking state.

**Properties:**
```kotlin
val trackingState: TrackingState
val trackingFailureReason: TrackingFailureReason
val pose: Pose
val displayOrientedPose: Pose
val textureIntrinsics: CameraIntrinsics
val imageIntrinsics: CameraIntrinsics
```

**Methods:**
```kotlin
fun getProjectionMatrix(dest: FloatArray, offset: Int, near: Float, far: Float)
fun getViewMatrix(dest: FloatArray, offset: Int)
```

**TrackingState:**
- `TRACKING` - Camera is tracking successfully
- `PAUSED` - Tracking is paused (insufficient features, motion, etc.)
- `STOPPED` - Tracking has stopped

**TrackingFailureReason:**
- `NONE` - No tracking failure
- `BAD_STATE` - ARCore in bad internal state
- `INSUFFICIENT_LIGHT` - Insufficient lighting
- `EXCESSIVE_MOTION` - Too much device motion
- `INSUFFICIENT_FEATURES` - Not enough visual features
- `CAMERA_UNAVAILABLE` - Camera unavailable

**Example:**
```kotlin
val camera = frame.camera
when (camera.trackingState) {
    TrackingState.TRACKING -> {
        val viewMatrix = FloatArray(16)
        val projectionMatrix = FloatArray(16)
        camera.getViewMatrix(viewMatrix, 0)
        camera.getProjectionMatrix(projectionMatrix, 0, 0.1f, 100f)
    }
    TrackingState.PAUSED -> {
        when (camera.trackingFailureReason) {
            TrackingFailureReason.INSUFFICIENT_LIGHT -> showMessage("Need more light")
            TrackingFailureReason.EXCESSIVE_MOTION -> showMessage("Move slower")
            TrackingFailureReason.INSUFFICIENT_FEATURES -> showMessage("Point at surfaces with more detail")
            else -> {}
        }
    }
    else -> {}
}
```

---

### Pose

Represents a position and orientation in 3D space.

**Constructor:**
```kotlin
Pose(translation: FloatArray, rotation: FloatArray)
Pose.makeTranslation(x: Float, y: Float, z: Float): Pose
Pose.makeRotation(qx: Float, qy: Float, qz: Float, qw: Float): Pose
Pose.IDENTITY: Pose
```

**Properties:**
```kotlin
val translation: FloatArray // [x, y, z] in meters
val rotationQuaternion: FloatArray // [qx, qy, qz, qw]
val xAxis: FloatArray // Unit vector in X direction
val yAxis: FloatArray // Unit vector in Y direction
val zAxis: FloatArray // Unit vector in Z direction
```

**Methods:**
```kotlin
fun toMatrix(dest: FloatArray, offset: Int)
fun inverse(): Pose
fun compose(other: Pose): Pose
fun extractTranslation(): Pose
fun extractRotation(): Pose
fun transformPoint(point: FloatArray): FloatArray
fun rotateVector(vector: FloatArray): FloatArray
```

**Example:**
```kotlin
val pose = anchor.pose
val translation = pose.translation // [x, y, z]
val rotation = pose.rotationQuaternion // [qx, qy, qz, qw]

val modelMatrix = FloatArray(16)
pose.toMatrix(modelMatrix, 0)

// Combine poses
val offsetPose = Pose.makeTranslation(0f, 0.5f, 0f)
val finalPose = pose.compose(offsetPose)
```

---

### Anchor

Maintains a fixed position and orientation in physical space.

**Properties:**
```kotlin
val pose: Pose
val trackingState: TrackingState
val cloudAnchorState: CloudAnchorState
val cloudAnchorId: String?
```

**Methods:**
```kotlin
fun detach()
```

**CloudAnchorState:**
- `NONE` - Not a cloud anchor
- `TASK_IN_PROGRESS` - Hosting/resolving in progress
- `SUCCESS` - Successfully hosted/resolved
- `ERROR_*` - Various error states

**Example:**
```kotlin
val anchor = hitResult.createAnchor()

fun updateAnchor(anchor: Anchor) {
    when (anchor.trackingState) {
        TrackingState.TRACKING -> {
            val modelMatrix = FloatArray(16)
            anchor.pose.toMatrix(modelMatrix, 0)
            renderObject(modelMatrix)
        }
        else -> {
            // Anchor not tracking
        }
    }
}

// Clean up
anchor.detach()
```

---

### Plane

Represents a detected planar surface in the environment.

**Properties:**
```kotlin
val centerPose: Pose
val extentX: Float // Half-width in meters
val extentZ: Float // Half-height in meters
val polygon: FloatBuffer // 2D polygon boundary
val type: Plane.Type
val trackingState: TrackingState
val subsumedBy: Plane?
```

**Methods:**
```kotlin
fun createAnchor(pose: Pose): Anchor
fun isPoseInPolygon(pose: Pose): Boolean
fun isPoseInExtents(pose: Pose): Boolean
```

**Type:**
- `HORIZONTAL_UPWARD_FACING` - Floor, table, ground
- `HORIZONTAL_DOWNWARD_FACING` - Ceiling
- `VERTICAL` - Wall

**Example:**
```kotlin
val planes = frame.getUpdatedTrackables(Plane::class.java)

for (plane in planes) {
    if (plane.trackingState == TrackingState.TRACKING && plane.subsumedBy == null) {
        when (plane.type) {
            Plane.Type.HORIZONTAL_UPWARD_FACING -> {
                val centerPose = plane.centerPose
                val width = plane.extentX * 2
                val height = plane.extentZ * 2

                // Check if pose is within plane
                if (plane.isPoseInPolygon(testPose)) {
                    val anchor = plane.createAnchor(testPose)
                }
            }
            else -> {}
        }
    }
}
```

---

### HitResult

Result of a ray cast against trackables in the scene.

**Properties:**
```kotlin
val hitPose: Pose
val distance: Float
val trackable: Trackable?
```

**Methods:**
```kotlin
fun createAnchor(): Anchor
```

**Example:**
```kotlin
val hitResults = frame.hitTest(screenX, screenY)

for (hit in hitResults) {
    val trackable = hit.trackable

    if (trackable is Plane && trackable.isPoseInPolygon(hit.hitPose)) {
        val anchor = hit.createAnchor()
        val distance = hit.distance // Distance from camera in meters
        break
    }
}
```

---

### AugmentedImage

Represents a detected 2D image in the environment.

**Properties:**
```kotlin
val name: String
val index: Int
val centerPose: Pose
val extentX: Float // Physical width in meters
val extentZ: Float // Physical height in meters
val trackingState: TrackingState
val trackingMethod: TrackingMethod
```

**Methods:**
```kotlin
fun createAnchor(pose: Pose): Anchor
```

**TrackingMethod:**
- `FULL_TRACKING` - Image fully tracked with accurate pose
- `LAST_KNOWN_POSE` - Using last known pose (image not currently visible)
- `NOT_TRACKING` - Not tracking

**Example:**
```kotlin
val images = frame.getUpdatedTrackables(AugmentedImage::class.java)

for (image in images) {
    when (image.trackingState) {
        TrackingState.TRACKING -> {
            if (image.trackingMethod == AugmentedImage.TrackingMethod.FULL_TRACKING) {
                val anchor = image.createAnchor(image.centerPose)
                val physicalWidth = image.extentX * 2
                val physicalHeight = image.extentZ * 2
            }
        }
        else -> {}
    }
}
```

---

### AugmentedImageDatabase

Database of images to detect in the environment.

**Constructor:**
```kotlin
AugmentedImageDatabase(session: Session)
AugmentedImageDatabase.deserialize(session: Session, inputStream: InputStream): AugmentedImageDatabase
```

**Methods:**
```kotlin
fun addImage(name: String, bitmap: Bitmap): Int
fun addImage(name: String, bitmap: Bitmap, widthInMeters: Float): Int
fun serialize(): ByteBuffer
```

**Example:**
```kotlin
val database = AugmentedImageDatabase(session)

// Add image from bitmap
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.target_image)
val imageIndex = database.addImage("product_logo", bitmap, 0.15f) // 15cm width

// Save database
val outputStream = FileOutputStream("image_db.imgdb")
outputStream.write(database.serialize().array())

// Load database
val inputStream = assets.open("image_db.imgdb")
val loadedDatabase = AugmentedImageDatabase.deserialize(session, inputStream)

// Configure session
config.augmentedImageDatabase = database
session.configure(config)
```

---

### AugmentedFace

Represents a detected and tracked human face.

**Properties:**
```kotlin
val centerPose: Pose
val meshVertices: FloatBuffer
val meshNormals: FloatBuffer
val meshTextureCoordinates: FloatBuffer
val meshTriangleIndices: ShortBuffer
val trackingState: TrackingState
```

**Methods:**
```kotlin
fun getRegionPose(regionType: RegionType): Pose
fun createAnchor(pose: Pose): Anchor
```

**RegionType:**
- `NOSE_TIP`
- `FOREHEAD_LEFT`
- `FOREHEAD_RIGHT`

**Example:**
```kotlin
val faces = frame.getUpdatedTrackables(AugmentedFace::class.java)

for (face in faces) {
    if (face.trackingState == TrackingState.TRACKING) {
        // Get face mesh
        val vertices = face.meshVertices
        val normals = face.meshNormals
        val uvs = face.meshTextureCoordinates
        val indices = face.meshTriangleIndices

        // Get specific face regions
        val noseTipPose = face.getRegionPose(AugmentedFace.RegionType.NOSE_TIP)
        val anchor = face.createAnchor(noseTipPose)

        renderFaceMesh(vertices, normals, uvs, indices)
    }
}
```

---

### LightEstimate

Environmental lighting information.

**Properties:**
```kotlin
val state: State
val pixelIntensity: Float
val colorCorrection: FloatArray // RGBA

// Environmental HDR properties
val environmentalHdrMainLightDirection: FloatArray
val environmentalHdrMainLightIntensity: FloatArray
val environmentalHdrAmbientSphericalHarmonics: FloatArray
```

**Methods:**
```kotlin
fun acquireEnvironmentalHdrCubeMap(): Image
```

**State:**
- `VALID` - Light estimate is valid
- `NOT_VALID` - Light estimate not available

**Example:**
```kotlin
val lightEstimate = frame.lightEstimate

when (lightEstimate.state) {
    LightEstimate.State.VALID -> {
        // Simple lighting
        val intensity = lightEstimate.pixelIntensity
        val colorCorrection = lightEstimate.colorCorrection

        // Environmental HDR
        val mainLightDir = lightEstimate.environmentalHdrMainLightDirection
        val mainLightIntensity = lightEstimate.environmentalHdrMainLightIntensity
        val sphericalHarmonics = lightEstimate.environmentalHdrAmbientSphericalHarmonics

        // Cubemap for reflections
        val cubemap = lightEstimate.acquireEnvironmentalHdrCubeMap()
        cubemap.close()

        applyLighting(intensity, colorCorrection, mainLightDir, mainLightIntensity)
    }
    else -> {
        // Use default lighting
    }
}
```

---

### Earth

Provides geospatial information and capabilities.

**Properties:**
```kotlin
val trackingState: TrackingState
val earthState: EarthState
val cameraGeospatialPose: GeospatialPose
```

**Methods:**
```kotlin
fun createAnchor(
    latitude: Double,
    longitude: Double,
    altitude: Double,
    qx: Float,
    qy: Float,
    qz: Float,
    qw: Float
): Anchor

fun resolveAnchorOnTerrain(
    latitude: Double,
    longitude: Double,
    altitudeAboveTerrain: Float,
    qx: Float,
    qy: Float,
    qz: Float,
    qw: Float
): Future<ResolveAnchorOnTerrainResult>
```

**EarthState:**
- `ENABLED` - Geospatial tracking enabled
- `ERROR_*` - Various error states

**Example:**
```kotlin
val earth = session.earth

if (earth?.trackingState == TrackingState.TRACKING) {
    val geoPose = earth.cameraGeospatialPose

    // Create anchor at specific location
    val anchor = earth.createAnchor(
        latitude = 37.7749,
        longitude = -122.4194,
        altitude = 10.0,
        qx = 0f, qy = 0f, qz = 0f, qw = 1f
    )

    // Anchor on terrain
    val terrainAnchorFuture = earth.resolveAnchorOnTerrain(
        latitude = 37.7749,
        longitude = -122.4194,
        altitudeAboveTerrain = 2.0f,
        qx = 0f, qy = 0f, qz = 0f, qw = 1f
    )
}
```

---

### GeospatialPose

Device position in geographic coordinates.

**Properties:**
```kotlin
val latitude: Double // Degrees
val longitude: Double // Degrees
val altitude: Double // Meters (WGS84 ellipsoid)
val heading: Double // Degrees (0-360, clockwise from north)
val horizontalAccuracy: Double // Meters
val verticalAccuracy: Double // Meters
val headingAccuracy: Double // Degrees
```

**Example:**
```kotlin
val geoPose = earth.cameraGeospatialPose

val lat = geoPose.latitude
val lon = geoPose.longitude
val alt = geoPose.altitude
val heading = geoPose.heading

// Check accuracy
if (geoPose.horizontalAccuracy < 5.0 && geoPose.headingAccuracy < 15.0) {
    // Good accuracy for placing anchors
    val anchor = earth.createAnchor(lat, lon, alt, 0f, 0f, 0f, 1f)
} else {
    // Accuracy too low
    showMessage("Move to improve accuracy")
}
```

---

### PointCloud

Collection of 3D feature points detected in the environment.

**Properties:**
```kotlin
val ids: IntBuffer
val points: FloatBuffer // x, y, z coordinates
val timestamp: Long
```

**Methods:**
```kotlin
fun release()
```

**Example:**
```kotlin
val pointCloud = frame.acquirePointCloud()

val points = pointCloud.points
val ids = pointCloud.ids

// Process points (format: x, y, z, x, y, z, ...)
points.rewind()
while (points.hasRemaining()) {
    val x = points.get()
    val y = points.get()
    val z = points.get()
    // Render point
}

pointCloud.release()
```

---

### CameraConfig

Configuration for camera resolution and capabilities.

**Properties:**
```kotlin
val imageSize: Size
val textureSize: Size
val fpsRange: IntRange
val depthSensorUsage: DepthSensorUsage
```

**Example:**
```kotlin
val filter = CameraConfigFilter(session).apply {
    setTargetFps(EnumSet.of(CameraConfig.TargetFps.TARGET_FPS_60))
    setDepthSensorUsage(EnumSet.of(CameraConfig.DepthSensorUsage.REQUIRE_AND_USE))
}

val configs = session.getSupportedCameraConfigs(filter)

// Select config with highest resolution
val selectedConfig = configs.maxByOrNull { it.imageSize.width * it.imageSize.height }
session.cameraConfig = selectedConfig
```

---

### CameraIntrinsics

Physical characteristics of the camera.

**Properties:**
```kotlin
val focalLength: FloatArray // [fx, fy] in pixels
val principalPoint: FloatArray // [cx, cy] in pixels
val imageDimensions: IntArray // [width, height]
```

**Methods:**
```kotlin
fun unproject(point2d: FloatArray, depth: Float): FloatArray
```

**Example:**
```kotlin
val intrinsics = frame.camera.textureIntrinsics

val focalLength = intrinsics.focalLength // [fx, fy]
val principalPoint = intrinsics.principalPoint // [cx, cy]
val dimensions = intrinsics.imageDimensions // [width, height]

// Convert 2D screen point to 3D ray
val point3d = intrinsics.unproject(floatArrayOf(screenX, screenY), 1.0f)
```

---

## Exception Handling

ARCore throws specific exceptions for various error conditions:

**UnavailableException:**
- `UnavailableArcoreNotInstalledException` - ARCore not installed
- `UnavailableApkTooOldException` - ARCore version too old
- `UnavailableSdkTooOldException` - App SDK version too old
- `UnavailableDeviceNotCompatibleException` - Device not compatible
- `UnavailableUserDeclinedInstallationException` - User declined installation

**Other Exceptions:**
- `NotYetAvailableException` - Resource not yet available (e.g., depth image)
- `DeadlineExceededException` - Operation exceeded timeout
- `ResourceExhaustedException` - Too many resources allocated
- `FatalException` - Unrecoverable error

**Example:**
```kotlin
try {
    session = Session(context)
} catch (e: UnavailableArcoreNotInstalledException) {
    // Prompt user to install ARCore
} catch (e: UnavailableDeviceNotCompatibleException) {
    // Device doesn't support ARCore
} catch (e: UnavailableApkTooOldException) {
    // ARCore needs update
} catch (e: Exception) {
    // Other error
}

// Resource availability
try {
    val depthImage = frame.acquireDepthImage16Bits()
    depthImage.close()
} catch (e: NotYetAvailableException) {
    // Depth not ready yet
}
```

---

## Utility Classes

### Ray

Represents a ray in 3D space.

```kotlin
data class Ray(
    val origin: FloatArray,
    val direction: FloatArray
)
```

### Size

Represents 2D dimensions.

```kotlin
data class Size(
    val width: Int,
    val height: Int
)
```

---

## Best Practices

1. **Always check tracking state** before using poses or creating anchors
2. **Close/release resources** (Images, PointClouds) when done
3. **Detach anchors** when no longer needed to free resources
4. **Limit active anchors** to ~20 for optimal performance
5. **Handle exceptions** during session creation and frame updates
6. **Monitor tracking failure reasons** to provide user guidance
7. **Use appropriate config modes** based on app requirements
8. **Test on physical devices** - emulators have limited ARCore support
