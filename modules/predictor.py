"""
Lactylation Site Prediction Module
Predicts lactylation sites on Lysine (K) residues
"""

import numpy as np
from typing import List, Dict, Tuple


def find_lysine_sites(protein_sequence):
    """
    Find all Lysine (K) residues in a protein sequence.
    
    Args:
        protein_sequence (str): Protein sequence
        
    Returns:
        list: List of positions (0-indexed) where K residues are found
    """
    return [i for i, aa in enumerate(protein_sequence) if aa == 'K']


def extract_window(sequence, position, window_size=15):
    """
    Extract flanking sequence window around a position.
    
    Args:
        sequence (str): Protein sequence
        position (int): Central position (K residue)
        window_size (int): Number of residues on each side (default: 15)
        
    Returns:
        str: Flanking sequence window (padded with '-' if needed)
    """
    start = max(0, position - window_size)
    end = min(len(sequence), position + window_size + 1)
    
    # Extract window
    window = sequence[start:end]
    
    # Pad if necessary
    left_pad = window_size - (position - start)
    right_pad = window_size - (end - position - 1)
    
    if left_pad > 0:
        window = '-' * left_pad + window
    if right_pad > 0:
        window = window + '-' * right_pad
    
    return window


def calculate_features(window, model_type="AGEA"):
    """
    Calculate features for the sequence window based on model type.
    This is a simplified simulation of feature encoding.
    
    Args:
        window (str): Sequence window
        model_type (str): ML model type
        
    Returns:
        dict: Feature dictionary
    """
    features = {}
    
    # Basic compositional features
    amino_acids = "ACDEFGHIKLMNPQRSTVWY"
    for aa in amino_acids:
        features[f'comp_{aa}'] = window.count(aa) / len(window)
    
    # Physicochemical properties (simplified)
    hydrophobic = "AILMFVPGW"
    polar = "STYCNQ"
    charged = "DEKR"
    
    features['hydrophobic_ratio'] = sum(1 for aa in window if aa in hydrophobic) / len(window)
    features['polar_ratio'] = sum(1 for aa in window if aa in polar) / len(window)
    features['charged_ratio'] = sum(1 for aa in window if aa in charged) / len(window)
    
    return features


def predict_lactylation(protein_sequence, model_type="AGEA", threshold=0.5):
    """
    Predict lactylation sites in a protein sequence.
    
    Args:
        protein_sequence (str): Protein sequence
        model_type (str): ML model to use (AGEA, LSTM, BLSTM, etc.)
        threshold (float): Classification threshold (default: 0.5)
        
    Returns:
        list: List of prediction dictionaries
    """
    predictions = []
    
    # Find all K residues
    lysine_sites = find_lysine_sites(protein_sequence)
    
    for site in lysine_sites:
        # Extract window
        window = extract_window(protein_sequence, site)
        
        # Calculate features
        features = calculate_features(window, model_type)
        
        # Simulate prediction (in real implementation, this would use trained model)
        # Using pseudo-random but deterministic scoring based on features
        score = simulate_model_prediction(features, model_type, site)
        
        # Classify
        is_lactylated = score >= threshold
        
        predictions.append({
            'position': site + 1,  # Convert to 1-indexed
            'residue': 'K',
            'window': window,
            'score': score,
            'confidence': abs(score - 0.5) * 2,  # Confidence based on distance from threshold
            'prediction': 'Lactylated' if is_lactylated else 'Non-Lactylated',
            'label': '+' if is_lactylated else '-'
        })
    
    return predictions


def simulate_model_prediction(features, model_type, position):
    """
    Simulate model prediction score.
    In real implementation, this would load and apply trained model.
    
    Args:
        features (dict): Feature dictionary
        model_type (str): Model type
        position (int): Position in sequence (for reproducibility)
        
    Returns:
        float: Prediction score (0-1)
    """
    # Use features and position to generate pseudo-random but deterministic score
    np.random.seed(position)
    
    # Model-specific scoring logic
    base_score = np.random.random()
    
    # Adjust based on features
    if features['charged_ratio'] > 0.3:
        base_score += 0.1
    if features['hydrophobic_ratio'] > 0.4:
        base_score -= 0.1
    if features['comp_K'] > 0.1:
        base_score += 0.05
    
    # Model-specific adjustments
    model_weights = {
        'AGEA': 1.0,
        'LSTM': 0.95,
        'BLSTM': 0.98,
        'BGRU': 0.96,
        'CNN': 0.93,
        'CNN_BGRU': 0.97
    }
    
    weight = model_weights.get(model_type, 1.0)
    final_score = base_score * weight
    
    # Clip to [0, 1]
    final_score = max(0.0, min(1.0, final_score))
    
    return final_score


def predict_six_frames(frames_dict, model_type="AGEA"):
    """
    Predict lactylation sites for all six reading frames.
    
    Args:
        frames_dict (dict): Dictionary of translated frames
        model_type (str): ML model type
        
    Returns:
        dict: Predictions for each frame
    """
    all_predictions = {}
    
    for frame_name, protein_sequence in frames_dict.items():
        predictions = predict_lactylation(protein_sequence, model_type)
        all_predictions[frame_name] = predictions
    
    return all_predictions


def aggregate_frame_statistics(frame_predictions):
    """
    Aggregate statistics across all frames.
    
    Args:
        frame_predictions (dict): Predictions for each frame
        
    Returns:
        dict: Aggregated statistics
    """
    total_sites = 0
    total_lactylated = 0
    total_non_lactylated = 0
    
    frame_stats = {}
    
    for frame_name, predictions in frame_predictions.items():
        lactylated = [p for p in predictions if p['label'] == '+']
        non_lactylated = [p for p in predictions if p['label'] == '-']
        
        frame_stats[frame_name] = {
            'total_sites': len(predictions),
            'lactylated_sites': len(lactylated),
            'non_lactylated_sites': len(non_lactylated),
            'avg_score': np.mean([p['score'] for p in predictions]) if predictions else 0,
            'avg_confidence': np.mean([p['confidence'] for p in predictions]) if predictions else 0
        }
        
        total_sites += len(predictions)
        total_lactylated += len(lactylated)
        total_non_lactylated += len(non_lactylated)
    
    summary = {
        'total_sites': total_sites,
        'total_lactylated': total_lactylated,
        'total_non_lactylated': total_non_lactylated,
        'frame_statistics': frame_stats
    }
    
    return summary

