---
name: arcore-kotlin
description: Comprehensive skill for implementing ARCore in Android applications using Kotlin. This skill should be used when developing augmented reality applications for Android, implementing AR features such as motion tracking, plane detection, anchors, augmented images, depth sensing, geospatial positioning, or any ARCore-related functionality. Use this when working with 3D AR experiences, environmental understanding, or location-based AR on Android devices.
---

# ARCore for Android (Kotlin)

## Overview

This skill provides comprehensive guidance for implementing Google ARCore in Android applications using Kotlin. ARCore is Google's platform for building augmented reality experiences on Android devices. It uses device cameras, sensors, and processors to track the device's position and orientation in the real world, detect surfaces, estimate lighting conditions, and enable placing virtual objects that appear anchored to the physical environment.

**Latest Stable Version:** ARCore 1.51.252580493 (supports Android 15.0, targetSdkVersion 36)

**Key Capabilities:**
- Motion tracking (6DoF tracking)
- Environmental understanding (plane detection, depth)
- Light estimation
- Anchors (local and cloud)
- Augmented Images
- Geospatial API
- Camera configuration
- Scene understanding

## Quick Start

### Prerequisites

Before implementing ARCore features, ensure:

1. **Android Studio:** Version 3.1 or higher
2. **SDK Platform:** Android SDK Platform version 7.0 (API level 24) or higher
3. **ARCore APK:** Users must have ARCore installed on their device
4. **Device Compatibility:** Check device support at https://developers.google.com/ar/devices

### Project Setup

To set up ARCore in an Android project:

1. **Add ARCore dependency** to `build.gradle.kts` (Module):
```kotlin
dependencies {
    implementation("com.google.ar:core:1.51.0")

    // Optional: Jetpack XR integration
    implementation("androidx.xr.arcore:arcore:1.0.0-alpha03")
}
```

2. **Update AndroidManifest.xml:**
```xml
<manifest>
    <!-- ARCore requires camera permission -->
    <uses-permission android:name="android.permission.CAMERA" />

    <!-- Limit app to ARCore supported devices (optional) -->
    <uses-feature android:name="android.hardware.camera.ar" android:required="true" />

    <application>
        <!-- Indicates this app requires ARCore ("AR Required" apps) -->
        <!-- For "AR Optional" apps, use android:value="optional" -->
        <meta-data
            android:name="com.google.ar.core"
            android:value="required" />
    </application>
</manifest>
```

3. **Verify ARCore Availability:**
```kotlin
import com.google.ar.core.ArCoreApk
import com.google.ar.core.exceptions.UnavailableException

fun checkARCoreAvailability(activity: Activity) {
    val availability = ArCoreApk.getInstance().checkAvailability(activity)

    when (availability) {
        ArCoreApk.Availability.SUPPORTED_INSTALLED -> {
            // ARCore is installed and ready
        }
        ArCoreApk.Availability.SUPPORTED_APK_TOO_OLD,
        ArCoreApk.Availability.SUPPORTED_NOT_INSTALLED -> {
            // Request ARCore installation
            try {
                val installStatus = ArCoreApk.getInstance()
                    .requestInstall(activity, true)
                when (installStatus) {
                    ArCoreApk.InstallStatus.INSTALLED -> {
                        // ARCore installed successfully
                    }
                    ArCoreApk.InstallStatus.INSTALL_REQUESTED -> {
                        // Installation in progress
                    }
                }
            } catch (e: UnavailableException) {
                // Handle installation failure
            }
        }
        else -> {
            // ARCore is not supported on this device
        }
    }
}
```

### Session Initialization

To create and configure an ARCore session:

```kotlin
import com.google.ar.core.Session
import com.google.ar.core.Config

class ARActivity : AppCompatActivity() {
    private lateinit var session: Session

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Create ARCore session
        session = Session(this)

        // Configure session
        val config = Config(session).apply {
            // Set plane finding mode
            planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL

            // Enable depth mode if supported
            depthMode = Config.DepthMode.AUTOMATIC

            // Enable light estimation
            lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR

            // Enable instant placement
            instantPlacementMode = Config.InstantPlacementMode.LOCAL_Y_UP
        }

        session.configure(config)
    }

    override fun onResume() {
        super.onResume()
        session.resume()
    }

    override fun onPause() {
        super.onPause()
        session.pause()
    }

    override fun onDestroy() {
        super.onDestroy()
        session.close()
    }
}
```

### Frame Update Loop

To process AR frames and update the scene:

```kotlin
import com.google.ar.core.Frame

fun updateARFrame() {
    // Update session and get current frame
    val frame = session.update()

    // Get camera pose
    val cameraPose = frame.camera.pose

    // Process trackables (planes, points, etc.)
    processTrackables(frame)

    // Render AR content
    renderScene(frame)
}
```

For detailed session configuration options, see `references/session_config.md`.

## Core Features

### 1. Motion Tracking

ARCore tracks the device's position and orientation in 3D space using 6DoF (six degrees of freedom) tracking.

**Camera Tracking States:**
```kotlin
import com.google.ar.core.TrackingState

fun checkCameraTracking(frame: Frame) {
    when (frame.camera.trackingState) {
        TrackingState.TRACKING -> {
            // Camera is tracking successfully
            // Safe to place and update AR objects
        }
        TrackingState.PAUSED -> {
            // Tracking paused (poor lighting, feature points, etc.)
            // Display user guidance
        }
        TrackingState.STOPPED -> {
            // Tracking stopped
            // ARCore cannot determine device position
        }
    }
}
```

**Getting Camera Pose:**
```kotlin
fun getCameraPoseInfo(frame: Frame) {
    val pose = frame.camera.pose

    // Translation (position in meters)
    val translation = pose.translation // FloatArray [x, y, z]

    // Rotation (quaternion)
    val rotation = pose.rotationQuaternion // FloatArray [qx, qy, qz, qw]

    // Transform matrix (4x4)
    val matrix = FloatArray(16)
    pose.toMatrix(matrix, 0)
}
```

### 2. Environmental Understanding

ARCore detects horizontal and vertical surfaces (planes) in the environment.

**Plane Detection:**
```kotlin
import com.google.ar.core.Plane
import com.google.ar.core.TrackingState

fun detectPlanes(frame: Frame) {
    // Get all trackable planes
    val planes = frame.getUpdatedTrackables(Plane::class.java)

    for (plane in planes) {
        if (plane.trackingState == TrackingState.TRACKING) {
            // Plane type
            when (plane.type) {
                Plane.Type.HORIZONTAL_UPWARD_FACING -> {
                    // Floor, table, etc.
                }
                Plane.Type.HORIZONTAL_DOWNWARD_FACING -> {
                    // Ceiling
                }
                Plane.Type.VERTICAL -> {
                    // Wall
                }
            }

            // Plane polygon (boundary)
            val polygon = plane.polygon

            // Plane center pose
            val centerPose = plane.centerPose

            // Plane extent (width and length)
            val extentX = plane.extentX
            val extentZ = plane.extentZ

            // Check if plane is subsumed by another
            if (plane.subsumedBy == null) {
                // Plane is active
            }
        }
    }
}
```

**Hit Testing:**
```kotlin
import com.google.ar.core.HitResult

fun performHitTest(frame: Frame, screenX: Float, screenY: Float) {
    // Hit test against planes and feature points
    val hitResults = frame.hitTest(screenX, screenY)

    for (hit in hitResults) {
        val trackable = hit.trackable

        if (trackable is Plane && trackable.isPoseInPolygon(hit.hitPose)) {
            // Hit a plane within its polygon boundary
            val hitPose = hit.hitPose

            // Create anchor at hit location
            val anchor = hit.createAnchor()
            break
        }
    }
}
```

### 3. Anchors

Anchors maintain the position and orientation of virtual objects relative to the real world.

**Creating Anchors:**
```kotlin
import com.google.ar.core.Anchor

// Create anchor from a pose
fun createAnchorAtPose(session: Session, pose: Pose): Anchor {
    return session.createAnchor(pose)
}

// Create anchor from hit test result
fun createAnchorFromHit(hitResult: HitResult): Anchor {
    return hitResult.createAnchor()
}

// Create anchor on a plane
fun createAnchorOnPlane(plane: Plane, pose: Pose): Anchor {
    return plane.createAnchor(pose)
}
```

**Managing Anchors:**
```kotlin
fun manageAnchor(anchor: Anchor) {
    // Check anchor tracking state
    when (anchor.trackingState) {
        TrackingState.TRACKING -> {
            // Anchor is being tracked
            val anchorPose = anchor.pose
            // Update virtual object position
        }
        TrackingState.PAUSED -> {
            // Anchor tracking paused
        }
        TrackingState.STOPPED -> {
            // Anchor tracking stopped
        }
    }

    // Detach anchor when no longer needed
    anchor.detach()
}

// Get all anchors
fun getAllAnchors(session: Session): Collection<Anchor> {
    return session.getAllAnchors()
}
```

### 4. Augmented Images

ARCore can detect and track 2D images in the environment.

**Setup:**
```kotlin
import com.google.ar.core.AugmentedImageDatabase
import android.graphics.BitmapFactory

fun setupAugmentedImages(session: Session, config: Config) {
    // Create image database
    val imageDatabase = AugmentedImageDatabase(session)

    // Add images from bitmap
    val bitmap = BitmapFactory.decodeResource(resources, R.drawable.target_image)
    val imageIndex = imageDatabase.addImage("image_name", bitmap, 0.2f) // 0.2m physical width

    // Or load from database file
    // val inputStream = assets.open("image_database.imgdb")
    // val imageDatabase = AugmentedImageDatabase.deserialize(session, inputStream)

    // Configure session with database
    config.augmentedImageDatabase = imageDatabase
    session.configure(config)
}
```

**Tracking Images:**
```kotlin
import com.google.ar.core.AugmentedImage

fun trackAugmentedImages(frame: Frame) {
    val augmentedImages = frame.getUpdatedTrackables(AugmentedImage::class.java)

    for (image in augmentedImages) {
        when (image.trackingState) {
            TrackingState.TRACKING -> {
                // Image is being tracked
                val imageName = image.name
                val imageIndex = image.index
                val centerPose = image.centerPose
                val extentX = image.extentX // Physical width
                val extentZ = image.extentZ // Physical height

                // Check tracking method
                when (image.trackingMethod) {
                    AugmentedImage.TrackingMethod.FULL_TRACKING -> {
                        // Image is fully tracked with pose
                    }
                    AugmentedImage.TrackingMethod.LAST_KNOWN_POSE -> {
                        // Using last known pose
                    }
                    AugmentedImage.TrackingMethod.NOT_TRACKING -> {
                        // Not currently tracking
                    }
                }

                // Create anchor on image
                val anchor = image.createAnchor(centerPose)
            }
            else -> {
                // Image not tracking
            }
        }
    }
}
```

### 5. Light Estimation

ARCore estimates environmental lighting conditions for realistic rendering.

**Environmental HDR Mode:**
```kotlin
import com.google.ar.core.LightEstimate

fun getLightEstimation(frame: Frame) {
    val lightEstimate = frame.lightEstimate

    when (lightEstimate.state) {
        LightEstimate.State.VALID -> {
            // Environmental HDR lighting
            val colorCorrection = lightEstimate.colorCorrection // RGBA
            val pixelIntensity = lightEstimate.pixelIntensity

            // Get environmental HDR cubemap
            val cubeMap = lightEstimate.acquireEnvironmentalHdrCubeMap()

            // Main directional light
            val mainLightDirection = lightEstimate.environmentalHdrMainLightDirection
            val mainLightIntensity = lightEstimate.environmentalHdrMainLightIntensity

            // Ambient spherical harmonics
            val sphericalHarmonics = lightEstimate.environmentalHdrAmbientSphericalHarmonics
        }
        LightEstimate.State.NOT_VALID -> {
            // Light estimation not available
        }
    }
}
```

### 6. Depth API

ARCore provides depth information for occlusion and physics simulation.

**Enable Depth:**
```kotlin
fun enableDepth(session: Session) {
    val config = session.config

    // Check if depth is supported
    if (session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)) {
        config.depthMode = Config.DepthMode.AUTOMATIC
        session.configure(config)
    }
}
```

**Access Depth Data:**
```kotlin
import com.google.ar.core.exceptions.NotYetAvailableException

fun getDepthImage(frame: Frame) {
    try {
        val depthImage = frame.acquireDepthImage16Bits()

        val width = depthImage.width
        val height = depthImage.height

        // Access depth buffer
        val depthBuffer = depthImage.planes[0].buffer

        // Get depth at specific pixel (x, y)
        // Depth values are in millimeters

        depthImage.close()
    } catch (e: NotYetAvailableException) {
        // Depth data not yet available
    }
}
```

### 7. Geospatial API

ARCore's Geospatial API enables world-scale AR experiences using GPS, compass, and visual positioning.

**Enable Geospatial Mode:**
```kotlin
import com.google.ar.core.GeospatialMode

fun enableGeospatial(session: Session) {
    val config = session.config
    config.geospatialMode = Config.GeospatialMode.ENABLED
    session.configure(config)
}
```

**Get Geospatial Pose:**
```kotlin
import com.google.ar.core.Earth

fun getGeospatialPose(frame: Frame) {
    val earth = session.earth

    if (earth?.trackingState == TrackingState.TRACKING) {
        val cameraGeospatialPose = earth.cameraGeospatialPose

        val latitude = cameraGeospatialPose.latitude
        val longitude = cameraGeospatialPose.longitude
        val altitude = cameraGeospatialPose.altitude // Meters (WGS84)
        val heading = cameraGeospatialPose.heading // Degrees (0-360)

        // Positioning accuracy
        val horizontalAccuracy = cameraGeospatialPose.horizontalAccuracy
        val verticalAccuracy = cameraGeospatialPose.verticalAccuracy
        val headingAccuracy = cameraGeospatialPose.headingAccuracy
    }
}
```

**Create Geospatial Anchors:**
```kotlin
fun createGeospatialAnchor(
    earth: Earth,
    latitude: Double,
    longitude: Double,
    altitude: Double,
    heading: Float
): Anchor {
    return earth.createAnchor(latitude, longitude, altitude, 0f, 0f, 0f, heading)
}
```

### 8. Camera Configuration

Configure camera resolution and focus mode.

**Camera Config:**
```kotlin
import com.google.ar.core.CameraConfigFilter
import com.google.ar.core.CameraConfig

fun configureCameraResolution(session: Session) {
    val filter = CameraConfigFilter(session).apply {
        // Target FPS
        setTargetFps(EnumSet.of(CameraConfig.TargetFps.TARGET_FPS_60))

        // Depth sensor usage
        setDepthSensorUsage(EnumSet.of(CameraConfig.DepthSensorUsage.REQUIRE_AND_USE))
    }

    val cameraConfigs = session.getSupportedCameraConfigs(filter)

    if (cameraConfigs.isNotEmpty()) {
        session.cameraConfig = cameraConfigs[0]
    }
}

fun getCameraIntrinsics(frame: Frame) {
    val camera = frame.camera
    val intrinsics = camera.textureIntrinsics

    val focalLength = intrinsics.focalLength // [fx, fy]
    val principalPoint = intrinsics.principalPoint // [cx, cy]
    val imageDimensions = intrinsics.imageDimensions // [width, height]
}
```

### 9. Recording and Playback

Record AR sessions for testing and playback.

**Recording:**
```kotlin
import com.google.ar.core.RecordingConfig
import java.io.File

fun startRecording(session: Session) {
    val file = File(filesDir, "ar_session.mp4")
    val recordingConfig = RecordingConfig(session)
        .setMp4DatasetFilePath(file.absolutePath)
        .setAutoStopOnPause(true)

    session.startRecording(recordingConfig)
}

fun stopRecording(session: Session) {
    session.stopRecording()
}
```

**Playback:**
```kotlin
fun playbackRecording(context: Context, filePath: String) {
    val session = Session(context, EnumSet.of(Session.Feature.FRONT_CAMERA))
    session.setPlaybackDatasetUri(Uri.parse(filePath))
    session.resume()
}
```

### 10. Cloud Anchors

Share AR experiences across devices using Cloud Anchors.

**Host Cloud Anchor:**
```kotlin
fun hostCloudAnchor(anchor: Anchor) {
    val future = session.hostCloudAnchorAsync(
        anchor,
        300, // TTL in days
        { cloudAnchorId ->
            // Cloud anchor hosted successfully
            // Share cloudAnchorId with other users
        },
        { error ->
            // Handle hosting error
        }
    )
}
```

**Resolve Cloud Anchor:**
```kotlin
fun resolveCloudAnchor(cloudAnchorId: String) {
    session.resolveCloudAnchorAsync(
        cloudAnchorId,
        { anchor ->
            // Cloud anchor resolved successfully
            // Use anchor to place shared content
        },
        { error ->
            // Handle resolution error
        }
    )
}
```

## Common Use Cases

### Placing Virtual Objects

```kotlin
fun placeObject(frame: Frame, screenX: Float, screenY: Float) {
    val hitResults = frame.hitTest(screenX, screenY)

    for (hit in hitResults) {
        val trackable = hit.trackable

        if (trackable is Plane && trackable.isPoseInPolygon(hit.hitPose)) {
            // Create anchor
            val anchor = hit.createAnchor()

            // Get pose for rendering
            val pose = anchor.pose

            // Transform to model matrix
            val modelMatrix = FloatArray(16)
            pose.toMatrix(modelMatrix, 0)

            // Render 3D model at anchor position
            break
        }
    }
}
```

### Face Tracking (Front Camera)

```kotlin
import com.google.ar.core.AugmentedFace

fun setupFaceTracking(context: Context) {
    val session = Session(context, EnumSet.of(Session.Feature.FRONT_CAMERA))

    val config = Config(session).apply {
        augmentedFaceMode = Config.AugmentedFaceMode.MESH3D
    }
    session.configure(config)
}

fun trackFaces(frame: Frame) {
    val faces = frame.getUpdatedTrackables(AugmentedFace::class.java)

    for (face in faces) {
        if (face.trackingState == TrackingState.TRACKING) {
            // Face center pose
            val centerPose = face.centerPose

            // Face mesh vertices
            val vertices = face.meshVertices
            val normals = face.meshNormals
            val uvs = face.meshTextureCoordinates
            val indices = face.meshTriangleIndices

            // Face regions
            val noseTipPose = face.getRegionPose(AugmentedFace.RegionType.NOSE_TIP)
            val foreheadLeftPose = face.getRegionPose(AugmentedFace.RegionType.FOREHEAD_LEFT)
        }
    }
}
```

### Instant Placement

For quick object placement without waiting for plane detection:

```kotlin
fun enableInstantPlacement(config: Config) {
    config.instantPlacementMode = Config.InstantPlacementMode.LOCAL_Y_UP
}

fun instantPlace(frame: Frame, screenX: Float, screenY: Float) {
    val hitResults = frame.hitTestInstantPlacement(screenX, screenY, 1.0f) // 1.0m estimated distance

    for (hit in hitResults) {
        val trackable = hit.trackable as? InstantPlacementPoint

        if (trackable?.trackingMethod == InstantPlacementPoint.TrackingMethod.SCREENSPACE_WITH_APPROXIMATE_DISTANCE) {
            val anchor = hit.createAnchor()
            // Object will adjust position as ARCore learns more about the environment
        }
    }
}
```

## Resources

For comprehensive API documentation, configuration details, and code examples, see the reference files:

### references/api_reference.md
Complete ARCore API reference covering all classes, methods, and properties. Read this file when implementing specific ARCore features or troubleshooting API usage.

### references/session_config.md
Detailed guide to ARCore session configuration options, including all Config properties, feature flags, and mode settings. Reference this when setting up or modifying session behavior.

### references/examples.md
Common implementation patterns, complete code examples, and best practices for typical ARCore scenarios. Use this for end-to-end implementation guidance.

## Best Practices

1. **Check Device Support:** Always verify ARCore availability before creating a session
2. **Handle Camera Permissions:** Request CAMERA permission at runtime for Android 6.0+
3. **Manage Session Lifecycle:** Properly pause/resume session with activity lifecycle
4. **Monitor Tracking State:** Check camera and trackable tracking states before updating AR content
5. **Resource Management:** Close/detach anchors and trackables when no longer needed
6. **User Guidance:** Provide visual feedback when tracking is degraded
7. **Performance:** Limit number of active anchors and trackables for optimal performance
8. **Testing:** Test on physical devices (ARCore doesn't work well in emulators)
9. **Lighting:** Guide users to well-lit environments for better tracking
10. **Surface Detection:** Give users time to scan environment for plane detection

## Troubleshooting

**Session creation fails:**
- Verify ARCore APK is installed and up-to-date
- Check device is ARCore compatible
- Ensure camera permissions are granted

**Poor tracking quality:**
- Improve lighting conditions
- Scan environment with more texture/features
- Avoid reflective or transparent surfaces
- Move device slowly and steadily

**Planes not detected:**
- Enable appropriate plane finding mode (horizontal/vertical)
- Scan surfaces at different angles
- Ensure sufficient lighting and texture
- Wait for tracking to stabilize

**Anchors drifting:**
- Ensure camera tracking state is TRACKING
- Avoid rapid device movement
- Use feature-rich environments
- Consider Cloud Anchors for persistent positioning

## Additional Resources

- **Official Documentation:** https://developers.google.com/ar/develop
- **API Reference:** https://developers.google.com/ar/reference
- **GitHub Repository:** https://github.com/google-ar/arcore-android-sdk
- **Supported Devices:** https://developers.google.com/ar/devices
- **Community:** Stack Overflow tag `arcore`
