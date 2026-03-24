"""
Six-Frame Translation Module
Translates nucleic acid sequences in all 6 reading frames
"""

# Standard genetic code codon table
CODON_TABLE = {
    'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'ATG': 'M',
    'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
    'AAC': 'N', 'AAT': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGC': 'S', 'AGT': 'S', 'AGA': 'R', 'AGG': 'R',
    'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
    'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
    'CAC': 'H', 'CAT': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
    'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
    'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
    'GAC': 'D', 'GAT': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
    'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
    'TTC': 'F', 'TTT': 'F', 'TTA': 'L', 'TTG': 'L',
    'TAC': 'Y', 'TAT': 'Y', 'TAA': '*', 'TAG': '*',
    'TGC': 'C', 'TGT': 'C', 'TGA': '*', 'TGG': 'W',
    # RNA codons
    'AUA': 'I', 'AUC': 'I', 'AUU': 'I', 'AUG': 'M',
    'UCA': 'S', 'UCC': 'S', 'UCG': 'S', 'UCU': 'S',
    'UUC': 'F', 'UUU': 'F', 'UUA': 'L', 'UUG': 'L',
    'UAC': 'Y', 'UAU': 'Y', 'UAA': '*', 'UAG': '*',
    'UGC': 'C', 'UGU': 'C', 'UGA': '*', 'UGG': 'W',
    'CUA': 'L', 'CUC': 'L', 'CUG': 'L', 'CUU': 'L',
    'GUA': 'V', 'GUC': 'V', 'GUG': 'V', 'GUU': 'V',
}


def translate_frame(sequence, frame_offset=0):
    """
    Translate a single reading frame.
    
    Args:
        sequence (str): Nucleotide sequence
        frame_offset (int): Starting position (0, 1, or 2)
        
    Returns:
        str: Translated protein sequence
    """
    protein = ""
    start = frame_offset
    
    for i in range(start, len(sequence) - 2, 3):
        codon = sequence[i:i + 3]
        if len(codon) == 3:
            amino_acid = CODON_TABLE.get(codon, 'X')  # X for unknown
            protein += amino_acid
    
    return protein


def reverse_complement(sequence):
    """
    Generate reverse complement of a nucleotide sequence.
    
    Args:
        sequence (str): Nucleotide sequence (DNA or RNA)
        
    Returns:
        str: Reverse complement sequence
    """
    # Complement mapping for both DNA and RNA
    complement = {
        'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
        'U': 'A',  # RNA specific
    }
    
    # If RNA, convert U to A in complement
    if 'U' in sequence:
        complement['A'] = 'U'
    
    rev_comp = ''.join(complement.get(base, 'N') for base in reversed(sequence))
    return rev_comp


def six_frame_translation(sequence):
    """
    Translate nucleotide sequence in all 6 reading frames.
    
    Args:
        sequence (str): Nucleotide sequence (DNA or RNA)
        
    Returns:
        dict: Dictionary with frame names as keys and translated proteins as values
            Format: {'+1': protein, '+2': protein, '+3': protein,
                     '-1': protein, '-2': protein, '-3': protein}
    """
    frames = {}
    
    # Forward strand frames (+1, +2, +3)
    for frame in range(3):
        frame_name = f"+{frame + 1}"
        frames[frame_name] = translate_frame(sequence, frame)
    
    # Reverse complement strand frames (-1, -2, -3)
    rev_comp = reverse_complement(sequence)
    for frame in range(3):
        frame_name = f"-{frame + 1}"
        frames[frame_name] = translate_frame(rev_comp, frame)
    
    return frames


def get_frame_info(frames):
    """
    Get summary information about translated frames.
    
    Args:
        frames (dict): Dictionary of translated frames
        
    Returns:
        dict: Summary information including lengths and K counts
    """
    info = {}
    
    for frame_name, protein in frames.items():
        k_count = protein.count('K')
        stop_count = protein.count('*')
        
        info[frame_name] = {
            'length': len(protein),
            'lysine_count': k_count,
            'stop_codons': stop_count,
            'sequence': protein
        }
    
    return info


def find_longest_orf(protein_sequence):
    """
    Find the longest open reading frame (ORF) in a protein sequence.
    An ORF is defined as sequence between start (M) and stop (*) codons.
    
    Args:
        protein_sequence (str): Translated protein sequence
        
    Returns:
        tuple: (start_pos, end_pos, orf_sequence) or None if no ORF found
    """
    orfs = []
    
    # Find all ORFs (M to *)
    start_positions = [i for i, aa in enumerate(protein_sequence) if aa == 'M']
    
    for start in start_positions:
        # Find next stop codon
        for end in range(start + 1, len(protein_sequence)):
            if protein_sequence[end] == '*':
                orf = protein_sequence[start:end]
                orfs.append((start, end, orf))
                break
    
    # Return longest ORF
    if orfs:
        longest = max(orfs, key=lambda x: len(x[2]))
        return longest
    
    return None

