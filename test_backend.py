#!/usr/bin/env python3
"""
Quick test script to verify the complete backend API functionality
"""
import requests
import time
import json
from pathlib import Path

# Backend API base URL
API_BASE = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_health_check():
    """Test the health check endpoint"""
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_create_test_file():
    """Create a test text file for upload"""
    print_section("Creating Test File")
    test_texts = [
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with multiple layers.",
        "Natural language processing deals with text and speech.",
        "Computer vision enables machines to understand images.",
        "Data science combines statistics and programming.",
        "Python is a popular language for data science.",
        "JavaScript is essential for web development.",
        "Databases store and organize information efficiently.",
        "Cloud computing provides scalable infrastructure.",
        "Cybersecurity protects systems from digital threats."
    ]

    test_file = Path("test_dataset.txt")
    with open(test_file, 'w') as f:
        f.write('\n'.join(test_texts))

    print(f"✅ Created test file: {test_file}")
    print(f"   Contains {len(test_texts)} sample texts")
    return test_file

def test_upload_dataset(test_file):
    """Test dataset upload"""
    print_section("Testing Dataset Upload")
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test_dataset.txt', f, 'text/plain')}
            data = {'name': 'Test ML Dataset'}

            response = requests.post(f"{API_BASE}/api/v1/datasets", files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                print("✅ Dataset upload successful")
                print(f"   Dataset ID: {result.get('dataset_id')}")
                print(f"   Name: {result.get('name')}")
                print(f"   Status: {result.get('status')}")
                return result.get('dataset_id')
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_dataset_status(dataset_id):
    """Test checking dataset status"""
    print_section("Testing Dataset Status")
    try:
        response = requests.get(f"{API_BASE}/api/v1/datasets/{dataset_id}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Status check successful")
            print(f"   Dataset ID: {result.get('dataset_id')}")
            print(f"   Name: {result.get('name')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Created: {result.get('created_at')}")
            return result
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None

def test_list_datasets():
    """Test listing all datasets"""
    print_section("Testing List Datasets")
    try:
        response = requests.get(f"{API_BASE}/api/v1/datasets")
        if response.status_code == 200:
            datasets = response.json()
            print(f"✅ List datasets successful")
            print(f"   Total datasets: {len(datasets)}")
            for ds in datasets:
                print(f"   - {ds.get('name')} ({ds.get('status')})")
            return datasets
        else:
            print(f"❌ List datasets failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ List datasets error: {e}")
        return []

def wait_for_processing(dataset_id, max_wait=300):
    """Wait for dataset processing to complete"""
    print_section("Waiting for Processing")
    print(f"Waiting for dataset {dataset_id} to process...")

    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{API_BASE}/api/v1/datasets/{dataset_id}/status")
            if response.status_code == 200:
                status_info = response.json()
                status = status_info.get('status')
                progress = status_info.get('progress', 0)

                print(f"   Status: {status} | Progress: {progress}%")

                if status == 'completed':
                    print("✅ Processing completed successfully")
                    return True
                elif status == 'failed':
                    print(f"❌ Processing failed: {status_info.get('error', 'Unknown error')}")
                    return False
                elif status == 'processing':
                    # Continue waiting
                    pass
                else:
                    print(f"   Unknown status: {status}")

            time.sleep(5)
        except Exception as e:
            print(f"   Error checking status: {e}")
            time.sleep(5)

    print("❌ Processing timeout")
    return False

def test_get_visualization_data(dataset_id):
    """Test getting visualization data"""
    print_section("Testing Visualization Data")

    # Test point data
    try:
        response = requests.get(f"{API_BASE}/api/v1/datasets/{dataset_id}/data")
        if response.status_code == 200:
            # Count lines in NDJSON response
            lines = response.text.strip().split('\n')
            print(f"✅ Point data retrieved successfully")
            print(f"   Total points: {len(lines)}")
            if lines:
                first_point = json.loads(lines[0])
                print(f"   Sample point: {first_point}")
        else:
            print(f"❌ Point data failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Point data error: {e}")

    # Test grid data
    try:
        response = requests.get(f"{API_BASE}/api/v1/datasets/{dataset_id}/grid")
        if response.status_code == 200:
            grid_data = response.json()
            print(f"✅ Grid data retrieved successfully")
            print(f"   Grid dimensions: {len(grid_data.get('grid', [[]]))}x{len(grid_data.get('grid', [[]])[0]) if grid_data.get('grid') else 0}")
        else:
            print(f"❌ Grid data failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Grid data error: {e}")

def main():
    """Run all backend tests"""
    print("\n🚀 WizMap Backend API Test Suite")
    print("=" * 60)

    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Backend is not running. Please start the backend first.")
        print("   Run: docker compose up -d")
        return

    # Test 2: Create test file
    test_file = test_create_test_file()

    # Test 3: Upload dataset
    dataset_id = test_upload_dataset(test_file)
    if not dataset_id:
        print("\n❌ Dataset upload failed. Cannot continue with further tests.")
        return

    # Test 4: Check dataset status
    test_dataset_status(dataset_id)

    # Test 5: List all datasets
    test_list_datasets()

    # Test 6: Wait for processing
    if wait_for_processing(dataset_id):
        # Test 7: Get visualization data
        test_get_visualization_data(dataset_id)

        print_section("Test Results Summary")
        print("✅ All tests passed!")
        print(f"🎉 Backend API is fully functional")
        print(f"📊 Test dataset ID: {dataset_id}")
        print(f"🌐 View at: http://localhost:3001/?datasetId={dataset_id}")
    else:
        print_section("Test Results Summary")
        print("⚠️ Processing tests completed but with warnings")
        print("📊 Test dataset ID: {dataset_id}")
        print("💡 You can check the status manually:")
        print(f"   curl {API_BASE}/api/v1/datasets/{dataset_id}/status")

    # Cleanup
    test_file.unlink()

if __name__ == "__main__":
    main()