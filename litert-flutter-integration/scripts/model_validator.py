#!/usr/bin/env python3
"""
model_validator.py
Validate TFLite model compatibility with LiteRT and mobile deployment
"""

import argparse
import sys
from pathlib import Path

try:
    import tensorflow as tf
    import numpy as np
except ImportError:
    print("Error: TensorFlow not installed. Install with: pip install tensorflow")
    sys.exit(1)


class TFLiteModelValidator:
    def __init__(self, model_path):
        self.model_path = Path(model_path)
        self.interpreter = None
        self.validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }

    def validate(self):
        """Run all validation checks"""
        print(f"Validating model: {self.model_path}")
        print("=" * 60)

        # Check file exists
        if not self.model_path.exists():
            self.validation_results['valid'] = False
            self.validation_results['errors'].append(
                f"Model file not found: {self.model_path}"
            )
            return self.validation_results

        # Check file size
        self._check_file_size()

        # Load model
        try:
            self.interpreter = tf.lite.Interpreter(model_path=str(self.model_path))
            self.interpreter.allocate_tensors()
        except Exception as e:
            self.validation_results['valid'] = False
            self.validation_results['errors'].append(f"Failed to load model: {e}")
            return self.validation_results

        # Run validation checks
        self._check_input_output()
        self._check_quantization()
        self._check_operations()
        self._check_memory_usage()
        self._check_mobile_compatibility()

        return self.validation_results

    def _check_file_size(self):
        """Check if model size is reasonable for mobile"""
        size_mb = self.model_path.stat().st_size / (1024 * 1024)
        self.validation_results['info']['size_mb'] = round(size_mb, 2)

        if size_mb > 100:
            self.validation_results['warnings'].append(
                f"Model size ({size_mb:.2f} MB) is large for mobile deployment. "
                "Consider using quantization."
            )
        elif size_mb > 50:
            self.validation_results['warnings'].append(
                f"Model size ({size_mb:.2f} MB) may impact app performance. "
                "Quantization recommended."
            )

        print(f"✓ Model size: {size_mb:.2f} MB")

    def _check_input_output(self):
        """Validate input and output tensors"""
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        print(f"\n✓ Input tensors: {len(input_details)}")
        for i, detail in enumerate(input_details):
            shape = detail['shape']
            dtype = detail['dtype']
            name = detail.get('name', f'input_{i}')

            print(f"  [{i}] {name}")
            print(f"      Shape: {shape}")
            print(f"      Type: {dtype}")

            # Check for dynamic shapes
            if -1 in shape:
                self.validation_results['warnings'].append(
                    f"Input tensor {i} has dynamic shape {shape}. "
                    "May not be optimized for mobile."
                )

            # Store info
            self.validation_results['info'][f'input_{i}_shape'] = shape.tolist()
            self.validation_results['info'][f'input_{i}_type'] = str(dtype)

        print(f"\n✓ Output tensors: {len(output_details)}")
        for i, detail in enumerate(output_details):
            shape = detail['shape']
            dtype = detail['dtype']
            name = detail.get('name', f'output_{i}')

            print(f"  [{i}] {name}")
            print(f"      Shape: {shape}")
            print(f"      Type: {dtype}")

            self.validation_results['info'][f'output_{i}_shape'] = shape.tolist()
            self.validation_results['info'][f'output_{i}_type'] = str(dtype)

    def _check_quantization(self):
        """Check quantization status"""
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        is_quantized = any(
            detail['dtype'] in [np.uint8, np.int8]
            for detail in input_details + output_details
        )

        self.validation_results['info']['quantized'] = is_quantized

        if is_quantized:
            print("\n✓ Model is quantized (INT8)")

            # Check quantization parameters
            for i, detail in enumerate(input_details):
                if 'quantization_parameters' in detail:
                    quant_params = detail['quantization_parameters']
                    scale = quant_params.get('scales', [None])[0]
                    zero_point = quant_params.get('zero_points', [None])[0]

                    if scale is not None and zero_point is not None:
                        print(f"  Input {i}: scale={scale:.6f}, zero_point={zero_point}")
        else:
            print("\n⚠ Model is NOT quantized (FP32/FP16)")
            self.validation_results['warnings'].append(
                "Model is not quantized. Consider INT8 quantization for better "
                "mobile performance (4x smaller, 2-4x faster)."
            )

    def _check_operations(self):
        """Check for unsupported operations"""
        try:
            # Get operation codes
            with open(self.model_path, 'rb') as f:
                model_content = f.read()

            # Check for SELECT_TF_OPS (indicates TF ops, not just TFLite ops)
            if b'FlexDelegate' in model_content:
                self.validation_results['warnings'].append(
                    "Model contains TensorFlow operations (SELECT_TF_OPS). "
                    "May have compatibility issues on some devices. "
                    "Consider using only TFLite built-in ops."
                )
                print("\n⚠ Model uses TensorFlow Select operations")
            else:
                print("\n✓ Model uses TFLite built-in operations only")

        except Exception as e:
            self.validation_results['warnings'].append(
                f"Could not check operations: {e}"
            )

    def _check_memory_usage(self):
        """Estimate memory usage"""
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        # Calculate input memory
        input_memory = 0
        for detail in input_details:
            shape = detail['shape']
            dtype = detail['dtype']
            num_elements = np.prod([s for s in shape if s > 0])
            bytes_per_element = np.dtype(dtype).itemsize
            input_memory += num_elements * bytes_per_element

        # Calculate output memory
        output_memory = 0
        for detail in output_details:
            shape = detail['shape']
            dtype = detail['dtype']
            num_elements = np.prod([s for s in shape if s > 0])
            bytes_per_element = np.dtype(dtype).itemsize
            output_memory += num_elements * bytes_per_element

        total_memory_mb = (input_memory + output_memory) / (1024 * 1024)

        self.validation_results['info']['estimated_memory_mb'] = round(total_memory_mb, 2)

        print(f"\n✓ Estimated memory usage: {total_memory_mb:.2f} MB")

        if total_memory_mb > 100:
            self.validation_results['warnings'].append(
                f"High memory usage ({total_memory_mb:.2f} MB). "
                "May cause OOM errors on low-end devices."
            )

    def _check_mobile_compatibility(self):
        """Check overall mobile compatibility"""
        print("\n" + "=" * 60)
        print("Mobile Compatibility Check")
        print("=" * 60)

        compatibility_score = 100

        # Deduct points for issues
        if not self.validation_results['info'].get('quantized', False):
            compatibility_score -= 20
            print("⚠ Not quantized: -20 points")

        size_mb = self.validation_results['info']['size_mb']
        if size_mb > 50:
            compatibility_score -= 15
            print(f"⚠ Large size ({size_mb:.2f} MB): -15 points")
        elif size_mb > 20:
            compatibility_score -= 5
            print(f"⚠ Medium size ({size_mb:.2f} MB): -5 points")

        memory_mb = self.validation_results['info'].get('estimated_memory_mb', 0)
        if memory_mb > 50:
            compatibility_score -= 10
            print(f"⚠ High memory ({memory_mb:.2f} MB): -10 points")

        # Check for warnings
        if len(self.validation_results['warnings']) > 0:
            compatibility_score -= len(self.validation_results['warnings']) * 5

        self.validation_results['info']['compatibility_score'] = max(0, compatibility_score)

        print(f"\nCompatibility Score: {compatibility_score}/100")

        if compatibility_score >= 90:
            print("✓ Excellent for mobile deployment")
        elif compatibility_score >= 70:
            print("✓ Good for mobile deployment with minor optimizations")
        elif compatibility_score >= 50:
            print("⚠ Fair - optimization recommended")
        else:
            print("⚠ Poor - significant optimization needed")

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        if self.validation_results['valid']:
            print("✓ Model is valid")
        else:
            print("✗ Model validation FAILED")

        if self.validation_results['errors']:
            print("\nErrors:")
            for error in self.validation_results['errors']:
                print(f"  ✗ {error}")

        if self.validation_results['warnings']:
            print(f"\nWarnings ({len(self.validation_results['warnings'])}):")
            for warning in self.validation_results['warnings']:
                print(f"  ⚠ {warning}")

        print("\nRecommendations:")
        if not self.validation_results['info'].get('quantized', False):
            print("  1. Apply INT8 quantization for 4x size reduction")

        size_mb = self.validation_results['info'].get('size_mb', 0)
        if size_mb > 20:
            print("  2. Consider using a smaller model architecture")

        print("  3. Test on real devices for accurate performance")
        print("  4. Profile inference time on target hardware")

    def test_inference(self):
        """Run a test inference"""
        print("\n" + "=" * 60)
        print("Running test inference...")
        print("=" * 60)

        try:
            input_details = self.interpreter.get_input_details()

            # Create dummy input
            for detail in input_details:
                shape = detail['shape']
                dtype = detail['dtype']

                if dtype in [np.uint8, np.int8]:
                    dummy_input = np.random.randint(0, 255, size=shape, dtype=dtype)
                else:
                    dummy_input = np.random.randn(*shape).astype(dtype)

                self.interpreter.set_tensor(detail['index'], dummy_input)

            # Run inference
            import time
            start = time.time()
            self.interpreter.invoke()
            inference_time = (time.time() - start) * 1000

            print(f"✓ Test inference successful")
            print(f"  CPU inference time: {inference_time:.2f} ms")

            self.validation_results['info']['cpu_inference_ms'] = round(inference_time, 2)

            # Get output
            output_details = self.interpreter.get_output_details()
            for i, detail in enumerate(output_details):
                output = self.interpreter.get_tensor(detail['index'])
                print(f"  Output {i} shape: {output.shape}")

        except Exception as e:
            print(f"✗ Test inference failed: {e}")
            self.validation_results['warnings'].append(f"Test inference failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate TFLite model for LiteRT mobile deployment'
    )
    parser.add_argument('model_path', help='Path to .tflite model file')
    parser.add_argument('--test', action='store_true',
                       help='Run test inference')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')

    args = parser.parse_args()

    validator = TFLiteModelValidator(args.model_path)
    results = validator.validate()

    if args.test and results['valid']:
        validator.test_inference()

    if not args.json:
        validator.print_summary()
    else:
        import json
        print(json.dumps(results, indent=2))

    # Exit code based on validation
    sys.exit(0 if results['valid'] else 1)


if __name__ == '__main__':
    main()
