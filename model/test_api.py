#!/usr/bin/env python3
"""
Test script for the ATS API
"""
import requests
import json

def test_api():
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return

    # Test analyze endpoint with a sample PDF
    try:
        with open("resume.pdf", "rb") as f:
            files = {"file": ("resume.pdf", f, "application/pdf")}
            response = requests.post("http://localhost:8000/analyze", files=files)

        print(f"Analyze endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Success! Response keys:", list(result.keys()))
            print(f"Final ATS Score: {result.get('final_ats_score')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Analyze test failed: {e}")

if __name__ == "__main__":
    test_api()