"""
Sequence Type Detection Module
Detects whether input sequence is Protein, DNA, or RNA
"""

def detect_sequence_type(sequence):
    """
    Detect the type of biological sequence.
    
    Args:
        sequence (str): The input sequence string
        
    Returns:
        str: "PROTEIN", "DNA", or "RNA"
    """
    # Remove whitespace and convert to uppercase
    clean_seq = sequence.replace(" ", "").replace("\n", "").replace("\r", "").upper()
    
    # Remove FASTA header if present
    if ">" in clean_seq:
        lines = clean_seq.split("\n")
        clean_seq = "".join([line for line in lines if not line.startswith(">")])
    
    # Define character sets
    nucleotides = set("ATGC")
    rna_specific = set("U")
    amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
    
    # Count character types
    nucleotide_count = sum(1 for c in clean_seq if c in nucleotides)
    rna_count = sum(1 for c in clean_seq if c in rna_specific)
    amino_acid_only_count = sum(1 for c in clean_seq if c in amino_acids and c not in nucleotides)
    
    total_valid = len([c for c in clean_seq if c.isalpha()])
    
    if total_valid == 0:
        return "UNKNOWN"
    
    nucleotide_ratio = nucleotide_count / total_valid
    rna_ratio = rna_count / total_valid
    
    # If contains U, likely RNA
    if rna_ratio > 0.01:
        return "RNA"
    
    # If >90% are valid nucleotides (ATGC), it's DNA
    if nucleotide_ratio > 0.90:
        return "DNA"
    
    # If contains amino acids not in nucleotides, it's protein
    if amino_acid_only_count > 0:
        return "PROTEIN"
    
    # Default to protein if ambiguous
    return "PROTEIN"


def clean_sequence(sequence):
    """
    Clean and prepare sequence for processing.
    
    Args:
        sequence (str): Raw input sequence
        
    Returns:
        str: Cleaned uppercase sequence without whitespace or headers
    """
    # Remove FASTA headers
    lines = sequence.strip().split("\n")
    clean_lines = [line for line in lines if not line.startswith(">")]
    
    # Join and clean
    clean_seq = "".join(clean_lines)
    clean_seq = clean_seq.replace(" ", "").replace("\r", "").upper()
    
    return clean_seq


def validate_sequence(sequence, seq_type):
    """
    Validate sequence contains only valid characters for its type.
    
    Args:
        sequence (str): The sequence to validate
        seq_type (str): "PROTEIN", "DNA", or "RNA"
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if seq_type == "PROTEIN":
        valid_chars = set("ACDEFGHIKLMNPQRSTVWY")
        invalid = set(sequence) - valid_chars
        if invalid:
            return False, f"Invalid amino acid characters found: {', '.join(sorted(invalid))}"
    
    elif seq_type == "DNA":
        valid_chars = set("ATGC")
        invalid = set(sequence) - valid_chars
        if invalid:
            return False, f"Invalid DNA nucleotide characters found: {', '.join(sorted(invalid))}"
    
    elif seq_type == "RNA":
        valid_chars = set("AUGC")
        invalid = set(sequence) - valid_chars
        if invalid:
            return False, f"Invalid RNA nucleotide characters found: {', '.join(sorted(invalid))}"
    
    return True, ""

