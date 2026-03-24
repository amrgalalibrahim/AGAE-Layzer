"""
AGEA-Layzer V2.0 - Glitch Deployment
Lysine Lactylation Site Prediction Tool
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
from datetime import datetime

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from sequence_detector import detect_sequence_type, clean_sequence, validate_sequence
from translator import six_frame_translation, get_frame_info
from predictor import predict_lactylation, predict_six_frames, aggregate_frame_statistics
from exporter import export_all_formats

app = Flask(__name__)
app.config['RESULTS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'results')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Ensure results directory exists
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint."""
    try:
        data = request.get_json()
        
        if not data or 'sequence' not in data:
            return jsonify({'error': 'No sequence provided'}), 400
        
        raw_sequence = data['sequence']
        model_type = data.get('model', 'AGEA')
        
        # Clean sequence
        sequence = clean_sequence(raw_sequence)
        
        if not sequence:
            return jsonify({'error': 'Empty sequence after cleaning'}), 400
        
        # Detect sequence type
        seq_type = detect_sequence_type(sequence)
        
        # Validate sequence
        is_valid, error_msg = validate_sequence(sequence, seq_type)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Process based on sequence type
        if seq_type == 'PROTEIN':
            predictions = predict_lactylation(sequence, model_type)
            
            lactylated = [p for p in predictions if p['label'] == '+']
            non_lactylated = [p for p in predictions if p['label'] == '-']
            
            statistics = {
                'total_sites': len(predictions),
                'total_lactylated': len(lactylated),
                'total_non_lactylated': len(non_lactylated)
            }
            
            result = {
                'sequence_type': seq_type,
                'sequence_length': len(sequence),
                'model_used': model_type,
                'predictions': predictions,
                'statistics': statistics,
                'sequence': sequence
            }
        
        elif seq_type in ['DNA', 'RNA']:
            frames = six_frame_translation(sequence)
            frame_info = get_frame_info(frames)
            frame_predictions = predict_six_frames(frames, model_type)
            statistics = aggregate_frame_statistics(frame_predictions)
            
            result = {
                'sequence_type': seq_type,
                'sequence_length': len(sequence),
                'model_used': model_type,
                'frames': frame_info,
                'predictions': frame_predictions,
                'statistics': statistics,
                'original_sequence': sequence
            }
        
        else:
            return jsonify({'error': 'Unknown sequence type'}), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['POST'])
def export():
    """Export predictions to various formats."""
    try:
        data = request.get_json()
        
        if not data or 'predictions' not in data:
            return jsonify({'error': 'No prediction data provided'}), 400
        
        predictions = data['predictions']
        sequence_info = data.get('sequence_info', {})
        statistics = data.get('statistics', {})
        export_format = data.get('format', 'csv')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = os.path.join(
            app.config['RESULTS_FOLDER'],
            f'lactylation_results_{timestamp}'
        )
        
        from exporter import export_to_csv, export_to_excel, export_to_json, export_to_text
        
        if export_format == 'csv':
            output_path = f"{base_filename}.csv"
            export_to_csv(predictions, sequence_info, output_path)
        elif export_format == 'excel':
            output_path = f"{base_filename}.xlsx"
            export_to_excel(predictions, sequence_info, statistics, output_path)
        elif export_format == 'json':
            output_path = f"{base_filename}.json"
            export_to_json(predictions, sequence_info, statistics, output_path)
        elif export_format == 'text':
            output_path = f"{base_filename}_report.txt"
            export_to_text(predictions, sequence_info, statistics, output_path)
        else:
            return jsonify({'error': 'Invalid export format'}), 400
        
        return jsonify({
            'success': True,
            'file': output_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download(filename):
    """Download exported file."""
    try:
        file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'service': 'AGEA-Layzer'
    })


if __name__ == '__main__':
    # Glitch uses PORT environment variable
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)

