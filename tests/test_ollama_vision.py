"""
Test script for Ollama vision model badge recognition.

This script tests different prompt strategies and evaluates Ollama's ability
to recognize and count Scout badges from photos.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import ollama


# Test prompt templates
PROMPTS = {
    "basic": "What Scout badges do you see in this image?",

    "detailed": """Identify all Australian Cub Scout badges in this image.
For each badge type, provide:
1. Badge name
2. Quantity/count
3. Your confidence level (high/medium/low)""",

    "structured": """Analyze this image of Scout badges and provide a structured response:

BADGES IDENTIFIED:
- Badge Name: [name]
  Count: [number]
  Confidence: [high/medium/low]

List all distinct badge types you can identify.""",

    "counting": """You are analyzing a photo of Scout badge inventory.

Task: Count and identify each type of badge visible.

For each badge type, tell me:
- The badge name or description
- How many you can see
- Where they are located in the image

Be specific about quantities.""",

    "context_rich": """This is a photo of Australian Cub Scout badges stored in an organizer box.

Australian Cub Scout badges include:
- OAS (Outdoor Adventure Skills) badges with stages 1-4
- Special Interest Area (SIA) badges (hexagonal, purple border)
- Milestone badges (circular)
- Achievement badges (various shapes)

Identify each type of badge you see and count how many of each.""",
}


def test_badge_recognition(
    image_path: Path,
    prompt: str,
    model: str = "llava:7b"
) -> Tuple[str, float]:
    """
    Test badge recognition with a specific prompt.

    Args:
        image_path: Path to the badge image
        prompt: Prompt template to use
        model: Ollama model name

    Returns:
        Tuple of (response text, response time in seconds)
    """
    print(f"\n{'='*60}")
    print(f"Testing: {image_path.name}")
    print(f"Model: {model}")
    print(f"Prompt: {prompt[:50]}...")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [str(image_path)]
            }]
        )

        elapsed_time = time.time() - start_time
        response_text = response['message']['content']

        print(f"\nResponse (took {elapsed_time:.2f}s):")
        print("-" * 60)
        print(response_text)
        print("-" * 60)

        return response_text, elapsed_time

    except Exception as e:
        elapsed_time = time.time() - start_time
        error_msg = f"Error: {str(e)}"
        print(f"\n{error_msg}")
        return error_msg, elapsed_time


def run_comprehensive_tests(
    test_images_dir: Path,
    output_file: Path,
    model: str = "llava:7b"
) -> Dict:
    """
    Run comprehensive tests on all images with all prompt strategies.

    Args:
        test_images_dir: Directory containing test images
        output_file: Path to save results JSON
        model: Ollama model to test

    Returns:
        Dictionary of test results
    """
    print(f"\n{'#'*60}")
    print("# OLLAMA BADGE RECOGNITION TEST SUITE")
    print(f"# Model: {model}")
    print(f"{'#'*60}\n")

    # Find all test images
    image_files = list(test_images_dir.glob("*.jpeg")) + \
                  list(test_images_dir.glob("*.jpg")) + \
                  list(test_images_dir.glob("*.png"))

    print(f"Found {len(image_files)} test images:")
    for img in image_files:
        print(f"  - {img.name} ({img.stat().st_size / 1024 / 1024:.1f} MB)")

    results = {
        "model": model,
        "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "num_images": len(image_files),
        "prompt_strategies": list(PROMPTS.keys()),
        "tests": []
    }

    # Test each image with each prompt
    for image_path in image_files:
        print(f"\n\n{'*'*60}")
        print(f"* TESTING IMAGE: {image_path.name}")
        print(f"{'*'*60}")

        image_results = {
            "image": image_path.name,
            "prompt_tests": {}
        }

        for prompt_name, prompt_text in PROMPTS.items():
            print(f"\n--- Testing prompt: {prompt_name} ---")

            response, elapsed_time = test_badge_recognition(
                image_path, prompt_text, model
            )

            image_results["prompt_tests"][prompt_name] = {
                "prompt": prompt_text,
                "response": response,
                "time_seconds": elapsed_time
            }

            # Brief pause between tests
            time.sleep(1)

        results["tests"].append(image_results)

    # Calculate summary statistics
    total_time = sum(
        test["time_seconds"]
        for img_result in results["tests"]
        for test in img_result["prompt_tests"].values()
    )
    avg_time = total_time / (len(image_files) * len(PROMPTS))

    results["summary"] = {
        "total_tests": len(image_files) * len(PROMPTS),
        "total_time_seconds": total_time,
        "average_response_time_seconds": avg_time
    }

    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\n{'='*60}")
    print("TEST SUITE COMPLETE")
    print(f"{'='*60}")
    print(f"Total tests run: {results['summary']['total_tests']}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average response time: {avg_time:.2f} seconds")
    print(f"Results saved to: {output_file}")

    return results


def quick_test(image_path: Path, model: str = "llava:7b"):
    """
    Run a quick test with the best performing prompt.

    Args:
        image_path: Path to test image
        model: Ollama model name
    """
    print(f"\n{'='*60}")
    print("QUICK TEST")
    print(f"{'='*60}")

    # Use the context-rich prompt as it's likely most effective
    response, elapsed_time = test_badge_recognition(
        image_path,
        PROMPTS["context_rich"],
        model
    )

    return response, elapsed_time


if __name__ == "__main__":
    import sys

    # Setup paths
    project_root = Path(__file__).parent.parent
    test_images_dir = project_root / "tests" / "sample_badges"
    output_file = project_root / "tests" / "ollama_test_results.json"

    # Check if test images exist
    if not test_images_dir.exists():
        print(f"Error: Test images directory not found: {test_images_dir}")
        sys.exit(1)

    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test mode with first image
        images = list(test_images_dir.glob("*.jpeg"))
        if images:
            quick_test(images[0])
        else:
            print("No test images found!")
            sys.exit(1)
    else:
        # Full test suite
        results = run_comprehensive_tests(
            test_images_dir,
            output_file,
            model="llava:7b"
        )

        print("\n" + "="*60)
        print("To generate a human-readable report, run:")
        print("  python tests/generate_test_report.py")
        print("="*60)
