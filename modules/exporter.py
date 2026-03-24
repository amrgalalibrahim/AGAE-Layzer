"""
Result Export Module
Exports prediction results in various formats (CSV, Excel, JSON, TXT)
"""

import json
import pandas as pd
from datetime import datetime
import os


def export_to_csv(predictions, sequence_info, output_path):
    """
    Export predictions to CSV format.
    
    Args:
        predictions (dict or list): Predictions data
        sequence_info (dict): Sequence metadata
        output_path (str): Output file path
        
    Returns:
        str: Path to saved file
    """
    rows = []
    
    # Handle single protein sequence
    if isinstance(predictions, list):
        for pred in predictions:
            rows.append({
                'Position': pred['position'],
                'Residue': pred['residue'],
                'Window': pred['window'],
                'Prediction': pred['prediction'],
                'Label': pred['label'],
                'Score': round(pred['score'], 4),
                'Confidence': round(pred['confidence'], 4)
            })
    
    # Handle six-frame predictions
    elif isinstance(predictions, dict):
        for frame_name, frame_preds in predictions.items():
            for pred in frame_preds:
                rows.append({
                    'Frame': frame_name,
                    'Position': pred['position'],
                    'Residue': pred['residue'],
                    'Window': pred['window'],
                    'Prediction': pred['prediction'],
                    'Label': pred['label'],
                    'Score': round(pred['score'], 4),
                    'Confidence': round(pred['confidence'], 4)
                })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    
    return output_path


def export_to_excel(predictions, sequence_info, statistics, output_path):
    """
    Export predictions to Excel format with multiple sheets.
    
    Args:
        predictions (dict or list): Predictions data
        sequence_info (dict): Sequence metadata
        statistics (dict): Summary statistics
        output_path (str): Output file path
        
    Returns:
        str: Path to saved file
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Summary sheet
        summary_data = {
            'Metric': [],
            'Value': []
        }
        
        summary_data['Metric'].append('Sequence Type')
        summary_data['Value'].append(sequence_info.get('type', 'N/A'))
        
        summary_data['Metric'].append('Sequence Length')
        summary_data['Value'].append(sequence_info.get('length', 'N/A'))
        
        summary_data['Metric'].append('Model Used')
        summary_data['Value'].append(sequence_info.get('model', 'N/A'))
        
        summary_data['Metric'].append('Analysis Date')
        summary_data['Value'].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        if isinstance(statistics, dict):
            summary_data['Metric'].append('Total K Sites')
            summary_data['Value'].append(statistics.get('total_sites', 0))
            
            summary_data['Metric'].append('Lactylated Sites')
            summary_data['Value'].append(statistics.get('total_lactylated', 0))
            
            summary_data['Metric'].append('Non-Lactylated Sites')
            summary_data['Value'].append(statistics.get('total_non_lactylated', 0))
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Detailed results sheet
        if isinstance(predictions, list):
            # Single protein sequence
            rows = []
            for pred in predictions:
                rows.append({
                    'Position': pred['position'],
                    'Residue': pred['residue'],
                    'Window': pred['window'],
                    'Prediction': pred['prediction'],
                    'Label': pred['label'],
                    'Score': round(pred['score'], 4),
                    'Confidence': round(pred['confidence'], 4)
                })
            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name='Predictions', index=False)
        
        elif isinstance(predictions, dict):
            # Six-frame predictions
            for frame_name, frame_preds in predictions.items():
                rows = []
                for pred in frame_preds:
                    rows.append({
                        'Position': pred['position'],
                        'Residue': pred['residue'],
                        'Window': pred['window'],
                        'Prediction': pred['prediction'],
                        'Label': pred['label'],
                        'Score': round(pred['score'], 4),
                        'Confidence': round(pred['confidence'], 4)
                    })
                if rows:
                    df = pd.DataFrame(rows)
                    # Clean frame name for sheet name
                    sheet_name = f"Frame_{frame_name.replace('+', 'plus').replace('-', 'minus')}"
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Frame statistics sheet
            if 'frame_statistics' in statistics:
                frame_stats_rows = []
                for frame_name, stats in statistics['frame_statistics'].items():
                    frame_stats_rows.append({
                        'Frame': frame_name,
                        'Total Sites': stats['total_sites'],
                        'Lactylated': stats['lactylated_sites'],
                        'Non-Lactylated': stats['non_lactylated_sites'],
                        'Avg Score': round(stats['avg_score'], 4),
                        'Avg Confidence': round(stats['avg_confidence'], 4)
                    })
                frame_stats_df = pd.DataFrame(frame_stats_rows)
                frame_stats_df.to_excel(writer, sheet_name='Frame_Statistics', index=False)
    
    return output_path


def export_to_json(predictions, sequence_info, statistics, output_path):
    """
    Export predictions to JSON format.
    
    Args:
        predictions (dict or list): Predictions data
        sequence_info (dict): Sequence metadata
        statistics (dict): Summary statistics
        output_path (str): Output file path
        
    Returns:
        str: Path to saved file
    """
    output_data = {
        'metadata': {
            'sequence_type': sequence_info.get('type', 'N/A'),
            'sequence_length': sequence_info.get('length', 'N/A'),
            'model_used': sequence_info.get('model', 'N/A'),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'statistics': statistics,
        'predictions': predictions
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    return output_path


def export_to_text(predictions, sequence_info, statistics, output_path):
    """
    Export predictions to human-readable text report.
    
    Args:
        predictions (dict or list): Predictions data
        sequence_info (dict): Sequence metadata
        statistics (dict): Summary statistics
        output_path (str): Output file path
        
    Returns:
        str: Path to saved file
    """
    with open(output_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("AGAE-LAYZER V2.0 - LACTYLATION PREDICTION REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # Metadata
        f.write("ANALYSIS INFORMATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"Sequence Type: {sequence_info.get('type', 'N/A')}\n")
        f.write(f"Sequence Length: {sequence_info.get('length', 'N/A')}\n")
        f.write(f"Model Used: {sequence_info.get('model', 'N/A')}\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n")
        
        # Statistics
        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 80 + "\n")
        
        if isinstance(statistics, dict):
            f.write(f"Total Lysine (K) Sites: {statistics.get('total_sites', 0)}\n")
            f.write(f"Lactylated Sites (+): {statistics.get('total_lactylated', 0)}\n")
            f.write(f"Non-Lactylated Sites (-): {statistics.get('total_non_lactylated', 0)}\n")
            
            if statistics.get('total_sites', 0) > 0:
                lactylation_rate = (statistics.get('total_lactylated', 0) / 
                                   statistics.get('total_sites', 1)) * 100
                f.write(f"Lactylation Rate: {lactylation_rate:.2f}%\n")
            
            f.write("\n")
            
            # Frame statistics if available
            if 'frame_statistics' in statistics:
                f.write("FRAME-BY-FRAME STATISTICS\n")
                f.write("-" * 80 + "\n")
                for frame_name, stats in statistics['frame_statistics'].items():
                    f.write(f"\nFrame {frame_name}:\n")
                    f.write(f"  Total Sites: {stats['total_sites']}\n")
                    f.write(f"  Lactylated: {stats['lactylated_sites']}\n")
                    f.write(f"  Non-Lactylated: {stats['non_lactylated_sites']}\n")
                    f.write(f"  Average Score: {stats['avg_score']:.4f}\n")
                    f.write(f"  Average Confidence: {stats['avg_confidence']:.4f}\n")
                f.write("\n")
        
        # Detailed predictions
        f.write("DETAILED PREDICTIONS\n")
        f.write("-" * 80 + "\n\n")
        
        if isinstance(predictions, list):
            # Single protein sequence
            for pred in predictions:
                f.write(f"Position: {pred['position']}\n")
                f.write(f"Window: {pred['window']}\n")
                f.write(f"Prediction: {pred['prediction']} ({pred['label']})\n")
                f.write(f"Score: {pred['score']:.4f}\n")
                f.write(f"Confidence: {pred['confidence']:.4f}\n")
                f.write("-" * 40 + "\n")
        
        elif isinstance(predictions, dict):
            # Six-frame predictions
            for frame_name, frame_preds in predictions.items():
                f.write(f"\n{'=' * 40}\n")
                f.write(f"FRAME {frame_name}\n")
                f.write(f"{'=' * 40}\n\n")
                
                for pred in frame_preds:
                    f.write(f"Position: {pred['position']}\n")
                    f.write(f"Window: {pred['window']}\n")
                    f.write(f"Prediction: {pred['prediction']} ({pred['label']})\n")
                    f.write(f"Score: {pred['score']:.4f}\n")
                    f.write(f"Confidence: {pred['confidence']:.4f}\n")
                    f.write("-" * 40 + "\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    return output_path


def export_all_formats(predictions, sequence_info, statistics, base_filename):
    """
    Export predictions in all available formats.
    
    Args:
        predictions (dict or list): Predictions data
        sequence_info (dict): Sequence metadata
        statistics (dict): Summary statistics
        base_filename (str): Base filename without extension
        
    Returns:
        dict: Paths to all exported files
    """
    exported_files = {}
    
    # Ensure results directory exists
    results_dir = os.path.dirname(base_filename)
    if results_dir and not os.path.exists(results_dir):
        os.makedirs(results_dir, exist_ok=True)
    
    # Export CSV
    csv_path = f"{base_filename}.csv"
    export_to_csv(predictions, sequence_info, csv_path)
    exported_files['csv'] = csv_path
    
    # Export Excel
    excel_path = f"{base_filename}.xlsx"
    export_to_excel(predictions, sequence_info, statistics, excel_path)
    exported_files['excel'] = excel_path
    
    # Export JSON
    json_path = f"{base_filename}.json"
    export_to_json(predictions, sequence_info, statistics, json_path)
    exported_files['json'] = json_path
    
    # Export Text Report
    txt_path = f"{base_filename}_report.txt"
    export_to_text(predictions, sequence_info, statistics, txt_path)
    exported_files['text'] = txt_path
    
    return exported_files

