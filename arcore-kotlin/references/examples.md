# ARCore Implementation Examples

Complete, production-ready examples for common ARCore use cases with Kotlin.

## Table of Contents

1. [Basic AR Activity Setup](#basic-ar-activity-setup)
2. [Furniture Placement AR](#furniture-placement-ar)
3. [Image Marker AR](#image-marker-ar)
4. [Face Filter AR](#face-filter-ar)
5. [Multi-User Cloud Anchors](#multi-user-cloud-anchors)
6. [Geospatial AR Navigation](#geospatial-ar-navigation)
7. [Depth Occlusion](#depth-occlusion)
8. [AR Measurement Tool](#ar-measurement-tool)

---

## Basic AR Activity Setup

Complete activity with ARCore session lifecycle management.

```kotlin
import android.opengl.GLSurfaceView
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.google.ar.core.*
import com.google.ar.core.exceptions.*
import javax.microedition.khronos.egl.EGLConfig
import javax.microedition.khronos.opengles.GL10

class BasicARActivity : AppCompatActivity(), GLSurfaceView.Renderer {

    private lateinit var surfaceView: GLSurfaceView
    private var session: Session? = null
    private val messageQueue = mutableListOf<String>()

    // Installation and permissions
    private var userRequestedInstall = true
    private var cameraPermissionGranted = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Setup GLSurfaceView
        surfaceView = GLSurfaceView(this).apply {
            preserveEGLContextOnPause = true
            setEGLContextClientVersion(2)
            setEGLConfigChooser(8, 8, 8, 8, 16, 0)
            setRenderer(this@BasicARActivity)
            renderMode = GLSurfaceView.RENDERMODE_CONTINUOUSLY
        }
        setContentView(surfaceView)

        // Request camera permission
        if (!hasCameraPermission()) {
            requestCameraPermission()
        }
    }

    override fun onResume() {
        super.onResume()

        // Check ARCore installation
        if (session == null) {
            try {
                when (ArCoreApk.getInstance().requestInstall(this, userRequestedInstall)) {
                    ArCoreApk.InstallStatus.INSTALLED -> {
                        // Success - create session
                        if (hasCameraPermission()) {
                            session = Session(this)
                            configureSession()
                        }
                    }
                    ArCoreApk.InstallStatus.INSTALL_REQUESTED -> {
                        // Installation started
                        userRequestedInstall = false
                        return
                    }
                }
            } catch (e: UnavailableArcoreNotInstalledException) {
                showMessage("Please install ARCore")
            } catch (e: UnavailableDeviceNotCompatibleException) {
                showMessage("This device does not support AR")
            } catch (e: UnavailableApkTooOldException) {
                showMessage("Please update ARCore")
            } catch (e: UnavailableSdkTooOldException) {
                showMessage("Please update this app")
            } catch (e: Exception) {
                showMessage("Failed to create AR session: ${e.message}")
            }
        }

        session?.resume()
        surfaceView.onResume()
    }

    override fun onPause() {
        super.onPause()
        session?.pause()
        surfaceView.onPause()
    }

    override fun onDestroy() {
        session?.close()
        session = null
        super.onDestroy()
    }

    private fun configureSession() {
        val config = Config(session!!).apply {
            planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
            lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
            depthMode = Config.DepthMode.AUTOMATIC
            instantPlacementMode = Config.InstantPlacementMode.LOCAL_Y_UP
        }
        session?.configure(config)
    }

    // GLSurfaceView.Renderer implementation
    override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) {
        // Initialize rendering (load shaders, textures, etc.)
    }

    override fun onSurfaceChanged(gl: GL10?, width: Int, height: Int) {
        session?.setDisplayGeometry(
            windowManager.defaultDisplay.rotation,
            width,
            height
        )
    }

    override fun onDrawFrame(gl: GL10?) {
        val session = session ?: return

        try {
            // Update ARCore session
            val frame = session.update()

            // Check camera tracking
            when (frame.camera.trackingState) {
                TrackingState.TRACKING -> {
                    // Render AR content
                    renderScene(frame)
                }
                TrackingState.PAUSED -> {
                    // Show tracking lost message
                    handleTrackingFailure(frame.camera.trackingFailureReason)
                }
                else -> {}
            }

        } catch (e: Exception) {
            showMessage("Error: ${e.message}")
        }
    }

    private fun renderScene(frame: Frame) {
        // Get view and projection matrices
        val viewMatrix = FloatArray(16)
        val projectionMatrix = FloatArray(16)
        frame.camera.getViewMatrix(viewMatrix, 0)
        frame.camera.getProjectionMatrix(projectionMatrix, 0, 0.1f, 100f)

        // Render AR objects, planes, etc.
    }

    private fun handleTrackingFailure(reason: TrackingFailureReason) {
        val message = when (reason) {
            TrackingFailureReason.INSUFFICIENT_LIGHT -> "Need more light"
            TrackingFailureReason.EXCESSIVE_MOTION -> "Moving too fast"
            TrackingFailureReason.INSUFFICIENT_FEATURES -> "Point at surfaces with more detail"
            else -> "Tracking lost"
        }
        showMessage(message)
    }

    private fun showMessage(message: String) {
        messageQueue.add(message)
    }

    private fun hasCameraPermission(): Boolean {
        return checkSelfPermission(android.Manifest.permission.CAMERA) ==
                android.content.pm.PackageManager.PERMISSION_GRANTED
    }

    private fun requestCameraPermission() {
        requestPermissions(arrayOf(android.Manifest.permission.CAMERA), 0)
    }
}
```

---

## Furniture Placement AR

Complete furniture placement with plane visualization and object anchoring.

```kotlin
class FurniturePlacementActivity : AppCompatActivity() {

    private lateinit var session: Session
    private val anchoredObjects = mutableListOf<AnchoredObject>()

    data class AnchoredObject(
        val anchor: Anchor,
        val modelName: String
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Setup UI
        val placeButton = findViewById<Button>(R.id.placeButton)
        placeButton.setOnClickListener {
            placeObject()
        }
    }

    private fun onDrawFrame(frame: Frame) {
        // Clear background
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT or GLES20.GL_DEPTH_BUFFER_BIT)

        // Get camera matrices
        val viewMatrix = FloatArray(16)
        val projectionMatrix = FloatArray(16)
        frame.camera.getViewMatrix(viewMatrix, 0)
        frame.camera.getProjectionMatrix(projectionMatrix, 0, 0.1f, 100f)

        // Visualize detected planes
        renderPlanes(frame, viewMatrix, projectionMatrix)

        // Render placed objects
        renderAnchoredObjects(viewMatrix, projectionMatrix)
    }

    private fun placeObject() {
        val frame = session.update()

        // Perform hit test at screen center
        val screenX = surfaceView.width / 2f
        val screenY = surfaceView.height / 2f

        val hitResults = frame.hitTest(screenX, screenY)

        for (hit in hitResults) {
            val trackable = hit.trackable

            // Place on detected plane
            if (trackable is Plane && trackable.isPoseInPolygon(hit.hitPose)) {
                // Create anchor
                val anchor = hit.createAnchor()

                // Store anchored object
                anchoredObjects.add(
                    AnchoredObject(
                        anchor = anchor,
                        modelName = "chair.obj"
                    )
                )

                Toast.makeText(this, "Object placed!", Toast.LENGTH_SHORT).show()
                break
            }
        }
    }

    private fun renderPlanes(
        frame: Frame,
        viewMatrix: FloatArray,
        projectionMatrix: FloatArray
    ) {
        val planes = frame.getUpdatedTrackables(Plane::class.java)

        for (plane in planes) {
            if (plane.trackingState != TrackingState.TRACKING) continue
            if (plane.subsumedBy != null) continue

            // Render plane visualization
            when (plane.type) {
                Plane.Type.HORIZONTAL_UPWARD_FACING -> {
                    renderPlaneGrid(plane, viewMatrix, projectionMatrix, Color.GREEN)
                }
                Plane.Type.VERTICAL -> {
                    renderPlaneGrid(plane, viewMatrix, projectionMatrix, Color.BLUE)
                }
                else -> {}
            }
        }
    }

    private fun renderPlaneGrid(
        plane: Plane,
        viewMatrix: FloatArray,
        projectionMatrix: FloatArray,
        color: Int
    ) {
        // Get plane polygon
        val polygon = plane.polygon

        // Get plane center pose
        val modelMatrix = FloatArray(16)
        plane.centerPose.toMatrix(modelMatrix, 0)

        // Render grid using OpenGL
        // (Implementation depends on rendering engine)
    }

    private fun renderAnchoredObjects(
        viewMatrix: FloatArray,
        projectionMatrix: FloatArray
    ) {
        // Remove detached anchors
        anchoredObjects.removeAll { obj ->
            obj.anchor.trackingState == TrackingState.STOPPED
        }

        // Render each object
        for (obj in anchoredObjects) {
            if (obj.anchor.trackingState != TrackingState.TRACKING) continue

            // Get object model matrix
            val modelMatrix = FloatArray(16)
            obj.anchor.pose.toMatrix(modelMatrix, 0)

            // Apply any transformations (rotation, scale, etc.)
            // Scale to appropriate size (e.g., 0.5m)
            Matrix.scaleM(modelMatrix, 0, 0.5f, 0.5f, 0.5f)

            // Render 3D model
            render3DModel(obj.modelName, modelMatrix, viewMatrix, projectionMatrix)
        }
    }

    private fun render3DModel(
        modelName: String,
        modelMatrix: FloatArray,
        viewMatrix: FloatArray,
        projectionMatrix: FloatArray
    ) {
        // Load and render 3D model
        // (Use library like Sceneform, Filament, or custom OpenGL)
    }

    override fun onDestroy() {
        // Detach all anchors
        anchoredObjects.forEach { it.anchor.detach() }
        anchoredObjects.clear()
        super.onDestroy()
    }
}
```

---

## Image Marker AR

Detect and track 2D images to place AR content.

```kotlin
class ImageMarkerARActivity : AppCompatActivity() {

    private lateinit var session: Session
    private val trackedImages = mutableMapOf<String, Anchor>()

    private fun setupAugmentedImages() {
        // Create image database
        val database = AugmentedImageDatabase(session)

        // Add images from resources
        val markerImages = listOf(
            "product_box" to R.drawable.product_box,
            "poster" to R.drawable.movie_poster,
            "business_card" to R.drawable.business_card
        )

        for ((name, resourceId) in markerImages) {
            val bitmap = BitmapFactory.decodeResource(resources, resourceId)
            database.addImage(name, bitmap, 0.15f) // 15cm physical width
        }

        // Configure session
        val config = session.config.apply {
            augmentedImageDatabase = database
            planeFindingMode = Config.PlaneFindingMode.DISABLED // Not needed
        }
        session.configure(config)
    }

    private fun onDrawFrame(frame: Frame) {
        // Track augmented images
        val images = frame.getUpdatedTrackables(AugmentedImage::class.java)

        for (image in images) {
            when (image.trackingState) {
                TrackingState.TRACKING -> {
                    if (image.trackingMethod == AugmentedImage.TrackingMethod.FULL_TRACKING) {
                        handleTrackedImage(image)
                    }
                }
                TrackingState.PAUSED -> {
                    // Image was tracked but now lost
                    trackedImages.remove(image.name)?.detach()
                }
                else -> {}
            }
        }

        // Render content for tracked images
        renderTrackedImages()
    }

    private fun handleTrackedImage(image: AugmentedImage) {
        val imageName = image.name

        // Create anchor if not already tracking
        if (!trackedImages.containsKey(imageName)) {
            val anchor = image.createAnchor(image.centerPose)
            trackedImages[imageName] = anchor

            onImageDetected(imageName, image)
        }
    }

    private fun onImageDetected(imageName: String, image: AugmentedImage) {
        when (imageName) {
            "product_box" -> {
                // Show 3D product demo
                Log.d("AR", "Product box detected!")
            }
            "poster" -> {
                // Play movie trailer
                Log.d("AR", "Movie poster detected!")
            }
            "business_card" -> {
                // Show contact info
                Log.d("AR", "Business card detected!")
            }
        }
    }

    private fun renderTrackedImages() {
        val viewMatrix = FloatArray(16)
        val projectionMatrix = FloatArray(16)

        trackedImages.forEach { (imageName, anchor) ->
            if (anchor.trackingState == TrackingState.TRACKING) {
                val modelMatrix = FloatArray(16)
                anchor.pose.toMatrix(modelMatrix, 0)

                // Render content based on image name
                when (imageName) {
                    "product_box" -> render3DProduct(modelMatrix, viewMatrix, projectionMatrix)
                    "poster" -> renderVideoOverlay(modelMatrix, viewMatrix, projectionMatrix)
                    "business_card" -> renderContactInfo(modelMatrix, viewMatrix, projectionMatrix)
                }
            }
        }
    }

    private fun render3DProduct(
        modelMatrix: FloatArray,
        viewMatrix: FloatArray,
        projectionMatrix: FloatArray
    ) {
        // Offset above image
        val offsetPose = Pose.makeTranslation(0f, 0.1f, 0f)
        val finalMatrix = FloatArray(16)
        // Apply offset
        Matrix.multiplyMM(finalMatrix, 0, modelMatrix, 0, offsetPose.toMatrix(FloatArray(16), 0), 0)

        // Render 3D model
    }

    private fun renderVideoOverlay(
        modelMatrix: FloatArray,
        viewMatrix: FloatArray,
        projectionMatrix: FloatArray
    ) {
        // Render video quad aligned with image
    }

    private fun renderContactInfo(
        modelMatrix: FloatArray,
        viewMatrix: FloatArray,
        projectionMatrix: FloatArray
    ) {
        // Render UI overlay with contact details
    }
}
```

---

## Face Filter AR

Real-time face tracking with 3D mesh and filters.

```kotlin
class FaceFilterActivity : AppCompatActivity() {

    private lateinit var session: Session

    private fun createSession() {
        // Create session with front camera
        session = Session(this, EnumSet.of(Session.Feature.FRONT_CAMERA))

        // Configure for face tracking
        val config = Config(session).apply {
            augmentedFaceMode = Config.AugmentedFaceMode.MESH3D
            planeFindingMode = Config.PlaneFindingMode.DISABLED
        }
        session.configure(config)
    }

    private fun onDrawFrame(frame: Frame) {
        val faces = frame.getUpdatedTrackables(AugmentedFace::class.java)

        for (face in faces) {
            if (face.trackingState == TrackingState.TRACKING) {
                renderFaceFilter(face)
            }
        }
    }

    private fun renderFaceFilter(face: AugmentedFace) {
        // Get face mesh
        val vertices = face.meshVertices
        val normals = face.meshNormals
        val uvs = face.meshTextureCoordinates
        val indices = face.meshTriangleIndices

        // Render face mesh with texture
        renderFaceMesh(vertices, normals, uvs, indices)

        // Add accessories at specific face regions
        renderAccessories(face)
    }

    private fun renderAccessories(face: AugmentedFace) {
        // Get nose tip position for glasses
        val noseTipPose = face.getRegionPose(AugmentedFace.RegionType.NOSE_TIP)
        val modelMatrix = FloatArray(16)
        noseTipPose.toMatrix(modelMatrix, 0)

        // Adjust position for glasses
        val glassesOffset = Pose.makeTranslation(0f, 0.03f, 0.08f)
        // ... render glasses 3D model

        // Get forehead for hat/crown
        val foreheadLeft = face.getRegionPose(AugmentedFace.RegionType.FOREHEAD_LEFT)
        val foreheadRight = face.getRegionPose(AugmentedFace.RegionType.FOREHEAD_RIGHT)

        // Calculate center and orientation for hat
        val hatPose = calculateHatPose(foreheadLeft, foreheadRight, face.centerPose)
        // ... render hat 3D model
    }

    private fun renderFaceMesh(
        vertices: FloatBuffer,
        normals: FloatBuffer,
        uvs: FloatBuffer,
        indices: ShortBuffer
    ) {
        // Bind texture (face paint, makeup, etc.)
        // Draw mesh with OpenGL
        // Apply blend modes for realistic effects
    }

    private fun calculateHatPose(
        foreheadLeft: Pose,
        foreheadRight: Pose,
        centerPose: Pose
    ): Pose {
        // Calculate midpoint
        val leftTrans = foreheadLeft.translation
        val rightTrans = foreheadRight.translation

        val midX = (leftTrans[0] + rightTrans[0]) / 2f
        val midY = (leftTrans[1] + rightTrans[1]) / 2f
        val midZ = (leftTrans[2] + rightTrans[2]) / 2f

        // Offset upward for hat placement
        val hatTranslation = floatArrayOf(midX, midY + 0.15f, midZ)

        return Pose(hatTranslation, centerPose.rotationQuaternion)
    }
}
```

---

## Multi-User Cloud Anchors

Share AR experiences across multiple devices.

```kotlin
class CloudAnchorActivity : AppCompatActivity() {

    private lateinit var session: Session
    private lateinit var firebaseDatabase: DatabaseReference

    private var currentCloudAnchor: Anchor? = null
    private var hostingInProgress = false

    private fun setupCloudAnchors() {
        // Enable cloud anchors
        val config = session.config.apply {
            cloudAnchorMode = Config.CloudAnchorMode.ENABLED
            planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
        }
        session.configure(config)

        // Initialize Firebase
        firebaseDatabase = FirebaseDatabase.getInstance().reference
    }

    // Host anchor (create shared experience)
    private fun hostCloudAnchor(localAnchor: Anchor) {
        if (hostingInProgress) return

        hostingInProgress = true
        showMessage("Hosting anchor...")

        session.hostCloudAnchorAsync(
            localAnchor,
            ttlDays = 365,
            onSuccess = { cloudAnchorId ->
                hostingInProgress = false
                showMessage("Anchor hosted successfully!")

                // Save to Firebase for other users
                saveCloudAnchorToFirebase(cloudAnchorId)
            },
            onError = { error ->
                hostingInProgress = false
                showMessage("Hosting failed: $error")
            }
        )
    }

    private fun saveCloudAnchorToFirebase(cloudAnchorId: String) {
        val roomId = generateRoomId() // Or use existing room

        val anchorData = mapOf(
            "cloudAnchorId" to cloudAnchorId,
            "timestamp" to System.currentTimeMillis(),
            "userId" to getCurrentUserId()
        )

        firebaseDatabase
            .child("rooms")
            .child(roomId)
            .child("anchors")
            .push()
            .setValue(anchorData)
            .addOnSuccessListener {
                showMessage("Shared with room: $roomId")
            }
    }

    // Resolve anchor (join shared experience)
    private fun resolveCloudAnchor(cloudAnchorId: String) {
        showMessage("Resolving anchor...")

        session.resolveCloudAnchorAsync(
            cloudAnchorId,
            onSuccess = { anchor ->
                currentCloudAnchor = anchor
                showMessage("Anchor resolved!")

                // Place shared content at anchor
                placeSharedContent(anchor)
            },
            onError = { error ->
                showMessage("Resolving failed: $error")
            }
        )
    }

    private fun listenForSharedAnchors(roomId: String) {
        firebaseDatabase
            .child("rooms")
            .child(roomId)
            .child("anchors")
            .addChildEventListener(object : ChildEventListener {
                override fun onChildAdded(snapshot: DataSnapshot, previousChildName: String?) {
                    val cloudAnchorId = snapshot.child("cloudAnchorId").getValue(String::class.java)
                    cloudAnchorId?.let {
                        resolveCloudAnchor(it)
                    }
                }

                override fun onChildChanged(snapshot: DataSnapshot, previousChildName: String?) {}
                override fun onChildRemoved(snapshot: DataSnapshot) {}
                override fun onChildMoved(snapshot: DataSnapshot, previousChildName: String?) {}
                override fun onCancelled(error: DatabaseError) {}
            })
    }

    private fun placeSharedContent(anchor: Anchor) {
        // Render content at shared anchor location
        // All users see same content at same location
    }

    private fun generateRoomId(): String {
        return (1000..9999).random().toString()
    }

    private fun getCurrentUserId(): String {
        return "user_${System.currentTimeMillis()}"
    }
}
```

---

## Geospatial AR Navigation

GPS-based AR with waypoint navigation.

```kotlin
class GeospatialNavigationActivity : AppCompatActivity() {

    private lateinit var session: Session
    private val waypoints = mutableListOf<GeospatialAnchor>()

    data class GeospatialAnchor(
        val anchor: Anchor,
        val latitude: Double,
        val longitude: Double,
        val name: String
    )

    private fun setupGeospatial() {
        // Enable geospatial mode
        val config = session.config.apply {
            geospatialMode = Config.GeospatialMode.ENABLED
        }
        session.configure(config)

        // Add location permission check
        checkLocationPermission()
    }

    private fun onDrawFrame(frame: Frame) {
        val earth = session.earth ?: return

        // Check geospatial tracking
        if (earth.trackingState == TrackingState.TRACKING) {
            val geoPose = earth.cameraGeospatialPose

            // Update UI with current location
            updateLocationUI(geoPose)

            // Check accuracy
            if (geoPose.horizontalAccuracy < 5.0 && geoPose.headingAccuracy < 15.0) {
                // Good accuracy - can place anchors
                renderWaypoints()
            } else {
                showMessage("Improving accuracy...")
            }
        }
    }

    private fun addWaypoint(lat: Double, lon: Double, name: String) {
        val earth = session.earth ?: return

        // Create geospatial anchor at location
        val anchor = earth.createAnchor(
            latitude = lat,
            longitude = lon,
            altitude = earth.cameraGeospatialPose.altitude,
            qx = 0f, qy = 0f, qz = 0f, qw = 1f
        )

        waypoints.add(GeospatialAnchor(anchor, lat, lon, name))
        showMessage("Waypoint added: $name")
    }

    private fun addTerrainAnchor(lat: Double, lon: Double, heightAboveTerrain: Float) {
        val earth = session.earth ?: return

        earth.resolveAnchorOnTerrain(
            latitude = lat,
            longitude = lon,
            altitudeAboveTerrain = heightAboveTerrain,
            qx = 0f, qy = 0f, qz = 0f, qw = 1f
        ).thenAccept { result ->
            when (result.terrainAnchorState) {
                TerrainAnchorState.SUCCESS -> {
                    val anchor = result.anchor
                    showMessage("Terrain anchor created")
                }
                else -> {
                    showMessage("Terrain anchor failed: ${result.terrainAnchorState}")
                }
            }
        }
    }

    private fun renderWaypoints() {
        val earth = session.earth ?: return
        val currentPose = earth.cameraGeospatialPose

        for (waypoint in waypoints) {
            if (waypoint.anchor.trackingState == TrackingState.TRACKING) {
                // Calculate distance
                val distance = calculateDistance(
                    currentPose.latitude, currentPose.longitude,
                    waypoint.latitude, waypoint.longitude
                )

                // Render waypoint marker
                renderWaypointMarker(waypoint, distance)

                // Show navigation arrow if close
                if (distance < 50.0) { // Within 50m
                    renderNavigationArrow(waypoint)
                }
            }
        }
    }

    private fun renderWaypointMarker(waypoint: GeospatialAnchor, distance: Double) {
        val modelMatrix = FloatArray(16)
        waypoint.anchor.pose.toMatrix(modelMatrix, 0)

        // Render marker with label and distance
        // renderMarker(modelMatrix, waypoint.name, distance)
    }

    private fun renderNavigationArrow(waypoint: GeospatialAnchor) {
        // Calculate direction to waypoint
        // Render arrow pointing toward waypoint
    }

    private fun calculateDistance(
        lat1: Double, lon1: Double,
        lat2: Double, lon2: Double
    ): Double {
        val R = 6371000.0 // Earth radius in meters

        val dLat = Math.toRadians(lat2 - lat1)
        val dLon = Math.toRadians(lon2 - lon1)

        val a = sin(dLat / 2) * sin(dLat / 2) +
                cos(Math.toRadians(lat1)) * cos(Math.toRadians(lat2)) *
                sin(dLon / 2) * sin(dLon / 2)

        val c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c
    }

    private fun updateLocationUI(geoPose: GeospatialPose) {
        runOnUiThread {
            findViewById<TextView>(R.id.latTextView).text =
                "Lat: ${"%.6f".format(geoPose.latitude)}"
            findViewById<TextView>(R.id.lonTextView).text =
                "Lon: ${"%.6f".format(geoPose.longitude)}"
            findViewById<TextView>(R.id.headingTextView).text =
                "Heading: ${"%.1f".format(geoPose.heading)}°"
            findViewById<TextView>(R.id.accuracyTextView).text =
                "Accuracy: ${"%.1f".format(geoPose.horizontalAccuracy)}m"
        }
    }

    private fun checkLocationPermission() {
        if (checkSelfPermission(android.Manifest.permission.ACCESS_FINE_LOCATION) !=
            PackageManager.PERMISSION_GRANTED) {
            requestPermissions(
                arrayOf(android.Manifest.permission.ACCESS_FINE_LOCATION),
                LOCATION_PERMISSION_REQUEST
            )
        }
    }

    companion object {
        const val LOCATION_PERMISSION_REQUEST = 1
    }
}
```

---

## Depth Occlusion

Use depth API for realistic occlusion.

```kotlin
class DepthOcclusionActivity : AppCompatActivity() {

    private lateinit var session: Session
    private var depthTexture: Int = 0

    private fun setupDepth() {
        // Check depth support
        if (session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)) {
            val config = session.config.apply {
                depthMode = Config.DepthMode.AUTOMATIC
            }
            session.configure(config)

            // Create depth texture
            depthTexture = createDepthTexture()
        } else {
            showMessage("Depth not supported on this device")
        }
    }

    private fun onDrawFrame(frame: Frame) {
        // Get depth image
        try {
            val depthImage = frame.acquireDepthImage16Bits()

            // Upload to GPU
            uploadDepthToTexture(depthImage)

            depthImage.close()

            // Render with occlusion
            renderWithOcclusion(frame)

        } catch (e: NotYetAvailableException) {
            // Depth not ready yet
        }
    }

    private fun renderWithOcclusion(frame: Frame) {
        // 1. Render depth texture to depth buffer
        renderDepthToBuffer()

        // 2. Render AR objects with depth test enabled
        GLES20.glEnable(GLES20.GL_DEPTH_TEST)

        for (anchor in anchors) {
            if (anchor.trackingState == TrackingState.TRACKING) {
                val modelMatrix = FloatArray(16)
                anchor.pose.toMatrix(modelMatrix, 0)

                // Render with depth test
                // Objects behind real surfaces will be occluded
                render3DModel(modelMatrix)
            }
        }
    }

    private fun uploadDepthToTexture(depthImage: Image) {
        val width = depthImage.width
        val height = depthImage.height
        val buffer = depthImage.planes[0].buffer

        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, depthTexture)
        GLES20.glTexImage2D(
            GLES20.GL_TEXTURE_2D,
            0,
            GLES20.GL_RG8,
            width,
            height,
            0,
            GLES20.GL_RG,
            GLES20.GL_UNSIGNED_BYTE,
            buffer
        )
    }

    private fun createDepthTexture(): Int {
        val textures = IntArray(1)
        GLES20.glGenTextures(1, textures, 0)

        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textures[0])
        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_S, GLES20.GL_CLAMP_TO_EDGE)
        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_T, GLES20.GL_CLAMP_TO_EDGE)
        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MIN_FILTER, GLES20.GL_LINEAR)
        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MAG_FILTER, GLES20.GL_LINEAR)

        return textures[0]
    }

    private fun renderDepthToBuffer() {
        // Shader that converts depth texture to depth buffer
        // Uses custom fragment shader to write depth values
    }
}
```

---

## AR Measurement Tool

Measure real-world distances using AR.

```kotlin
class ARMeasurementActivity : AppCompatActivity() {

    private lateinit var session: Session
    private val measurementPoints = mutableListOf<Anchor>()
    private var currentMeasurement: Pair<Anchor, Anchor>? = null

    private fun onScreenTap(x: Float, y: Float) {
        val frame = session.update()

        val hitResults = frame.hitTest(x, y)

        for (hit in hitResults) {
            val trackable = hit.trackable

            if (trackable is Plane && trackable.isPoseInPolygon(hit.hitPose)) {
                addMeasurementPoint(hit)
                break
            }
        }
    }

    private fun addMeasurementPoint(hit: HitResult) {
        val anchor = hit.createAnchor()
        measurementPoints.add(anchor)

        when (measurementPoints.size) {
            1 -> {
                showMessage("Tap second point to measure")
            }
            2 -> {
                // Calculate distance
                currentMeasurement = Pair(measurementPoints[0], measurementPoints[1])
                val distance = calculateDistance(measurementPoints[0], measurementPoints[1])
                showMeasurement(distance)
            }
            else -> {
                // Reset for new measurement
                measurementPoints.forEach { it.detach() }
                measurementPoints.clear()
                measurementPoints.add(anchor)
                currentMeasurement = null
                showMessage("Measurement reset. Tap second point.")
            }
        }
    }

    private fun calculateDistance(anchor1: Anchor, anchor2: Anchor): Float {
        val pose1 = anchor1.pose.translation
        val pose2 = anchor2.pose.translation

        val dx = pose2[0] - pose1[0]
        val dy = pose2[1] - pose1[1]
        val dz = pose2[2] - pose1[2]

        return sqrt(dx * dx + dy * dy + dz * dz)
    }

    private fun showMeasurement(distance: Float) {
        val distanceCm = distance * 100
        val distanceInches = distance * 39.3701f

        showMessage(
            "Distance: %.1f cm (%.1f inches)".format(distanceCm, distanceInches)
        )
    }

    private fun onDrawFrame(frame: Frame) {
        // Render measurement points
        for (anchor in measurementPoints) {
            if (anchor.trackingState == TrackingState.TRACKING) {
                renderPoint(anchor.pose)
            }
        }

        // Render line between points
        currentMeasurement?.let { (start, end) ->
            if (start.trackingState == TrackingState.TRACKING &&
                end.trackingState == TrackingState.TRACKING) {
                renderLine(start.pose, end.pose)
                renderDistanceLabel(start.pose, end.pose)
            }
        }
    }

    private fun renderPoint(pose: Pose) {
        val modelMatrix = FloatArray(16)
        pose.toMatrix(modelMatrix, 0)

        // Render small sphere at point
        renderSphere(modelMatrix, 0.01f, Color.RED)
    }

    private fun renderLine(startPose: Pose, endPose: Pose) {
        // Render line between two points
        val start = startPose.translation
        val end = endPose.translation

        // Create line vertices
        val lineVertices = floatArrayOf(
            start[0], start[1], start[2],
            end[0], end[1], end[2]
        )

        // Render with OpenGL line primitive
    }

    private fun renderDistanceLabel(startPose: Pose, endPose: Pose) {
        // Calculate midpoint
        val start = startPose.translation
        val end = endPose.translation

        val midX = (start[0] + end[0]) / 2f
        val midY = (start[1] + end[1]) / 2f
        val midZ = (start[2] + end[2]) / 2f

        // Render text label at midpoint
        val distance = calculateDistance(
            measurementPoints[0],
            measurementPoints[1]
        )

        renderTextLabel(
            floatArrayOf(midX, midY, midZ),
            "%.2f m".format(distance)
        )
    }

    private fun renderSphere(modelMatrix: FloatArray, radius: Float, color: Int) {
        // Render sphere using OpenGL
    }

    private fun renderTextLabel(position: FloatArray, text: String) {
        // Render 3D text label
    }
}
```

---

## Common Patterns

### Singleton Session Manager
```kotlin
object ARSessionManager {
    private var session: Session? = null

    fun getSession(context: Context): Session {
        if (session == null) {
            session = Session(context)
        }
        return session!!
    }

    fun pause() {
        session?.pause()
    }

    fun resume() {
        session?.resume()
    }

    fun destroy() {
        session?.close()
        session = null
    }
}
```

### Anchor Manager
```kotlin
class AnchorManager {
    private val anchors = mutableListOf<Anchor>()

    fun addAnchor(anchor: Anchor) {
        anchors.add(anchor)
    }

    fun removeAnchor(anchor: Anchor) {
        anchor.detach()
        anchors.remove(anchor)
    }

    fun getActiveAnchors(): List<Anchor> {
        return anchors.filter { it.trackingState == TrackingState.TRACKING }
    }

    fun clearAll() {
        anchors.forEach { it.detach() }
        anchors.clear()
    }
}
```

---

These examples provide complete, production-ready implementations for common ARCore use cases. Adapt them based on specific app requirements and rendering engines.
