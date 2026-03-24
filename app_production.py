"""
AGAE-Layzer V2.0 - Production Flask Application
Lactylation Site Prediction Tool with 6-Frame Translation Support
Optimized for deployment
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
from datetime import datetime
import logging

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from sequence_detector import detect_sequence_type, clean_sequence, validate_sequence
from translator import six_frame_translation, get_frame_info
from predictor import predict_lactylation, predict_six_frames, aggregate_frame_statistics
from exporter import export_all_formats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['RESULTS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'results')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

# Ensure results directory exists
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Disable debug mode for production
app.config['DEBUG'] = False
app.config['TESTING'] = False


@app.route('/')
def index():
    """Render main page."""
    logger.info("Main page accessed")
    return render_template('index.html')


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint.
    Accepts sequence and model type, returns predictions.
    """
    try:
        data = request.get_json()
        
        if not data or 'sequence' not in data:
            logger.warning("Prediction request with no sequence")
            return jsonify({'error': 'No sequence provided'}), 400
        
        raw_sequence = data['sequence']
        model_type = data.get('model', 'AGEA')
        
        logger.info(f"Prediction request: model={model_type}, seq_length={len(raw_sequence)}")
        
        # Clean sequence
        sequence = clean_sequence(raw_sequence)
        
        if not sequence:
            return jsonify({'error': 'Empty sequence after cleaning'}), 400
        
        # Detect sequence type
        seq_type = detect_sequence_type(sequence)
        logger.info(f"Detected sequence type: {seq_type}")
        
        # Validate sequence
        is_valid, error_msg = validate_sequence(sequence, seq_type)
        if not is_valid:
            logger.warning(f"Invalid sequence: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Process based on sequence type
        if seq_type == 'PROTEIN':
            # Direct protein sequence analysis
            predictions = predict_lactylation(sequence, model_type)
            
            # Calculate statistics
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
            
            logger.info(f"Protein prediction complete: {len(predictions)} sites found")
        
        elif seq_type in ['DNA', 'RNA']:
            # Six-frame translation and analysis
            frames = six_frame_translation(sequence)
            frame_info = get_frame_info(frames)
            
            # Predict for all frames
            frame_predictions = predict_six_frames(frames, model_type)
            
            # Aggregate statistics
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
            
            logger.info(f"{seq_type} prediction complete: {statistics['total_sites']} total sites across 6 frames")
        
        else:
            return jsonify({'error': 'Unknown sequence type'}), 400
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['POST'])
def export():
    """
    Export predictions to various formats.
    """
    try:
        data = request.get_json()
        
        if not data or 'predictions' not in data:
            return jsonify({'error': 'No prediction data provided'}), 400
        
        predictions = data['predictions']
        sequence_info = data.get('sequence_info', {})
        statistics = data.get('statistics', {})
        export_format = data.get('format', 'csv')
        
        logger.info(f"Export request: format={export_format}")
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = os.path.join(
            app.config['RESULTS_FOLDER'],
            f'lactylation_results_{timestamp}'
        )
        
        # Export based on format
        if export_format == 'all':
            exported_files = export_all_formats(
                predictions, sequence_info, statistics, base_filename
            )
            return jsonify({
                'success': True,
                'files': exported_files
            })
        else:
            # Export single format
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
            
            logger.info(f"Export complete: {output_path}")
            
            return jsonify({
                'success': True,
                'file': output_path
            })
    
    except Exception as e:
        logger.error(f"Export error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download(filename):
    """
    Download exported file.
    """
    try:
        file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {filename}")
            return jsonify({'error': 'File not found'}), 404
        
        logger.info(f"File download: {filename}")
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
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


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {str(error)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("AGEA-LAYZER V2.0 - Production Server")
    logger.info("=" * 80)
    logger.info("Starting production server...")
    logger.info("Features:")
    logger.info("  - Protein sequence analysis")
    logger.info("  - DNA/RNA 6-frame translation")
    logger.info("  - Multiple ML models")
    logger.info("  - Export to CSV, Excel, JSON, and Text formats")
    logger.info("=" * 80)
    
    # Run with production settings
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

