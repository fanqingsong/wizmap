#!/usr/bin/env python3
"""
Simple test script to verify file upload functionality
"""

import requests
import os

# Backend API endpoint
API_URL = "http://localhost:8080/api/v1/datasets"

# Test file path
TEST_FILE = "/home/fqs/workspace/self/wizmap/example-dataset.txt"

def test_upload():
    """Test file upload to backend"""
    if not os.path.exists(TEST_FILE):
        print(f"❌ Test file not found: {TEST_FILE}")
        return False

    try:
        print(f"📤 Uploading test file: {TEST_FILE}")

        with open(TEST_FILE, 'rb') as f:
            files = {'file': ('example-dataset.txt', f, 'text/plain')}
            data = {'name': 'Test Dataset from Script'}

            response = requests.post(API_URL, files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   Dataset ID: {result.get('dataset_id')}")
                print(f"   Message: {result.get('message')}")
                print(f"   Status: {result.get('status')}")
                return True
            else:
                print(f"❌ Upload failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Upload failed with exception: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing WizMap File Upload Functionality")
    print("=" * 50)

    # First check if backend is running
    try:
        health_response = requests.get("http://localhost:8080/health")
        if health_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend is not responding correctly")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("   Please make sure the backend is running on http://localhost:8080")
        exit(1)

    # Test upload
    success = test_upload()

    print("=" * 50)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
        exit(1)
