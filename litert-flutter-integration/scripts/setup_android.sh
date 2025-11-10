#!/bin/bash
# setup_android.sh
# Automated Android project configuration for LiteRT Flutter integration

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}LiteRT Flutter Integration - Android Setup${NC}"
echo "=========================================="
echo

# Check if we're in a Flutter project
if [ ! -f "pubspec.yaml" ]; then
    echo -e "${RED}Error: pubspec.yaml not found. Please run this script from the Flutter project root.${NC}"
    exit 1
fi

# Check if android directory exists
if [ ! -d "android" ]; then
    echo -e "${RED}Error: android directory not found.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Configuring Gradle dependencies...${NC}"

# Backup build.gradle
cp android/app/build.gradle android/app/build.gradle.backup
echo "Backed up android/app/build.gradle"

# Add LiteRT dependencies
cat >> android/app/build.gradle << 'EOF'

// LiteRT dependencies added by setup script
dependencies {
    // LiteRT Next (v2) - Alpha
    implementation 'com.google.ai.edge.litert:litert:2.0.0-alpha'

    // OR use stable LiteRT v1 (uncomment below and comment above)
    // implementation 'com.google.ai.edge.litert:litert:1.2.0'

    // Support library for preprocessing
    implementation 'com.google.ai.edge.litert:litert-support:0.4.4'

    // GPU acceleration
    implementation 'com.google.ai.edge.litert:litert-gpu:2.14.0'

    // Kotlin coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
}
EOF

echo -e "${GREEN}✓ Added LiteRT dependencies to build.gradle${NC}"

# Update minSdk and compileSdk if needed
echo -e "${YELLOW}Step 2: Updating SDK versions...${NC}"

# Check and update android/app/build.gradle for SDK versions
sed -i.bak '/minSdk/c\        minSdk 24' android/app/build.gradle
sed -i.bak '/compileSdk/c\    compileSdk 34' android/app/build.gradle

echo -e "${GREEN}✓ Updated minSdk to 24 and compileSdk to 34${NC}"

# Create assets directory if it doesn't exist
echo -e "${YELLOW}Step 3: Creating assets directory...${NC}"

mkdir -p android/app/src/main/assets
echo -e "${GREEN}✓ Created android/app/src/main/assets/${NC}"
echo "Place your .tflite model files here"

# Create Kotlin source directory structure
echo -e "${YELLOW}Step 4: Setting up Kotlin source structure...${NC}"

# Find the package name from AndroidManifest.xml
PACKAGE_NAME=$(grep -oP 'package="\K[^"]+' android/app/src/main/AndroidManifest.xml | head -1)

if [ -z "$PACKAGE_NAME" ]; then
    echo -e "${YELLOW}Warning: Could not detect package name. Using default 'com.example.app'${NC}"
    PACKAGE_NAME="com.example.app"
fi

# Create Kotlin package directories
KOTLIN_DIR="android/app/src/main/kotlin/${PACKAGE_NAME//.//}"
mkdir -p "$KOTLIN_DIR"

echo -e "${GREEN}✓ Created Kotlin source directory: $KOTLIN_DIR${NC}"

# Create template LiteRTInferenceHelper.kt
echo -e "${YELLOW}Step 5: Creating LiteRTInferenceHelper template...${NC}"

cat > "$KOTLIN_DIR/LiteRTInferenceHelper.kt" << 'EOF'
package PACKAGE_NAME_PLACEHOLDER

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
    private val inputSize = 640

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
        val inputBuffer = preprocessImage(bitmap)
        val outputBuffers = model.run(inputBuffer)
        return postprocessDetections(outputBuffers)
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
        // TODO: Implement postprocessing based on your model's output format
        return emptyList()
    }

    fun close() {
        model.close()
    }
}
EOF

# Replace package name placeholder
sed -i "s/PACKAGE_NAME_PLACEHOLDER/$PACKAGE_NAME/" "$KOTLIN_DIR/LiteRTInferenceHelper.kt"

echo -e "${GREEN}✓ Created LiteRTInferenceHelper.kt${NC}"

# Update MainActivity to support platform channels
echo -e "${YELLOW}Step 6: Checking MainActivity.kt...${NC}"

MAIN_ACTIVITY="$KOTLIN_DIR/MainActivity.kt"

if [ -f "$MAIN_ACTIVITY" ]; then
    echo "MainActivity.kt already exists. Please manually add platform channel code."
    echo "See the skill documentation for MainActivity implementation."
else
    echo -e "${YELLOW}MainActivity.kt not found at expected location.${NC}"
fi

# Create labels.txt template
echo -e "${YELLOW}Step 7: Creating labels template...${NC}"

cat > android/app/src/main/assets/labels.txt << 'EOF'
person
bicycle
car
motorcycle
airplane
bus
train
truck
boat
traffic light
EOF

echo -e "${GREEN}✓ Created labels.txt template${NC}"

# Summary
echo
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo -e "==========================================${NC}"
echo
echo "Next steps:"
echo "1. Place your .tflite model in: android/app/src/main/assets/"
echo "2. Update labels.txt with your model's class labels"
echo "3. Implement platform channel in MainActivity.kt"
echo "4. Customize LiteRTInferenceHelper.kt postprocessing"
echo "5. Run: flutter clean && flutter pub get"
echo "6. Build: flutter build apk"
echo
echo "Backup files created:"
echo "- android/app/build.gradle.backup"
echo
echo -e "${YELLOW}Note: Review all changes before committing!${NC}"
