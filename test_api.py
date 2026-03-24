import requests
import json

print("Testing AGAE-Layzer V2.0 API...")
print()

# Test 1: Health check
print("1. Testing health endpoint...")
try:
    response = requests.get("http://localhost:5000/api/health", timeout=5)
    if response.status_code == 200:
        print("✓ Health check passed")
        print(f"   Response: {response.json()}")
    else:
        print(f"✗ Health check failed: {response.status_code}")
except Exception as e:
    print(f"✗ Health check error: {e}")

print()

# Test 2: Protein prediction
print("2. Testing protein sequence prediction...")
protein_data = {
    "sequence": ">Test\nMVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTK",
    "model": "AGEA"
}

try:
    response = requests.post(
        "http://localhost:5000/api/predict",
        json=protein_data,
        timeout=10
    )
    if response.status_code == 200:
        result = response.json()
        print("✓ Protein prediction passed")
        print(f"   Sequence type: {result['sequence_type']}")
        print(f"   Total K sites: {result['statistics']['total_sites']}")
    else:
        print(f"✗ Protein prediction failed: {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"✗ Protein prediction error: {e}")

print()

# Test 3: DNA prediction
print("3. Testing DNA sequence prediction (6-frame)...")
dna_data = {
    "sequence": "ATGGTTCTGTCTCCTGCCGACAAGACCAACGTCAAGGCCGCC",
    "model": "AGEA"
}

try:
    response = requests.post(
        "http://localhost:5000/api/predict",
        json=dna_data,
        timeout=10
    )
    if response.status_code == 200:
        result = response.json()
        print("✓ DNA prediction passed")
        print(f"   Sequence type: {result['sequence_type']}")
        print(f"   Total K sites (all frames): {result['statistics']['total_sites']}")
        print(f"   Frames analyzed: {len(result['predictions'])}")
    else:
        print(f"✗ DNA prediction failed: {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"✗ DNA prediction error: {e}")

print()
print("API testing completed!")
