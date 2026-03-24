"""
Simple startup script for AGAE-Layzer V2.0
Runs without debug mode for better stability
"""

from app import app

if __name__ == '__main__':
    print("=" * 80)
    print("AGAE-LAYZER V2.0 - Lactylation Site Prediction Tool")
    print("=" * 80)
    print("\nStarting server on http://localhost:5000")
    print("\nFeatures:")
    print("  - Protein sequence analysis")
    print("  - DNA/RNA 6-frame translation")
    print("  - Multiple ML models (AGEA, LSTM, BLSTM, BGRU, CNN, CNN+BGRU)")
    print("  - Export to CSV, Excel, JSON, and Text formats")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

