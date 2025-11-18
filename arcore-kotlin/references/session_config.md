# ARCore Session Configuration Guide

Comprehensive guide to configuring ARCore sessions for optimal performance and feature support.

## Overview

ARCore session configuration controls all AR features, tracking modes, and performance characteristics. Proper configuration is essential for creating effective AR experiences.

## Configuration Workflow

```kotlin
// 1. Create session
val session = Session(context)

// 2. Get current config or create new one
val config = session.config // or Config(session)

// 3. Configure features
config.apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    depthMode = Config.DepthMode.AUTOMATIC
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
}

// 4. Apply configuration
session.configure(config)
```

## Configuration Properties

### Plane Detection (planeFindingMode)

Controls which types of surfaces ARCore detects.

**Options:**
- `DISABLED` - No plane detection (improves performance)
- `HORIZONTAL` - Detect only horizontal planes (floors, tables)
- `VERTICAL` - Detect only vertical planes (walls)
- `HORIZONTAL_AND_VERTICAL` - Detect both types

**Usage:**
```kotlin
config.planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
```

**When to use each mode:**
- **HORIZONTAL**: Floor-based AR (furniture placement, games)
- **VERTICAL**: Wall-mounted AR (art, posters, UI elements)
- **HORIZONTAL_AND_VERTICAL**: Full environment scanning
- **DISABLED**: When using instant placement or image tracking only

**Performance impact:** HORIZONTAL_AND_VERTICAL uses more CPU than single mode.

---

### Depth Mode (depthMode)

Enables depth estimation for occlusion and physics.

**Options:**
- `DISABLED` - No depth estimation
- `AUTOMATIC` - Enable if device supports (recommended)

**Usage:**
```kotlin
// Check support before enabling
if (session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)) {
    config.depthMode = Config.DepthMode.AUTOMATIC
}
```

**Benefits:**
- Realistic occlusion (AR objects hide behind real objects)
- Physics simulation
- Better spatial understanding

**Requirements:**
- Depth sensor (ToF) or software depth estimation
- Android 7.0+
- Not all devices support depth

**Performance impact:** Moderate CPU/GPU usage increase.

---

### Light Estimation (lightEstimationMode)

Controls environmental lighting analysis for realistic rendering.

**Options:**
- `DISABLED` - No light estimation
- `AMBIENT_INTENSITY` - Simple intensity and color
- `ENVIRONMENTAL_HDR` - Full HDR with directional light, reflections, and shadows

**Usage:**
```kotlin
config.lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
```

**Comparison:**

| Mode | Intensity | Color | Directional Light | Reflections | Shadows |
|------|-----------|-------|-------------------|-------------|---------|
| DISABLED | L | L | L | L | L |
| AMBIENT_INTENSITY |  |  | L | L | L |
| ENVIRONMENTAL_HDR |  |  |  |  |  |

**When to use:**
- **DISABLED**: Non-realistic AR, performance-critical apps
- **AMBIENT_INTENSITY**: Simple lighting adjustments
- **ENVIRONMENTAL_HDR**: Realistic rendering, product visualization

**Performance impact:** ENVIRONMENTAL_HDR has moderate GPU usage.

---

### Instant Placement (instantPlacementMode)

Enables quick object placement without waiting for plane detection.

**Options:**
- `DISABLED` - Disabled
- `LOCAL_Y_UP` - Enable with Y-axis pointing up

**Usage:**
```kotlin
config.instantPlacementMode = Config.InstantPlacementMode.LOCAL_Y_UP

// Use with hitTestInstantPlacement
val hits = frame.hitTestInstantPlacement(screenX, screenY, 1.0f)
```

**How it works:**
1. User taps screen
2. ARCore estimates depth based on nearby planes
3. Creates anchor at estimated position
4. Refines position as more environment data is gathered

**Benefits:**
- Immediate user feedback
- No waiting for plane detection
- Better onboarding experience

**Limitations:**
- Initial position is approximate
- Object may adjust position as tracking improves

---

### Augmented Images (augmentedImageDatabase)

Configure database of 2D images to detect and track.

**Usage:**
```kotlin
val database = AugmentedImageDatabase(session)

// Add images
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.marker)
database.addImage("marker_1", bitmap, 0.2f) // 0.2m physical width

// Configure
config.augmentedImageDatabase = database
session.configure(config)
```

**Image requirements:**
- High contrast
- Rich textures
- Avoid repetitive patterns
- Good lighting in capture
- Flat surface (no warping)

**Best practices:**
- Provide physical width for scale
- Limit to 1-2 active images for best performance
- Use high-quality images (1024x1024 recommended)
- Test images with `arcoreimg` CLI tool

**Performance impact:** More images = slower tracking. Optimize database for production.

---

### Augmented Faces (augmentedFaceMode)

Enable face tracking with 3D mesh.

**Options:**
- `DISABLED` - No face tracking
- `MESH3D` - Enable 3D face mesh

**Usage:**
```kotlin
// Requires front camera
val session = Session(context, EnumSet.of(Session.Feature.FRONT_CAMERA))

val config = Config(session).apply {
    augmentedFaceMode = Config.AugmentedFaceMode.MESH3D
}
session.configure(config)
```

**Features:**
- 468-point 3D mesh
- Face regions (nose, forehead, etc.)
- Real-time tracking
- Multiple face support

**Requirements:**
- Front-facing camera
- Session.Feature.FRONT_CAMERA
- Android 7.0+

**Use cases:**
- Face filters
- Makeup try-on
- Face masks
- Expression analysis

---

### Cloud Anchors (cloudAnchorMode)

Enable sharing AR experiences across devices.

**Options:**
- `DISABLED` - Cloud anchors disabled
- `ENABLED` - Enable hosting and resolving

**Usage:**
```kotlin
config.cloudAnchorMode = Config.CloudAnchorMode.ENABLED
session.configure(config)

// Host anchor
session.hostCloudAnchorAsync(
    anchor,
    ttlDays = 365,
    onSuccess = { cloudAnchorId ->
        // Share cloudAnchorId with other users
    },
    onError = { state -> }
)

// Resolve anchor
session.resolveCloudAnchorAsync(
    cloudAnchorId,
    onSuccess = { anchor -> },
    onError = { state -> }
)
```

**Benefits:**
- Multi-user AR experiences
- Persistent AR content
- Cross-device sharing

**Requirements:**
- Internet connection
- Google Cloud API key
- Good tracking quality (feature-rich environment)

**Limitations:**
- Hosting takes 5-15 seconds
- Requires good lighting
- Works best indoors with distinct features

---

### Geospatial API (geospatialMode)

Enable GPS-based world-scale AR.

**Options:**
- `DISABLED` - Geospatial disabled
- `ENABLED` - Enable GPS + Visual Positioning Service (VPS)

**Usage:**
```kotlin
config.geospatialMode = Config.GeospatialMode.ENABLED
session.configure(config)

// Check Earth tracking
val earth = session.earth
if (earth?.trackingState == TrackingState.TRACKING) {
    val pose = earth.cameraGeospatialPose
    val lat = pose.latitude
    val lon = pose.longitude
    val heading = pose.heading
}
```

**Features:**
- GPS positioning (outdoor)
- Visual Positioning Service (VPS) for high accuracy
- Geospatial anchors
- Terrain anchors

**Accuracy:**
- Standard: 10-20m horizontal
- VPS: 1-5m horizontal (in VPS-enabled areas)
- Heading: 5-15 degrees

**Requirements:**
- Internet connection
- Location permissions
- Outdoor or VPS-enabled indoor areas

**Use cases:**
- Navigation
- Location-based AR
- Landmark annotation
- Tourism apps

---

### Focus Mode (focusMode)

Control camera autofocus behavior.

**Options:**
- `AUTO` - Continuous autofocus
- `FIXED` - Fixed focus (infinity)

**Usage:**
```kotlin
config.focusMode = Config.FocusMode.AUTO
```

**When to use:**
- **AUTO**: General AR, varying distances
- **FIXED**: Distant objects, stabilize focus

**Performance impact:** Minimal.

---

### Update Mode (updateMode)

Control frame update timing.

**Options:**
- `BLOCKING` - Wait for new camera frame
- `LATEST_CAMERA_IMAGE` - Return latest available immediately

**Usage:**
```kotlin
config.updateMode = Config.UpdateMode.LATEST_CAMERA_IMAGE
```

**Comparison:**
- **BLOCKING**: Consistent frame timing, may drop frames if processing is slow
- **LATEST_CAMERA_IMAGE**: Always returns quickly, may skip frames

**Recommendation:** Use LATEST_CAMERA_IMAGE for most apps.

---

## Camera Configuration

Control camera resolution, FPS, and depth sensor usage.

### Camera Config Filter

```kotlin
val filter = CameraConfigFilter(session).apply {
    // Target FPS
    setTargetFps(EnumSet.of(
        CameraConfig.TargetFps.TARGET_FPS_30,
        CameraConfig.TargetFps.TARGET_FPS_60
    ))

    // Depth sensor
    setDepthSensorUsage(EnumSet.of(
        CameraConfig.DepthSensorUsage.REQUIRE_AND_USE
    ))
}

val configs = session.getSupportedCameraConfigs(filter)
```

### FPS Options

- `TARGET_FPS_30` - 30 FPS (better battery, lower latency)
- `TARGET_FPS_60` - 60 FPS (smoother, higher CPU/GPU usage)

### Depth Sensor Usage

- `DO_NOT_USE` - Don't use depth sensor
- `REQUIRE_AND_USE` - Require depth sensor
- `USE_IF_AVAILABLE` - Use if available

### Selecting Camera Config

```kotlin
// Highest resolution
val highRes = configs.maxByOrNull { it.imageSize.width * it.imageSize.height }

// Specific resolution
val preferred = configs.firstOrNull {
    it.imageSize.width == 1920 && it.imageSize.height == 1080
}

// Apply
session.cameraConfig = highRes ?: configs[0]
```

---

## Feature Combinations

### Basic Object Placement
```kotlin
config.apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
    depthMode = Config.DepthMode.AUTOMATIC
    instantPlacementMode = Config.InstantPlacementMode.LOCAL_Y_UP
}
```

### Image Tracking AR
```kotlin
val database = AugmentedImageDatabase(session)
// ... add images

config.apply {
    augmentedImageDatabase = database
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
    planeFindingMode = Config.PlaneFindingMode.DISABLED // Not needed
}
```

### Face Filters
```kotlin
val session = Session(context, EnumSet.of(Session.Feature.FRONT_CAMERA))

config.apply {
    augmentedFaceMode = Config.AugmentedFaceMode.MESH3D
    planeFindingMode = Config.PlaneFindingMode.DISABLED
}
```

### Multi-User AR
```kotlin
config.apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    cloudAnchorMode = Config.CloudAnchorMode.ENABLED
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
}
```

### Geospatial AR
```kotlin
config.apply {
    geospatialMode = Config.GeospatialMode.ENABLED
    planeFindingMode = Config.PlaneFindingMode.DISABLED // Optional
}
```

---

## Performance Optimization

### Minimal Configuration (Maximum Performance)
```kotlin
config.apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL // Not both
    lightEstimationMode = Config.LightEstimationMode.DISABLED
    depthMode = Config.DepthMode.DISABLED
    instantPlacementMode = Config.InstantPlacementMode.LOCAL_Y_UP
}

// Lower resolution/FPS
val filter = CameraConfigFilter(session).apply {
    setTargetFps(EnumSet.of(CameraConfig.TargetFps.TARGET_FPS_30))
}
```

### Balanced Configuration
```kotlin
config.apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    lightEstimationMode = Config.LightEstimationMode.AMBIENT_INTENSITY
    depthMode = Config.DepthMode.AUTOMATIC // If supported
    instantPlacementMode = Config.InstantPlacementMode.LOCAL_Y_UP
}
```

### Maximum Quality
```kotlin
config.apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
    depthMode = Config.DepthMode.AUTOMATIC
}

val filter = CameraConfigFilter(session).apply {
    setTargetFps(EnumSet.of(CameraConfig.TargetFps.TARGET_FPS_60))
}
```

---

## Configuration Validation

### Check Feature Support
```kotlin
// Depth support
val supportsDepth = session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)

// Geospatial support
val supportsGeospatial = session.isGeospatialModeSupported(Config.GeospatialMode.ENABLED)

// Camera configs
val configs = session.getSupportedCameraConfigs()
val supports60fps = configs.any { config ->
    config.fpsRange.upper == 60
}
```

### Runtime Configuration Changes
```kotlin
// Reconfigure during session
val newConfig = session.config.apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL
}
session.configure(newConfig)
```

**Note:** Some configurations require session recreation (e.g., switching between front/back camera).

---

## Troubleshooting

### Configuration Fails
- Check device compatibility
- Verify feature support before enabling
- Ensure session is in correct state

### Poor Performance
- Disable unused features
- Lower FPS target
- Reduce resolution
- Disable ENVIRONMENTAL_HDR if not needed

### Planes Not Detected
- Enable appropriate planeFindingMode
- Scan environment with camera
- Ensure good lighting
- Move device to scan more area

### Depth Not Working
- Check isDepthModeSupported()
- Verify device has depth capability
- Ensure sufficient features in environment

### Cloud Anchors Fail
- Verify internet connection
- Ensure cloudAnchorMode is ENABLED
- Check tracking quality (need feature-rich environment)
- Wait for good tracking state

### Geospatial Inaccurate
- Move to outdoor area or VPS-enabled location
- Wait for better accuracy readings
- Ensure location permissions granted
- Check internet connectivity for VPS

---

## Best Practices

1. **Check support before enabling features** - Not all devices support all features
2. **Start with minimal config** - Enable features as needed
3. **Test on target devices** - Performance varies by device
4. **Reconfigure dynamically** - Adjust based on runtime conditions
5. **Monitor performance** - Use Android Profiler to optimize
6. **Provide user guidance** - Explain when features need specific conditions
7. **Handle degraded modes gracefully** - Fall back when features unavailable
8. **Balance quality and performance** - Choose appropriate config for use case
