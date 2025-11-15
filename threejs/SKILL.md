---
name: threejs
description: Comprehensive guide for implementing Three.js (r181) in web applications. Use when creating 3D graphics, WebGL applications, interactive visualizations, or when implementing animations, cameras, renderers, geometries, materials, lighting, textures, audio, physics, controls, or any Three.js-related features. This skill is web technology agnostic and covers core API, addons, nodes, and WebGPU support.
---

# Three.js - JavaScript 3D Library

## Overview

Three.js is a cross-browser JavaScript library and API for creating and displaying animated 3D computer graphics in web browsers using WebGL. Three.js (current stable: r181) provides a comprehensive framework for building complex 3D scenes with minimal code, abstracting WebGL complexity while maintaining performance and flexibility.

Use this skill when:
- Building 3D visualizations or interactive experiences for the web
- Creating WebGL applications with cameras, lights, geometries, and materials
- Implementing animations, particle systems, or visual effects
- Working with 3D model loaders (GLTF, OBJ, FBX, etc.)
- Setting up camera controls (Orbit, Fly, Transform, etc.)
- Integrating physics simulations or post-processing effects
- Developing WebGPU applications with node-based materials
- Creating immersive AR/VR experiences with WebXR

## Core Concepts and Nomenclature

### Fundamental Three.js Architecture

**Scene**: The container that holds all 3D objects, lights, and cameras. Everything visible must be added to a scene.

**Camera**: Defines the viewpoint from which the scene is rendered. Determines what the user sees and perspective.

**Renderer**: The engine that draws the scene to the canvas using WebGL, WebGPU, or other rendering backends.

**Object3D**: The base class for most Three.js objects. Provides transformation properties (position, rotation, scale).

**Mesh**: Combines a Geometry (shape) and Material (appearance) into a visible 3D object.

**Geometry**: Defines the shape/structure of a 3D object (vertices, faces, UVs).

**Material**: Defines how an object appears (color, texture, reflectivity, shading).

**Texture**: Images or data mapped onto geometry surfaces.

**Light**: Illuminates objects in the scene with various lighting models.

### Essential Three.js Pattern

Every Three.js application requires these three fundamental components:

```javascript
// 1. Scene - container for all objects
const scene = new THREE.Scene();

// 2. Camera - viewpoint
const camera = new THREE.PerspectiveCamera(
    75,                                    // Field of view
    window.innerWidth / window.innerHeight, // Aspect ratio
    0.1,                                   // Near clipping plane
    1000                                   // Far clipping plane
);

// 3. Renderer - draws the scene
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
```

## Installation and Setup

### Package Installation

Install via npm for module bundlers:

```bash
npm install three
```

Import in your application:

```javascript
// Import entire library
import * as THREE from 'three';

// Import specific classes
import { Scene, PerspectiveCamera, WebGLRenderer } from 'three';

// Import addons (from examples/jsm/)
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
```

### CDN Usage

For quick prototyping without build tools:

```html
<script type="importmap">
{
    "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.181.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.181.0/examples/jsm/"
    }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
// Your code here
</script>
```

### Basic Setup Pattern

```javascript
import * as THREE from 'three';

// Scene setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x222222);

// Camera setup
const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);
camera.position.z = 5;

// Renderer setup
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
```

## Cameras

Cameras define the viewpoint and projection for rendering the scene.

### PerspectiveCamera

Most common camera type, mimics human eye perspective with realistic depth.

```javascript
const camera = new THREE.PerspectiveCamera(
    fov,    // Field of view (degrees)
    aspect, // Aspect ratio (width/height)
    near,   // Near clipping plane
    far     // Far clipping plane
);

// Example
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 5, 10);
camera.lookAt(0, 0, 0);
```

**Field of View (FOV)**: Vertical viewing angle in degrees (typical: 45-75)
**Aspect Ratio**: Width/height ratio (match canvas dimensions)
**Near/Far Planes**: Objects outside this range are clipped (not rendered)

### OrthographicCamera

No perspective distortion, objects same size regardless of distance. Useful for 2D games, CAD, technical visualizations.

```javascript
const camera = new THREE.OrthographicCamera(
    left,   // Left plane
    right,  // Right plane
    top,    // Top plane
    bottom, // Bottom plane
    near,   // Near plane
    far     // Far plane
);

// Example - maintain aspect ratio
const aspect = window.innerWidth / window.innerHeight;
const frustumSize = 10;
const camera = new THREE.OrthographicCamera(
    frustumSize * aspect / -2,
    frustumSize * aspect / 2,
    frustumSize / 2,
    frustumSize / -2,
    0.1,
    1000
);
```

### Camera Control

```javascript
// Position
camera.position.set(x, y, z);
camera.position.x = 10;

// Rotation (radians)
camera.rotation.set(x, y, z);

// Look at target
camera.lookAt(targetVector);
camera.lookAt(0, 0, 0); // Look at origin

// Update projection after changes
camera.updateProjectionMatrix();

// Camera zoom (changes FOV for perspective, scale for orthographic)
camera.zoom = 2;
camera.updateProjectionMatrix();
```

## Renderers

Renderers draw the scene from the camera's perspective to a canvas.

### WebGLRenderer

Standard renderer using WebGL for hardware-accelerated 3D graphics.

```javascript
const renderer = new THREE.WebGLRenderer({
    antialias: true,           // Enable antialiasing
    alpha: true,               // Transparent background
    canvas: canvasElement,     // Use existing canvas
    powerPreference: 'high-performance',
    precision: 'highp',        // Shader precision
    stencil: false,            // Disable stencil buffer if not needed
    depth: true,               // Enable depth buffer
    logarithmicDepthBuffer: false
});

// Common settings
renderer.setSize(width, height);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setClearColor(0x000000, 1); // Background color and alpha

// Shadow settings
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// Tone mapping
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// Output encoding
renderer.outputEncoding = THREE.sRGBEncoding;

// Render the scene
renderer.render(scene, camera);
```

### WebGPURenderer

Next-generation renderer using WebGPU API (experimental, requires compatible browser).

```javascript
import WebGPU from 'three/addons/capabilities/WebGPU.js';
import WebGPURenderer from 'three/addons/renderers/webgpu/WebGPURenderer.js';

if (WebGPU.isAvailable()) {
    const renderer = new WebGPURenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Use with node-based materials
    await renderer.init();
} else {
    // Fallback to WebGL
    const renderer = new THREE.WebGLRenderer();
}
```

### CSS2DRenderer and CSS3DRenderer

Render HTML/CSS elements in 3D space alongside WebGL content.

```javascript
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { CSS3DRenderer, CSS3DObject } from 'three/addons/renderers/CSS3DRenderer.js';

// CSS2D (billboards, labels)
const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(window.innerWidth, window.innerHeight);
labelRenderer.domElement.style.position = 'absolute';
labelRenderer.domElement.style.top = '0';
document.body.appendChild(labelRenderer.domElement);

const labelDiv = document.createElement('div');
labelDiv.textContent = 'Label';
labelDiv.style.color = 'white';
const label = new CSS2DObject(labelDiv);
label.position.set(0, 1, 0);
scene.add(label);

// Render both
function animate() {
    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);
}

// CSS3D (transform3d for HTML elements)
const css3DRenderer = new CSS3DRenderer();
const div3D = document.createElement('div');
const object3D = new CSS3DObject(div3D);
scene.add(object3D);
```

## Geometries

Geometries define the shape and structure of 3D objects.

### BufferGeometry

Modern, efficient geometry class. All geometry in Three.js is now BufferGeometry-based.

```javascript
// Create custom geometry
const geometry = new THREE.BufferGeometry();

// Define vertices (positions)
const vertices = new Float32Array([
    -1.0, -1.0,  1.0,  // vertex 0
     1.0, -1.0,  1.0,  // vertex 1
     1.0,  1.0,  1.0,  // vertex 2
]);

geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

// Define normals for lighting
const normals = new Float32Array([...]);
geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));

// Define UVs for textures
const uvs = new Float32Array([...]);
geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));

// Define indices for faces
const indices = new Uint16Array([0, 1, 2, ...]);
geometry.setIndex(new THREE.BufferAttribute(indices, 1));

// Compute normals automatically
geometry.computeVertexNormals();

// Compute bounding box/sphere
geometry.computeBoundingBox();
geometry.computeBoundingSphere();
```

### Built-in Geometries

```javascript
// Box
const boxGeometry = new THREE.BoxGeometry(width, height, depth, widthSegments, heightSegments, depthSegments);

// Sphere
const sphereGeometry = new THREE.SphereGeometry(radius, widthSegments, heightSegments, phiStart, phiLength, thetaStart, thetaLength);

// Plane
const planeGeometry = new THREE.PlaneGeometry(width, height, widthSegments, heightSegments);

// Circle
const circleGeometry = new THREE.CircleGeometry(radius, segments, thetaStart, thetaLength);

// Cylinder
const cylinderGeometry = new THREE.CylinderGeometry(radiusTop, radiusBottom, height, radialSegments, heightSegments, openEnded);

// Cone
const coneGeometry = new THREE.ConeGeometry(radius, height, radialSegments, heightSegments, openEnded);

// Torus
const torusGeometry = new THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments, arc);

// Torus Knot
const torusKnotGeometry = new THREE.TorusKnotGeometry(radius, tube, tubularSegments, radialSegments, p, q);

// Ring
const ringGeometry = new THREE.RingGeometry(innerRadius, outerRadius, thetaSegments, phiSegments, thetaStart, thetaLength);

// Tube (along curve)
const path = new THREE.CatmullRomCurve3([...points]);
const tubeGeometry = new THREE.TubeGeometry(path, tubularSegments, radius, radialSegments, closed);

// Lathe (revolution surface)
const points = [new THREE.Vector2(0, 0), new THREE.Vector2(1, 1), ...];
const latheGeometry = new THREE.LatheGeometry(points, segments, phiStart, phiLength);

// Extrude (2D shape to 3D)
const shape = new THREE.Shape();
shape.moveTo(0, 0);
shape.lineTo(0, 1);
shape.lineTo(1, 1);
const extrudeGeometry = new THREE.ExtrudeGeometry(shape, {
    depth: 2,
    bevelEnabled: true,
    bevelThickness: 0.1,
    bevelSize: 0.1,
    bevelSegments: 3
});

// Text
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';

const loader = new FontLoader();
loader.load('fonts/helvetiker_regular.typeface.json', (font) => {
    const textGeometry = new TextGeometry('Hello Three.js', {
        font: font,
        size: 1,
        height: 0.2,
        curveSegments: 12,
        bevelEnabled: true,
        bevelThickness: 0.03,
        bevelSize: 0.02,
        bevelSegments: 5
    });
});

// Edges (wireframe edges only)
const edges = new THREE.EdgesGeometry(geometry, thresholdAngle);
const edgesMesh = new THREE.LineSegments(edges, lineMaterial);

// Wireframe
const wireframe = new THREE.WireframeGeometry(geometry);
const wireframeMesh = new THREE.LineSegments(wireframe, lineMaterial);
```

### Geometry Manipulation

```javascript
// Transform geometry
geometry.translate(x, y, z);
geometry.rotateX(angle);
geometry.rotateY(angle);
geometry.rotateZ(angle);
geometry.scale(x, y, z);

// Center geometry
geometry.center();

// Merge geometries
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
const mergedGeometry = mergeGeometries([geometry1, geometry2, geometry3]);

// Dispose when no longer needed
geometry.dispose();
```

## Materials

Materials define how geometry surfaces appear when rendered.

### Basic Materials

```javascript
// MeshBasicMaterial - unaffected by lights
const basicMaterial = new THREE.MeshBasicMaterial({
    color: 0xff0000,
    wireframe: false,
    transparent: false,
    opacity: 1.0,
    side: THREE.FrontSide, // FrontSide, BackSide, DoubleSide
    map: texture,
    alphaMap: alphaTexture,
    envMap: environmentMap
});

// MeshNormalMaterial - visualizes normals (debugging)
const normalMaterial = new THREE.MeshNormalMaterial();

// MeshDepthMaterial - renders based on depth
const depthMaterial = new THREE.MeshDepthMaterial();
```

### Lighting-based Materials

```javascript
// MeshLambertMaterial - non-shiny surfaces (matte)
const lambertMaterial = new THREE.MeshLambertMaterial({
    color: 0x00ff00,
    emissive: 0x000000,
    map: texture,
    emissiveMap: emissiveTexture,
    emissiveIntensity: 1.0
});

// MeshPhongMaterial - shiny surfaces with specular highlights
const phongMaterial = new THREE.MeshPhongMaterial({
    color: 0x0000ff,
    emissive: 0x000000,
    specular: 0x111111,
    shininess: 30,
    map: texture,
    specularMap: specularTexture,
    normalMap: normalTexture,
    bumpMap: bumpTexture,
    bumpScale: 1.0
});

// MeshStandardMaterial - PBR (physically based rendering)
const standardMaterial = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.5,      // 0 = smooth, 1 = rough
    metalness: 0.5,      // 0 = non-metal, 1 = metal
    map: baseColorTexture,
    roughnessMap: roughnessTexture,
    metalnessMap: metalnessTexture,
    normalMap: normalTexture,
    normalScale: new THREE.Vector2(1, 1),
    aoMap: aoTexture,
    aoMapIntensity: 1.0,
    emissive: 0x000000,
    emissiveMap: emissiveTexture,
    emissiveIntensity: 1.0,
    envMap: environmentMap,
    envMapIntensity: 1.0
});

// MeshPhysicalMaterial - advanced PBR with clearcoat, transmission
const physicalMaterial = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    roughness: 0.0,
    metalness: 0.0,
    transmission: 1.0,        // Glass-like transparency
    thickness: 0.5,           // Refraction thickness
    clearcoat: 1.0,           // Clear coat layer
    clearcoatRoughness: 0.1,
    ior: 1.5,                 // Index of refraction
    reflectivity: 0.5,
    sheen: 0.5,              // Fabric-like sheen
    sheenRoughness: 0.5,
    sheenColor: new THREE.Color(0xffffff)
});

// MeshToonMaterial - cartoon/cel shading
const toonMaterial = new THREE.MeshToonMaterial({
    color: 0xff6347,
    gradientMap: gradientTexture  // Custom toon ramp
});
```

### Special Materials

```javascript
// ShaderMaterial - custom GLSL shaders
const shaderMaterial = new THREE.ShaderMaterial({
    uniforms: {
        time: { value: 0 },
        color: { value: new THREE.Color(0xff0000) }
    },
    vertexShader: `
        varying vec2 vUv;
        void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `,
    fragmentShader: `
        uniform float time;
        uniform vec3 color;
        varying vec2 vUv;
        void main() {
            gl_FragColor = vec4(color * sin(time), 1.0);
        }
    `
});

// RawShaderMaterial - no built-in uniforms
const rawShaderMaterial = new THREE.RawShaderMaterial({
    vertexShader: `...`,
    fragmentShader: `...`
});

// PointsMaterial - for particle systems
const pointsMaterial = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.1,
    sizeAttenuation: true,  // Size affected by distance
    map: particleTexture,
    alphaMap: alphaTexture,
    transparent: true,
    opacity: 0.8,
    blending: THREE.AdditiveBlending
});

// LineMaterial - for lines
const lineMaterial = new THREE.LineBasicMaterial({
    color: 0xff0000,
    linewidth: 1  // Note: linewidth > 1 not supported by most platforms
});

// For wider lines, use LineGeometry with LineMaterial from addons
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { Line2 } from 'three/addons/lines/Line2.js';

const lineGeometry = new LineGeometry();
lineGeometry.setPositions([x1, y1, z1, x2, y2, z2, ...]);
const lineMaterial = new LineMaterial({
    color: 0xff0000,
    linewidth: 5  // Pixels
});
const line = new Line2(lineGeometry, lineMaterial);

// SpriteMaterial - 2D billboards always facing camera
const spriteMaterial = new THREE.SpriteMaterial({
    map: texture,
    color: 0xffffff,
    transparent: true
});
```

### Material Properties

```javascript
// Common properties
material.side = THREE.FrontSide;  // FrontSide, BackSide, DoubleSide
material.transparent = true;
material.opacity = 0.5;
material.visible = true;
material.depthTest = true;
material.depthWrite = true;
material.alphaTest = 0.5;  // Discard pixels below this alpha
material.blending = THREE.NormalBlending;  // NormalBlending, AdditiveBlending, etc.
material.needsUpdate = true;  // Mark for shader recompilation

// Dispose materials
material.dispose();
```

## Textures

Textures are images or data mapped onto geometry surfaces.

### Loading Textures

```javascript
const textureLoader = new THREE.TextureLoader();

// Simple load
const texture = textureLoader.load('path/to/texture.jpg');

// Load with callbacks
textureLoader.load(
    'texture.jpg',
    (texture) => {
        // Success
        console.log('Texture loaded');
    },
    (progress) => {
        // Progress
        console.log((progress.loaded / progress.total * 100) + '% loaded');
    },
    (error) => {
        // Error
        console.error('Error loading texture', error);
    }
);

// Apply to material
const material = new THREE.MeshStandardMaterial({
    map: texture
});
```

### Texture Properties

```javascript
// Wrapping
texture.wrapS = THREE.RepeatWrapping;  // Horizontal
texture.wrapT = THREE.RepeatWrapping;  // Vertical
// Options: RepeatWrapping, ClampToEdgeWrapping, MirroredRepeatWrapping

// Repeat and offset
texture.repeat.set(2, 2);  // Tile 2x2
texture.offset.set(0.5, 0.5);  // Offset by half

// Rotation
texture.rotation = Math.PI / 4;  // 45 degrees
texture.center.set(0.5, 0.5);    // Rotation center

// Filtering
texture.minFilter = THREE.LinearMipmapLinearFilter;
texture.magFilter = THREE.LinearFilter;
// minFilter: NearestFilter, LinearFilter, NearestMipmapNearestFilter, etc.
// magFilter: NearestFilter, LinearFilter

// Anisotropy (improves quality at angles)
texture.anisotropy = renderer.capabilities.getMaxAnisotropy();

// Encoding
texture.encoding = THREE.sRGBEncoding;  // For color textures
// LinearEncoding for data textures (normal maps, etc.)

// Update texture
texture.needsUpdate = true;

// Dispose
texture.dispose();
```

### Texture Types

```javascript
// Cube textures (environment maps)
const cubeTextureLoader = new THREE.CubeTextureLoader();
const envMap = cubeTextureLoader.load([
    'px.jpg', 'nx.jpg',  // Positive/negative X
    'py.jpg', 'ny.jpg',  // Positive/negative Y
    'pz.jpg', 'nz.jpg'   // Positive/negative Z
]);

// Data textures (procedural)
const size = 256;
const data = new Uint8Array(size * size * 3);
for (let i = 0; i < size * size; i++) {
    data[i * 3] = Math.random() * 255;     // R
    data[i * 3 + 1] = Math.random() * 255; // G
    data[i * 3 + 2] = Math.random() * 255; // B
}
const dataTexture = new THREE.DataTexture(data, size, size, THREE.RGBFormat);
dataTexture.needsUpdate = true;

// Canvas textures (dynamic)
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
canvas.width = 512;
canvas.height = 512;
ctx.fillStyle = '#ff0000';
ctx.fillRect(0, 0, 512, 512);

const canvasTexture = new THREE.CanvasTexture(canvas);
canvasTexture.needsUpdate = true;  // Update after canvas changes

// Video textures
const video = document.createElement('video');
video.src = 'video.mp4';
video.load();
video.play();
const videoTexture = new THREE.VideoTexture(video);

// Compressed textures (better performance)
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath('basis/');
ktx2Loader.detectSupport(renderer);
const compressedTexture = await ktx2Loader.loadAsync('texture.ktx2');
```

### Loading Manager

Manage multiple asset loads:

```javascript
const manager = new THREE.LoadingManager();

manager.onStart = (url, itemsLoaded, itemsTotal) => {
    console.log(`Started loading: ${url}`);
};

manager.onLoad = () => {
    console.log('All assets loaded');
};

manager.onProgress = (url, itemsLoaded, itemsTotal) => {
    console.log(`Loading: ${itemsLoaded}/${itemsTotal}`);
};

manager.onError = (url) => {
    console.error(`Error loading: ${url}`);
};

const textureLoader = new THREE.TextureLoader(manager);
const texture1 = textureLoader.load('texture1.jpg');
const texture2 = textureLoader.load('texture2.jpg');
```

## Lights

Lights illuminate objects in the scene.

### Light Types

```javascript
// AmbientLight - uniform lighting from all directions
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

// DirectionalLight - parallel rays (like sun)
const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
directionalLight.position.set(5, 10, 5);
directionalLight.castShadow = true;
scene.add(directionalLight);

// Shadow configuration
directionalLight.shadow.camera.left = -10;
directionalLight.shadow.camera.right = 10;
directionalLight.shadow.camera.top = 10;
directionalLight.shadow.camera.bottom = -10;
directionalLight.shadow.camera.near = 0.5;
directionalLight.shadow.camera.far = 50;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
directionalLight.shadow.bias = -0.0001;

// PointLight - emits in all directions from a point
const pointLight = new THREE.PointLight(0xff0000, 1.0, 100, 2);
// Parameters: color, intensity, distance, decay
pointLight.position.set(0, 5, 0);
pointLight.castShadow = true;
scene.add(pointLight);

// SpotLight - cone of light
const spotLight = new THREE.SpotLight(0xffffff, 1.0);
spotLight.position.set(0, 10, 0);
spotLight.angle = Math.PI / 6;  // Cone angle
spotLight.penumbra = 0.1;       // Soft edge (0-1)
spotLight.decay = 2;
spotLight.distance = 100;
spotLight.castShadow = true;
spotLight.target.position.set(0, 0, 0);
scene.add(spotLight);
scene.add(spotLight.target);

// HemisphereLight - gradient from sky to ground
const hemisphereLight = new THREE.HemisphereLight(
    0x0000ff,  // Sky color
    0x00ff00,  // Ground color
    0.5        // Intensity
);
scene.add(hemisphereLight);

// RectAreaLight - rectangular area light (no shadows)
import { RectAreaLight } from 'three';
import { RectAreaLightHelper } from 'three/addons/helpers/RectAreaLightHelper.js';

const rectLight = new RectAreaLight(0xffffff, 5, 10, 10);
rectLight.position.set(0, 5, 0);
rectLight.lookAt(0, 0, 0);
scene.add(rectLight);

const rectLightHelper = new RectAreaLightHelper(rectLight);
scene.add(rectLightHelper);
```

### Light Helpers

Visual debugging aids for lights:

```javascript
import {
    DirectionalLightHelper,
    PointLightHelper,
    SpotLightHelper,
    HemisphereLightHelper
} from 'three';

const dirLightHelper = new THREE.DirectionalLightHelper(directionalLight, 5);
scene.add(dirLightHelper);

const pointLightHelper = new THREE.PointLightHelper(pointLight, 1);
scene.add(pointLightHelper);

const spotLightHelper = new THREE.SpotLightHelper(spotLight);
scene.add(spotLightHelper);
spotLightHelper.update();  // Call after moving light

const hemiLightHelper = new THREE.HemisphereLightHelper(hemisphereLight, 5);
scene.add(hemiLightHelper);
```

### Shadow Configuration

```javascript
// Enable shadows on renderer
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
// Types: BasicShadowMap, PCFShadowMap, PCFSoftShadowMap, VSMShadowMap

// Enable casting/receiving on objects
mesh.castShadow = true;
mesh.receiveShadow = true;

// Light shadows
light.castShadow = true;
light.shadow.mapSize.width = 2048;
light.shadow.mapSize.height = 2048;
light.shadow.camera.near = 0.5;
light.shadow.camera.far = 500;
```

## Objects and Scene Graph

### Creating Objects

```javascript
// Mesh - geometry + material
const mesh = new THREE.Mesh(geometry, material);
mesh.position.set(0, 0, 0);
mesh.rotation.set(0, 0, 0);
mesh.scale.set(1, 1, 1);
scene.add(mesh);

// Points - particle system
const points = new THREE.Points(geometry, pointsMaterial);
scene.add(points);

// Line
const line = new THREE.Line(geometry, lineMaterial);
scene.add(line);

// LineSegments - disconnected line segments
const lineSegments = new THREE.LineSegments(geometry, lineMaterial);
scene.add(lineSegments);

// Sprite - 2D billboard
const sprite = new THREE.Sprite(spriteMaterial);
sprite.position.set(0, 1, 0);
sprite.scale.set(0.5, 0.5, 1);
scene.add(sprite);

// Group - container for multiple objects
const group = new THREE.Group();
group.add(mesh1);
group.add(mesh2);
scene.add(group);
```

### Object3D Hierarchy

```javascript
// Add/remove children
parent.add(child);
parent.remove(child);
parent.clear();  // Remove all children

// Traverse hierarchy
object.traverse((child) => {
    if (child.isMesh) {
        child.material.wireframe = true;
    }
});

// Find by name
const found = scene.getObjectByName('myObject');

// Find by property
const found = scene.getObjectByProperty('uuid', uuid);

// Parent/child relationships
const parent = child.parent;
const children = parent.children;
```

### Transformations

```javascript
// Position (Vector3)
object.position.set(x, y, z);
object.position.x = 5;
object.position.copy(otherPosition);
object.position.add(new THREE.Vector3(1, 0, 0));

// Rotation (Euler angles in radians)
object.rotation.set(x, y, z);
object.rotation.x = Math.PI / 4;
object.rotation.order = 'YXZ';  // Rotation order

// Quaternion rotation (more stable, no gimbal lock)
object.quaternion.setFromEuler(new THREE.Euler(x, y, z));
object.quaternion.multiply(otherQuaternion);

// Scale
object.scale.set(x, y, z);
object.scale.multiplyScalar(2);  // Uniform scale

// Look at target
object.lookAt(targetVector);
object.lookAt(x, y, z);

// Local vs. World transforms
object.getWorldPosition(targetVector);
object.getWorldQuaternion(targetQuaternion);
object.getWorldScale(targetVector);
object.getWorldDirection(targetVector);

// Translate in local space
object.translateX(distance);
object.translateY(distance);
object.translateZ(distance);
object.translateOnAxis(axis, distance);

// Update matrices
object.updateMatrix();
object.updateMatrixWorld();
object.updateWorldMatrix(updateParents, updateChildren);
```

### Object Properties

```javascript
// Visibility
object.visible = false;

// Rendering order
object.renderOrder = 1;  // Higher renders later

// Layers (for selective rendering)
object.layers.set(0);  // Layer 0
camera.layers.enable(0);  // Render layer 0

// User data
object.userData = { customData: 'value' };

// Raycasting
object.raycast = (raycaster, intersects) => { /* custom */ };

// Frustum culling
object.frustumCulled = true;

// Matrix auto-update
object.matrixAutoUpdate = false;  // Manual matrix control

// Dispose
object.geometry.dispose();
object.material.dispose();
```

## Animation

### Animation Loop

```javascript
// Basic loop
function animate() {
    requestAnimationFrame(animate);

    // Update logic
    mesh.rotation.y += 0.01;

    // Render
    renderer.render(scene, camera);
}
animate();

// Delta time for consistent animation
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();  // Seconds since last frame
    const elapsed = clock.getElapsedTime();  // Total elapsed time

    mesh.rotation.y += delta * 1;  // 1 radian per second

    renderer.render(scene, camera);
}
```

### Animation System (Skeletal Animation)

```javascript
// AnimationMixer - manages animations on objects
const mixer = new THREE.AnimationMixer(mesh);

// AnimationClip - keyframe data
const clip = THREE.AnimationClip.findByName(clips, 'Walk');

// AnimationAction - control playback
const action = mixer.clipAction(clip);
action.play();

// Update mixer in animation loop
function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    mixer.update(delta);

    renderer.render(scene, camera);
}

// Action control
action.play();
action.stop();
action.pause();
action.reset();
action.setLoop(THREE.LoopRepeat, Infinity);
action.setDuration(3);  // Override duration
action.timeScale = 2;   // Playback speed
action.weight = 0.5;    // Blend weight

// Blend between animations
action1.fadeOut(0.5);
action2.reset().fadeIn(0.5).play();

// Keyframe creation
const times = [0, 1, 2];
const values = [0, 0, 0,  1, 1, 1,  0, 0, 0];
const positionTrack = new THREE.VectorKeyframeTrack('.position', times, values);

const clip = new THREE.AnimationClip('Move', 2, [positionTrack]);
```

### Morph Targets (Blend Shapes)

```javascript
// Geometry with morph targets
geometry.morphAttributes.position = [
    new THREE.Float32BufferAttribute([...], 3),  // Target 1
    new THREE.Float32BufferAttribute([...], 3)   // Target 2
];

// Control influence
mesh.morphTargetInfluences[0] = 0.5;  // 50% of target 1

// Animate morph targets
function animate() {
    mesh.morphTargetInfluences[0] = Math.sin(Date.now() * 0.001) * 0.5 + 0.5;
    renderer.render(scene, camera);
}
```

### Tween Libraries Integration

```javascript
// Example with GSAP
import gsap from 'gsap';

gsap.to(mesh.position, {
    x: 5,
    duration: 2,
    ease: 'power2.inOut',
    onComplete: () => console.log('Done')
});

// Example with Tween.js
import TWEEN from '@tweenjs/tween.js';

new TWEEN.Tween(mesh.position)
    .to({ x: 5, y: 2 }, 2000)
    .easing(TWEEN.Easing.Quadratic.InOut)
    .start();

function animate() {
    requestAnimationFrame(animate);
    TWEEN.update();
    renderer.render(scene, camera);
}
```

## Loaders

Loaders import external 3D assets and data.

### GLTF/GLB Loader (Recommended)

glTF is the recommended format for 3D models (compact, feature-rich, industry standard).

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const loader = new GLTFLoader();

loader.load(
    'model.gltf',  // or 'model.glb'
    (gltf) => {
        const model = gltf.scene;
        scene.add(model);

        // Access animations
        const mixer = new THREE.AnimationMixer(model);
        gltf.animations.forEach((clip) => {
            mixer.clipAction(clip).play();
        });

        // Access cameras
        const camera = gltf.cameras[0];

        // Traverse model
        model.traverse((child) => {
            if (child.isMesh) {
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });
    },
    (progress) => {
        console.log((progress.loaded / progress.total * 100) + '% loaded');
    },
    (error) => {
        console.error('Error loading model', error);
    }
);
```

### Draco Compression (for GLTF)

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('draco/');  // Path to decoder files
dracoLoader.setDecoderConfig({ type: 'js' });  // or 'wasm'

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

gltfLoader.load('compressed-model.glb', (gltf) => {
    scene.add(gltf.scene);
});
```

### Other Loaders

```javascript
// OBJ Loader
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
const objLoader = new OBJLoader();
objLoader.load('model.obj', (obj) => scene.add(obj));

// FBX Loader
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
const fbxLoader = new FBXLoader();
fbxLoader.load('model.fbx', (fbx) => scene.add(fbx));

// Collada Loader
import { ColladaLoader } from 'three/addons/loaders/ColladaLoader.js';
const colladaLoader = new ColladaLoader();
colladaLoader.load('model.dae', (collada) => scene.add(collada.scene));

// STL Loader
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
const stlLoader = new STLLoader();
stlLoader.load('model.stl', (geometry) => {
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
});

// PLY Loader
import { PLYLoader } from 'three/addons/loaders/PLYLoader.js';
const plyLoader = new PLYLoader();
plyLoader.load('model.ply', (geometry) => {
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
});

// SVG Loader
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';
const svgLoader = new SVGLoader();
svgLoader.load('image.svg', (data) => {
    const paths = data.paths;
    const group = new THREE.Group();

    paths.forEach((path) => {
        const shapes = SVGLoader.createShapes(path);
        shapes.forEach((shape) => {
            const geometry = new THREE.ShapeGeometry(shape);
            const mesh = new THREE.Mesh(geometry, material);
            group.add(mesh);
        });
    });

    scene.add(group);
});

// HDR Loader (environment maps)
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
const rgbeLoader = new RGBELoader();
rgbeLoader.load('environment.hdr', (texture) => {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    scene.environment = texture;
    scene.background = texture;
});

// EXR Loader
import { EXRLoader } from 'three/addons/loaders/EXRLoader.js';
const exrLoader = new EXRLoader();
exrLoader.load('texture.exr', (texture) => {
    material.map = texture;
});
```

## Controls (Addons)

Interactive camera controls for user interaction.

### OrbitControls

Most common - orbit around a target point.

```javascript
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const controls = new OrbitControls(camera, renderer.domElement);

// Target point (what camera orbits around)
controls.target.set(0, 0, 0);

// Damping (smooth movement)
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Zoom
controls.enableZoom = true;
controls.zoomSpeed = 1.0;
controls.minDistance = 1;
controls.maxDistance = 100;

// Rotation
controls.enableRotate = true;
controls.rotateSpeed = 1.0;
controls.minPolarAngle = 0;  // Radians
controls.maxPolarAngle = Math.PI;
controls.minAzimuthAngle = -Infinity;
controls.maxAzimuthAngle = Infinity;

// Pan
controls.enablePan = true;
controls.panSpeed = 1.0;
controls.screenSpacePanning = false;  // Pan in world space

// Auto rotate
controls.autoRotate = true;
controls.autoRotateSpeed = 2.0;

// Update in animation loop (required if damping enabled)
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// Events
controls.addEventListener('change', () => {
    renderer.render(scene, camera);
});

controls.addEventListener('start', () => console.log('User interaction started'));
controls.addEventListener('end', () => console.log('User interaction ended'));

// Methods
controls.saveState();  // Save current state
controls.reset();      // Reset to saved state
controls.dispose();    // Cleanup
```

### Other Control Types

```javascript
// TrackballControls - free rotation (no up vector constraints)
import { TrackballControls } from 'three/addons/controls/TrackballControls.js';
const trackballControls = new TrackballControls(camera, renderer.domElement);
trackballControls.rotateSpeed = 1.0;
trackballControls.zoomSpeed = 1.2;
trackballControls.panSpeed = 0.8;
trackballControls.staticMoving = true;
trackballControls.dynamicDampingFactor = 0.3;

// FlyControls - flight simulator style
import { FlyControls } from 'three/addons/controls/FlyControls.js';
const flyControls = new FlyControls(camera, renderer.domElement);
flyControls.movementSpeed = 10;
flyControls.rollSpeed = Math.PI / 24;
flyControls.autoForward = false;
flyControls.dragToLook = true;

// Update with delta
const clock = new THREE.Clock();
function animate() {
    const delta = clock.getDelta();
    flyControls.update(delta);
    renderer.render(scene, camera);
}

// FirstPersonControls - FPS style
import { FirstPersonControls } from 'three/addons/controls/FirstPersonControls.js';
const fpControls = new FirstPersonControls(camera, renderer.domElement);
fpControls.movementSpeed = 10;
fpControls.lookSpeed = 0.1;
fpControls.lookVertical = true;

// PointerLockControls - FPS with mouse lock
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
const pointerControls = new PointerLockControls(camera, renderer.domElement);

document.addEventListener('click', () => {
    pointerControls.lock();
});

pointerControls.addEventListener('lock', () => {
    console.log('Pointer locked');
});

pointerControls.addEventListener('unlock', () => {
    console.log('Pointer unlocked');
});

scene.add(pointerControls.getObject());

// Movement with keyboard
const velocity = new THREE.Vector3();
const direction = new THREE.Vector3();

document.addEventListener('keydown', (event) => {
    switch (event.code) {
        case 'KeyW': moveForward = true; break;
        case 'KeyS': moveBackward = true; break;
        case 'KeyA': moveLeft = true; break;
        case 'KeyD': moveRight = true; break;
    }
});

// MapControls - like OrbitControls but for top-down views
import { MapControls } from 'three/addons/controls/MapControls.js';
const mapControls = new MapControls(camera, renderer.domElement);

// TransformControls - gizmo for object manipulation
import { TransformControls } from 'three/addons/controls/TransformControls.js';
const transformControls = new TransformControls(camera, renderer.domElement);
transformControls.attach(mesh);
transformControls.setMode('translate');  // 'translate', 'rotate', 'scale'
scene.add(transformControls);

transformControls.addEventListener('change', () => {
    renderer.render(scene, camera);
});

transformControls.addEventListener('dragging-changed', (event) => {
    orbitControls.enabled = !event.value;  // Disable orbit during transform
});

// ArcballControls - trackball-like with better touch support
import { ArcballControls } from 'three/addons/controls/ArcballControls.js';
const arcballControls = new ArcballControls(camera, renderer.domElement, scene);
arcballControls.setGizmosVisible(false);
```

## Helpers

Visual debugging aids for development.

```javascript
// AxesHelper - XYZ axes (red=X, green=Y, blue=Z)
const axesHelper = new THREE.AxesHelper(5);  // Size
scene.add(axesHelper);

// GridHelper - ground grid
const gridHelper = new THREE.GridHelper(10, 10);  // Size, divisions
scene.add(gridHelper);

// BoxHelper - bounding box of object
const boxHelper = new THREE.BoxHelper(mesh, 0xffff00);
scene.add(boxHelper);
boxHelper.update();  // Call after object changes

// Box3Helper - from Box3
const box = new THREE.Box3().setFromObject(mesh);
const box3Helper = new THREE.Box3Helper(box, 0xffff00);
scene.add(box3Helper);

// CameraHelper - visualize camera frustum
const cameraHelper = new THREE.CameraHelper(camera);
scene.add(cameraHelper);

// PlaneHelper - visualize plane
const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
const planeHelper = new THREE.PlaneHelper(plane, 5, 0xffff00);
scene.add(planeHelper);

// ArrowHelper - directional arrow
const dir = new THREE.Vector3(1, 0, 0).normalize();
const origin = new THREE.Vector3(0, 0, 0);
const length = 1;
const arrowHelper = new THREE.ArrowHelper(dir, origin, length, 0xff0000);
scene.add(arrowHelper);

// SkeletonHelper - visualize skeleton
const skeletonHelper = new THREE.SkeletonHelper(mesh);
scene.add(skeletonHelper);

// VertexNormalsHelper - visualize vertex normals
import { VertexNormalsHelper } from 'three/addons/helpers/VertexNormalsHelper.js';
const normalsHelper = new VertexNormalsHelper(mesh, 0.5, 0xff0000);
scene.add(normalsHelper);

// PolarGridHelper - polar grid
const polarGrid = new THREE.PolarGridHelper(10, 16, 8, 64);
scene.add(polarGrid);
```

## Math Utilities

### Vector2

```javascript
const vec2 = new THREE.Vector2(x, y);

vec2.set(x, y);
vec2.setX(x);
vec2.setY(y);
vec2.add(otherVec2);
vec2.sub(otherVec2);
vec2.multiply(otherVec2);
vec2.multiplyScalar(scalar);
vec2.length();
vec2.lengthSq();
vec2.normalize();
vec2.dot(otherVec2);
vec2.cross(otherVec2);
vec2.distanceTo(otherVec2);
vec2.angle();
vec2.lerp(otherVec2, alpha);
vec2.clone();
vec2.copy(otherVec2);
```

### Vector3

```javascript
const vec3 = new THREE.Vector3(x, y, z);

vec3.set(x, y, z);
vec3.add(otherVec3);
vec3.sub(otherVec3);
vec3.multiply(otherVec3);
vec3.multiplyScalar(scalar);
vec3.divide(otherVec3);
vec3.divideScalar(scalar);
vec3.length();
vec3.lengthSq();
vec3.normalize();
vec3.dot(otherVec3);
vec3.cross(otherVec3);
vec3.distanceTo(otherVec3);
vec3.distanceToSquared(otherVec3);
vec3.lerp(otherVec3, alpha);
vec3.applyMatrix4(matrix);
vec3.applyQuaternion(quaternion);
vec3.project(camera);  // World to NDC
vec3.unproject(camera);  // NDC to world
vec3.transformDirection(matrix);
vec3.angleTo(otherVec3);
vec3.clamp(minVec, maxVec);
vec3.clone();
vec3.copy(otherVec3);
```

### Matrix4

```javascript
const mat4 = new THREE.Matrix4();

mat4.set(n11, n12, n13, n14, n21, n22, ...);
mat4.identity();
mat4.clone();
mat4.copy(otherMat);
mat4.multiply(otherMat);
mat4.premultiply(otherMat);
mat4.invert();
mat4.transpose();
mat4.determinant();
mat4.compose(position, quaternion, scale);
mat4.decompose(position, quaternion, scale);
mat4.makeTranslation(x, y, z);
mat4.makeRotationX(theta);
mat4.makeRotationY(theta);
mat4.makeRotationZ(theta);
mat4.makeRotationAxis(axis, angle);
mat4.makeScale(x, y, z);
mat4.lookAt(eye, target, up);
mat4.makePerspective(left, right, top, bottom, near, far);
mat4.makeOrthographic(left, right, top, bottom, near, far);
```

### Quaternion

```javascript
const quat = new THREE.Quaternion(x, y, z, w);

quat.set(x, y, z, w);
quat.setFromEuler(euler);
quat.setFromAxisAngle(axis, angle);
quat.setFromRotationMatrix(matrix);
quat.multiply(otherQuat);
quat.premultiply(otherQuat);
quat.invert();
quat.normalize();
quat.slerp(otherQuat, alpha);  // Spherical interpolation
quat.angleTo(otherQuat);
quat.rotateTowards(otherQuat, step);
quat.clone();
quat.copy(otherQuat);
```

### Euler

```javascript
const euler = new THREE.Euler(x, y, z, order);

euler.set(x, y, z, order);
euler.order = 'XYZ';  // XYZ, YZX, ZXY, XZY, YXZ, ZYX
euler.setFromQuaternion(quat);
euler.setFromRotationMatrix(matrix);
euler.setFromVector3(vector);
euler.clone();
euler.copy(otherEuler);
```

### Color

```javascript
const color = new THREE.Color(0xff0000);

// Creation
new THREE.Color(r, g, b);  // 0-1
new THREE.Color(0xff0000);  // Hex
new THREE.Color('#ff0000');  // String
new THREE.Color('red');  // CSS name
new THREE.Color('rgb(255, 0, 0)');
new THREE.Color('hsl(0, 100%, 50%)');

// Manipulation
color.set(0x00ff00);
color.setHex(0x00ff00);
color.setRGB(r, g, b);
color.setHSL(h, s, l);
color.setStyle('rgb(0, 255, 0)');
color.add(otherColor);
color.multiply(otherColor);
color.multiplyScalar(scalar);
color.lerp(otherColor, alpha);
color.getHex();
color.getHexString();
color.getStyle();
color.clone();
color.copy(otherColor);
```

### MathUtils

```javascript
// Utilities
THREE.MathUtils.clamp(value, min, max);
THREE.MathUtils.degToRad(degrees);
THREE.MathUtils.radToDeg(radians);
THREE.MathUtils.isPowerOfTwo(value);
THREE.MathUtils.ceilPowerOfTwo(value);
THREE.MathUtils.floorPowerOfTwo(value);
THREE.MathUtils.lerp(start, end, alpha);
THREE.MathUtils.smoothstep(x, min, max);
THREE.MathUtils.smootherstep(x, min, max);
THREE.MathUtils.randInt(low, high);
THREE.MathUtils.randFloat(low, high);
THREE.MathUtils.randFloatSpread(range);
THREE.MathUtils.seededRandom(seed);
THREE.MathUtils.mapLinear(x, a1, a2, b1, b2);
THREE.MathUtils.pingpong(x, length);
```

### Raycasting

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

// Mouse coordinates to normalized device coordinates (-1 to +1)
function onMouseMove(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
}

// Update raycaster
raycaster.setFromCamera(mouse, camera);

// Find intersections
const intersects = raycaster.intersectObjects(scene.children, recursive);

if (intersects.length > 0) {
    const intersection = intersects[0];
    console.log('Hit:', intersection.object);
    console.log('Point:', intersection.point);
    console.log('Distance:', intersection.distance);
    console.log('Face:', intersection.face);
    console.log('UV:', intersection.uv);
}

// Raycaster properties
raycaster.near = 0.1;
raycaster.far = 1000;
raycaster.params.Points.threshold = 0.1;
raycaster.params.Line.threshold = 1;

// Ray from specific point/direction
raycaster.set(origin, direction);
const intersects = raycaster.intersectObject(object, recursive);
```

## Audio

Three.js provides spatial audio capabilities.

### Basic Audio

```javascript
// Audio listener (attach to camera)
const listener = new THREE.AudioListener();
camera.add(listener);

// Audio loader
const audioLoader = new THREE.AudioLoader();

// Non-positional audio
const sound = new THREE.Audio(listener);
audioLoader.load('sound.mp3', (buffer) => {
    sound.setBuffer(buffer);
    sound.setLoop(true);
    sound.setVolume(0.5);
    sound.play();
});

// Control
sound.play();
sound.pause();
sound.stop();
sound.setVolume(0.8);
sound.setPlaybackRate(1.5);

// Check if playing
if (sound.isPlaying) {
    console.log('Audio playing');
}
```

### Positional Audio

```javascript
// 3D spatial audio (changes based on position)
const positionalSound = new THREE.PositionalAudio(listener);

audioLoader.load('ambient.mp3', (buffer) => {
    positionalSound.setBuffer(buffer);
    positionalSound.setRefDistance(20);  // Reference distance
    positionalSound.setLoop(true);
    positionalSound.setVolume(1);
    positionalSound.play();
});

// Attach to object
mesh.add(positionalSound);

// Distance models
positionalSound.setDistanceModel('linear');  // linear, inverse, exponential
positionalSound.setMaxDistance(100);
positionalSound.setRolloffFactor(1);

// Directional cone
positionalSound.setDirectionalCone(innerAngle, outerAngle, outerGain);
```

### Audio Analyzer

```javascript
// Frequency analysis
const sound = new THREE.Audio(listener);
const analyzer = new THREE.AudioAnalyser(sound, fftSize);

audioLoader.load('music.mp3', (buffer) => {
    sound.setBuffer(buffer);
    sound.play();
});

// In animation loop
function animate() {
    const data = analyzer.getFrequencyData();
    const average = analyzer.getAverageFrequency();

    // Use data for visualization
    mesh.scale.y = average / 50;

    renderer.render(scene, camera);
}
```

## Nodes (WebGPU Node Material System)

Node-based material system for WebGPU renderer, providing visual shader programming.

### NodeMaterial Basics

```javascript
import { MeshStandardNodeMaterial } from 'three/nodes';
import { color, texture, uv, normalMap } from 'three/nodes';

// Create node material
const material = new MeshStandardNodeMaterial();

// Set color using node
material.colorNode = color(0xff0000);

// Texture mapping
const textureNode = texture(diffuseTexture);
material.colorNode = textureNode;

// UV manipulation
material.colorNode = texture(diffuseTexture, uv().mul(2));  // Tile 2x

// Normal mapping
material.normalNode = normalMap(texture(normalTexture));
```

### Node Operations

```javascript
import {
    add, sub, mul, div,
    sin, cos, pow, sqrt,
    vec2, vec3, vec4,
    float, color,
    uv, position, normal,
    time, modelWorldMatrix
} from 'three/nodes';

// Math operations
const node = add(float(1), float(2));
const node = mul(uv(), 2);
const node = sin(add(position.y, time));

// Vector operations
const uvScaled = uv().mul(vec2(2, 1));
const animated = position.add(normal.mul(sin(time)));

// Color manipulation
const tintedColor = mul(texture(tex), color(0xff00ff));
const brightened = add(texture(tex), float(0.2));
```

### Custom Node Materials

```javascript
import { NodeMaterial } from 'three/nodes';
import { uniform, varying, attribute } from 'three/nodes';

const customMaterial = new NodeMaterial();

// Custom uniforms
const timeUniform = uniform(0);
const colorUniform = uniform(new THREE.Color(0xff0000));

// Vertex shader nodes
customMaterial.vertexNode = position.add(
    normal.mul(sin(add(position.y, timeUniform)))
);

// Fragment shader nodes
customMaterial.colorNode = mul(
    colorUniform,
    sin(time)
);

// Update uniforms
function animate() {
    timeUniform.value = performance.now() * 0.001;
    renderer.render(scene, camera);
}
```

## Post-Processing Effects

Visual effects applied after rendering.

### EffectComposer Setup

```javascript
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';

// Create composer
const composer = new EffectComposer(renderer);

// Add render pass (base scene render)
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

// Render with composer instead of renderer
function animate() {
    requestAnimationFrame(animate);
    composer.render();
}

// Handle resize
window.addEventListener('resize', () => {
    composer.setSize(window.innerWidth, window.innerHeight);
});
```

### Common Passes

```javascript
// Bloom
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    1.5,  // Strength
    0.4,  // Radius
    0.85  // Threshold
);
composer.addPass(bloomPass);

// Outline
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';
const outlinePass = new OutlinePass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    scene,
    camera
);
outlinePass.selectedObjects = [mesh];
outlinePass.edgeStrength = 3;
outlinePass.edgeGlow = 1;
outlinePass.edgeThickness = 2;
outlinePass.visibleEdgeColor.set(0xffffff);
composer.addPass(outlinePass);

// FXAA (antialiasing)
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';
const fxaaPass = new ShaderPass(FXAAShader);
fxaaPass.material.uniforms['resolution'].value.x = 1 / window.innerWidth;
fxaaPass.material.uniforms['resolution'].value.y = 1 / window.innerHeight;
composer.addPass(fxaaPass);

// SMAA (better antialiasing)
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
const smaaPass = new SMAAPass(window.innerWidth, window.innerHeight);
composer.addPass(smaaPass);

// TAA (temporal antialiasing)
import { TAAPass } from 'three/addons/postprocessing/TAAPass.js';
const taaPass = new TAAPass(scene, camera);
composer.addPass(taaPass);

// SSAOPass (ambient occlusion)
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';
const ssaoPass = new SSAOPass(scene, camera, width, height);
ssaoPass.kernelRadius = 16;
ssaoPass.minDistance = 0.005;
ssaoPass.maxDistance = 0.1;
composer.addPass(ssaoPass);

// SSRPass (screen space reflections)
import { SSRPass } from 'three/addons/postprocessing/SSRPass.js';
const ssrPass = new SSRPass({ renderer, scene, camera });
composer.addPass(ssrPass);

// Glitch
import { GlitchPass } from 'three/addons/postprocessing/GlitchPass.js';
const glitchPass = new GlitchPass();
composer.addPass(glitchPass);

// Film grain
import { FilmPass } from 'three/addons/postprocessing/FilmPass.js';
const filmPass = new FilmPass(0.35, 0.5, 2048, false);
composer.addPass(filmPass);

// Pixelation
import { PixelPass } from 'three/addons/postprocessing/PixelPass.js';
const pixelPass = new PixelPass(4);
composer.addPass(pixelPass);

// Bokeh (depth of field)
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
const bokehPass = new BokehPass(scene, camera, {
    focus: 10.0,
    aperture: 0.025,
    maxblur: 0.01
});
composer.addPass(bokehPass);

// Custom shader pass
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
const customShader = {
    uniforms: {
        'tDiffuse': { value: null },
        'amount': { value: 0.5 }
    },
    vertexShader: `
        varying vec2 vUv;
        void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `,
    fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform float amount;
        varying vec2 vUv;
        void main() {
            vec4 color = texture2D(tDiffuse, vUv);
            gl_FragColor = color * amount;
        }
    `
};
const customPass = new ShaderPass(customShader);
customPass.renderToScreen = true;  // Last pass
composer.addPass(customPass);
```

## CSM (Cascaded Shadow Maps)

Improved shadow quality for large scenes using multiple shadow cascades.

```javascript
import { CSM } from 'three/addons/csm/CSM.js';
import { CSMHelper } from 'three/addons/csm/CSMHelper.js';

// Setup CSM
const csm = new CSM({
    maxFar: camera.far,
    cascades: 4,  // Number of cascades
    mode: 'practical',  // 'uniform', 'logarithmic', 'practical', 'custom'
    parent: scene,
    shadowMapSize: 2048,
    lightDirection: new THREE.Vector3(1, -1, 1).normalize(),
    camera: camera
});

// Update materials to use CSM
mesh.castShadow = true;
mesh.receiveShadow = true;
csm.setupMaterial(mesh.material);

// Update in animation loop
function animate() {
    requestAnimationFrame(animate);
    csm.update();
    renderer.render(scene, camera);
}

// Visualize cascades (debugging)
const csmHelper = new CSMHelper(csm);
scene.add(csmHelper);
```

## Physics Integration

Three.js doesn't include physics, but integrates well with physics engines.

### Recommended Physics Libraries

**Cannon.js / Cannon-es**: Popular JavaScript physics engine

```javascript
// Example with cannon-es
import * as CANNON from 'cannon-es';

// Physics world
const world = new CANNON.World();
world.gravity.set(0, -9.82, 0);

// Physics body
const shape = new CANNON.Box(new CANNON.Vec3(1, 1, 1));
const body = new CANNON.Body({ mass: 1, shape });
body.position.set(0, 10, 0);
world.addBody(body);

// Three.js mesh
const geometry = new THREE.BoxGeometry(2, 2, 2);
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);

// Update loop
function animate() {
    requestAnimationFrame(animate);

    world.step(1/60);

    // Sync Three.js mesh with physics body
    mesh.position.copy(body.position);
    mesh.quaternion.copy(body.quaternion);

    renderer.render(scene, camera);
}
```

**Ammo.js**: Port of Bullet physics engine (more features, larger)

**Oimo.js**: Lightweight physics engine

**Rapier**: High-performance Rust-based physics (via WASM)

## Performance Optimization

### General Best Practices

```javascript
// Reuse geometries and materials
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });

for (let i = 0; i < 100; i++) {
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.x = i;
    scene.add(mesh);
}

// Dispose unused resources
geometry.dispose();
material.dispose();
texture.dispose();
renderer.dispose();

// Use InstancedMesh for many identical objects
const instancedMesh = new THREE.InstancedMesh(geometry, material, count);
scene.add(instancedMesh);

const matrix = new THREE.Matrix4();
for (let i = 0; i < count; i++) {
    matrix.setPosition(i, 0, 0);
    instancedMesh.setMatrixAt(i, matrix);
}
instancedMesh.instanceMatrix.needsUpdate = true;

// LOD (Level of Detail)
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);
lod.addLevel(mediumDetailMesh, 50);
lod.addLevel(lowDetailMesh, 100);
scene.add(lod);

// Frustum culling (automatic, but can disable if needed)
mesh.frustumCulled = true;

// Reduce shadow map size if needed
renderer.shadowMap.type = THREE.PCFShadowMap;  // Instead of PCFSoftShadowMap

// Use lower precision for mobile
const renderer = new THREE.WebGLRenderer({ precision: 'mediump' });

// Render on demand (not continuous)
function render() {
    renderer.render(scene, camera);
}
controls.addEventListener('change', render);
render();

// Monitor performance
const stats = renderer.info;
console.log('Triangles:', stats.render.triangles);
console.log('Draw calls:', stats.render.calls);
console.log('Geometries:', stats.memory.geometries);
console.log('Textures:', stats.memory.textures);
```

### Stats Monitoring

```javascript
import Stats from 'three/addons/libs/stats.module.js';

const stats = new Stats();
stats.showPanel(0);  // 0: fps, 1: ms, 2: mb
document.body.appendChild(stats.dom);

function animate() {
    stats.begin();

    // Your rendering code
    renderer.render(scene, camera);

    stats.end();
}
```

## Common Patterns and Workflows

### Responsive Canvas

```javascript
function handleResize() {
    const width = window.innerWidth;
    const height = window.innerHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    if (composer) {
        composer.setSize(width, height);
    }
}

window.addEventListener('resize', handleResize);
```

### Object Picking

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onMouseClick(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);

    if (intersects.length > 0) {
        const object = intersects[0].object;
        object.material.color.set(0xff0000);
    }
}

window.addEventListener('click', onMouseClick);
```

### Loading Screen

```javascript
const manager = new THREE.LoadingManager();

manager.onStart = () => {
    document.getElementById('loading').style.display = 'block';
};

manager.onLoad = () => {
    document.getElementById('loading').style.display = 'none';
};

manager.onProgress = (url, loaded, total) => {
    const progress = (loaded / total) * 100;
    document.getElementById('progress').textContent = `${progress.toFixed(0)}%`;
};

const loader = new GLTFLoader(manager);
```

## Resources and References

### Official Documentation

- **Main Documentation**: https://threejs.org/docs/
- **Examples**: https://threejs.org/examples/
- **Manual**: https://threejs.org/manual/
- **GitHub**: https://github.com/mrdoob/three.js

### Reference Files

For detailed API references and examples, see:

- `references/api_core.md` - Core classes (Scene, Object3D, etc.)
- `references/api_cameras.md` - Camera types and properties
- `references/api_geometries.md` - All geometry types
- `references/api_materials.md` - Material types and properties
- `references/api_lights.md` - Light types and shadows
- `references/api_loaders.md` - Model and texture loaders
- `references/api_addons.md` - Controls, effects, utilities
- `references/examples.md` - Complete working examples

### Version Information

This skill is based on Three.js r181 (latest stable as of documentation). Always check the official documentation for the most current API changes and deprecations.

## Implementation Workflow

When implementing Three.js features:

1. **Setup**: Initialize scene, camera, renderer, and animation loop
2. **Assets**: Load models, textures, and other resources with appropriate loaders
3. **Scene Construction**: Create geometry, materials, meshes, lights, and add to scene
4. **Interaction**: Implement controls, raycasting, and user input handlers
5. **Animation**: Set up animation loop with proper timing and updates
6. **Optimization**: Profile performance, reduce draw calls, implement LOD, use instancing
7. **Effects**: Add post-processing effects if needed
8. **Responsive**: Handle window resize and different devices
9. **Cleanup**: Dispose resources when no longer needed to prevent memory leaks

Always consider performance implications, especially for mobile devices, and test across different browsers and hardware capabilities.
