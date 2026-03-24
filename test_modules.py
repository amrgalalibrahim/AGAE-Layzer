"""
Test script for AGAE-Layzer V2.0 modules
"""

import sys
import os

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from sequence_detector import detect_sequence_type, clean_sequence, validate_sequence
from translator import six_frame_translation, get_frame_info, reverse_complement
from predictor import predict_lactylation, predict_six_frames, aggregate_frame_statistics

print("=" * 80)
print("AGAE-LAYZER V2.0 - MODULE TESTING")
print("=" * 80)
print()

# Test 1: Sequence Detection
print("TEST 1: Sequence Type Detection")
print("-" * 80)

test_sequences = {
    "PROTEIN": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTK",
    "DNA": "ATGGTTCTGTCTCCTGCCGACAAGACCAACGTCAAGGCCGCC",
    "RNA": "AUGGCUAGCUAGCUAGCUAGCUAGCUAGCUAG"
}

for seq_type, sequence in test_sequences.items():
    detected = detect_sequence_type(sequence)
    status = "✓ PASS" if detected == seq_type else "✗ FAIL"
    print(f"{status} - Expected: {seq_type}, Detected: {detected}")

print()

# Test 2: Six-Frame Translation
print("TEST 2: Six-Frame Translation")
print("-" * 80)

dna_sequence = "ATGGTTCTGTCTCCTGCCGACAAGACCAACGTCAAGGCCGCC"
frames = six_frame_translation(dna_sequence)

print(f"Input DNA: {dna_sequence}")
print(f"DNA Length: {len(dna_sequence)} bp")
print()

for frame_name, protein in frames.items():
    print(f"Frame {frame_name}: {protein[:30]}... (length: {len(protein)} aa)")

print()

# Test 3: Reverse Complement
print("TEST 3: Reverse Complement")
print("-" * 80)

dna_test = "ATGC"
rev_comp = reverse_complement(dna_test)
expected = "GCAT"
status = "✓ PASS" if rev_comp == expected else "✗ FAIL"
print(f"{status} - Input: {dna_test}, Output: {rev_comp}, Expected: {expected}")

print()

# Test 4: Lactylation Prediction (Protein)
print("TEST 4: Lactylation Prediction (Protein)")
print("-" * 80)

protein_seq = "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTK"
predictions = predict_lactylation(protein_seq, model_type="AGEA")

print(f"Protein: {protein_seq}")
print(f"Total K sites found: {len(predictions)}")
print(f"Sample predictions:")

for pred in predictions[:3]:
    print(f"  Position {pred['position']}: {pred['prediction']} (score: {pred['score']:.3f})")

print()

# Test 5: Six-Frame Prediction
print("TEST 5: Six-Frame Prediction (DNA)")
print("-" * 80)

dna_seq = "ATGGTTCTGTCTCCTGCCGACAAGACCAACGTCAAGGCCGCCTGGGGTAAGGTCGGCGCGCACGCTGGCGAGTATGGTGCGGAGGCCCTGGAGAGGATGTTCCTGTCCTTCCCCACCACCAAGACCTACTTCCCGCACTTCGACCTGAGCCACGGCTCTGCCCAGGTTAAGGGCCACGGCAAGAAGGTGGCCGACGCGCTGACCAACGCCGTGGCGCACGTGGACGACATGCCCAACGCGCTGTCCGCCCTGAGCGACCTGCACGCGCACAAGCTGCGCGTGGACCCGGTCAACTTCAAGCTCCTAAGCCACTGCCTGCTGGTGACCCTGGCCGCCCACCTCCCCGCCGAGTTCACCCCTGCGGTGCACGCCTCCCTGGACAAGTTCCTGGCTTCTGTGAGCACCGTGCTGACCTCCAAATACCGTTAA"

frames = six_frame_translation(dna_seq)
frame_predictions = predict_six_frames(frames, model_type="AGEA")
statistics = aggregate_frame_statistics(frame_predictions)

print(f"DNA Length: {len(dna_seq)} bp")
print(f"Total K sites (all frames): {statistics['total_sites']}")
print(f"Lactylated sites: {statistics['total_lactylated']}")
print(f"Non-lactylated sites: {statistics['total_non_lactylated']}")
print()

print("Per-frame statistics:")
for frame_name, stats in statistics['frame_statistics'].items():
    print(f"  Frame {frame_name}: {stats['total_sites']} sites, "
          f"{stats['lactylated_sites']} lactylated, "
          f"avg score: {stats['avg_score']:.3f}")

print()

# Test 6: Validation
print("TEST 6: Sequence Validation")
print("-" * 80)

test_cases = [
    ("ACDEFGHIKLMNPQRSTVWY", "PROTEIN", True),
    ("ATGC", "DNA", True),
    ("AUGC", "RNA", True),
    ("ATGCX", "DNA", False),  # Invalid character
]

for sequence, seq_type, should_pass in test_cases:
    is_valid, error_msg = validate_sequence(sequence, seq_type)
    status = "✓ PASS" if is_valid == should_pass else "✗ FAIL"
    result = "Valid" if is_valid else f"Invalid ({error_msg})"
    print(f"{status} - {seq_type} '{sequence[:20]}...': {result}")

print()
print("=" * 80)
print("ALL TESTS COMPLETED")
print("=" * 80)

