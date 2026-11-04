"""AGAE-Layzer feature encoding for 31-residue lysine-centred windows.

Feature groups (dimension):
  AAC   - amino acid composition of the 30 flanking residues (20)
  EVO   - BLOSUM62 substitution profile of each flanking position (30 x 20 = 600)
  PHY   - seven physicochemical scales per flanking position (30 x 7 = 210)
  SS    - Chou-Fasman helix / strand / turn propensities per flanking position (30 x 3 = 90)
Total 920. Padding character 'X' (and any non-standard residue) is encoded as zeros.
"""
import numpy as np

AA = "ARNDCQEGHILKMFPSTWYV"
HALF = 15
WIN = 2 * HALF + 1

_B62_ROWS = """
A  4 -1 -2 -2  0 -1 -1  0 -2 -1 -1 -1 -1 -2 -1  1  0 -3 -2  0
R -1  5  0 -2 -3  1  0 -2  0 -3 -2  2 -1 -3 -2 -1 -1 -3 -2 -3
N -2  0  6  1 -3  0  0  0  1 -3 -3  0 -2 -3 -2  1  0 -4 -2 -3
D -2 -2  1  6 -3  0  2 -1 -1 -3 -4 -1 -3 -3 -1  0 -1 -4 -3 -3
C  0 -3 -3 -3  9 -3 -4 -3 -3 -1 -1 -3 -1 -2 -3 -1 -1 -2 -2 -1
Q -1  1  0  0 -3  5  2 -2  0 -3 -2  1  0 -3 -1  0 -1 -2 -1 -2
E -1  0  0  2 -4  2  5 -2  0 -3 -3  1 -2 -3 -1  0 -1 -3 -2 -2
G  0 -2  0 -1 -3 -2 -2  6 -2 -4 -4 -2 -3 -3 -2  0 -2 -2 -3 -3
H -2  0  1 -1 -3  0  0 -2  8 -3 -3 -1 -2 -1 -2 -1 -2 -2  2 -3
I -1 -3 -3 -3 -1 -3 -3 -4 -3  4  2 -3  1  0 -3 -2 -1 -3 -1  3
L -1 -2 -3 -4 -1 -2 -3 -4 -3  2  4 -2  2  0 -3 -2 -1 -2 -1  1
K -1  2  0 -1 -3  1  1 -2 -1 -3 -2  5 -1 -3 -1  0 -1 -3 -2 -2
M -1 -1 -2 -3 -1  0 -2 -3 -2  1  2 -1  5  0 -2 -1 -1 -1 -1  1
F -2 -3 -3 -3 -2 -3 -3 -3 -1  0  0 -3  0  6 -4 -2 -2  1  3 -1
P -1 -2 -2 -1 -3 -1 -1 -2 -2 -3 -3 -1 -2 -4  7 -1 -1 -4 -3 -2
S  1 -1  1  0 -1  0  0  0 -1 -2 -2  0 -1 -2 -1  4  1 -3 -2 -2
T  0 -1  0 -1 -1 -1 -1 -2 -2 -1 -1 -1 -1 -2 -1  1  5 -2 -2  0
W -3 -3 -4 -4 -2 -2 -3 -2 -2 -3 -2 -3 -1  1 -4 -3 -2 11  2 -3
Y -2 -2 -2 -3 -2 -1 -2 -3  2 -1 -1 -2 -1  3 -3 -2 -2  2  7 -1
V  0 -3 -3 -3 -1 -2 -2 -3 -3  3  1 -2  1 -1 -2 -2  0 -3 -1  4
"""
BLOSUM62 = {}
for line in _B62_ROWS.strip().splitlines():
    p = line.split()
    BLOSUM62[p[0]] = np.array([float(v) for v in p[1:]]) / 11.0

# physicochemical scales (raw values, z-scored across the 20 amino acids below)
_PHY = {
    #     KD    HoppWoods  mass     pI     charge  GranthamPol  GranthamVol
    "A": (1.8, -0.5, 71.08, 6.00, 0.0, 8.1, 31.0),
    "R": (-4.5, 3.0, 156.19, 10.76, 1.0, 10.5, 124.0),
    "N": (-3.5, 0.2, 114.10, 5.41, 0.0, 11.6, 56.0),
    "D": (-3.5, 3.0, 115.09, 2.77, -1.0, 13.0, 54.0),
    "C": (2.5, -1.0, 103.14, 5.07, 0.0, 5.5, 55.0),
    "Q": (-3.5, 0.2, 128.13, 5.65, 0.0, 10.5, 85.0),
    "E": (-3.5, 3.0, 129.12, 3.22, -1.0, 12.3, 83.0),
    "G": (-0.4, 0.0, 57.05, 5.97, 0.0, 9.0, 3.0),
    "H": (-3.2, -0.5, 137.14, 7.59, 0.1, 10.4, 96.0),
    "I": (4.5, -1.8, 113.16, 6.02, 0.0, 5.2, 111.0),
    "L": (3.8, -1.8, 113.16, 5.98, 0.0, 4.9, 111.0),
    "K": (-3.9, 3.0, 128.17, 9.74, 1.0, 11.3, 119.0),
    "M": (1.9, -1.3, 131.19, 5.74, 0.0, 5.7, 105.0),
    "F": (2.8, -2.5, 147.18, 5.48, 0.0, 5.2, 132.0),
    "P": (-1.6, 0.0, 97.12, 6.30, 0.0, 8.0, 32.5),
    "S": (-0.8, 0.3, 87.08, 5.68, 0.0, 9.2, 32.0),
    "T": (-0.7, -0.4, 101.10, 5.60, 0.0, 8.6, 61.0),
    "W": (-0.9, -3.4, 186.21, 5.89, 0.0, 5.4, 170.0),
    "Y": (-1.3, -2.3, 163.18, 5.66, 0.0, 6.2, 136.0),
    "V": (4.2, -1.5, 99.13, 5.96, 0.0, 5.9, 84.0),
}
PHY_NAMES = ["hydrophobicity_KD", "hydrophilicity_HW", "residue_mass", "pI",
             "charge_pH7", "polarity_Grantham", "volume_Grantham"]
_m = np.array([_PHY[a] for a in AA])
_m = (_m - _m.mean(0)) / _m.std(0)
PHY = {a: _m[i] for i, a in enumerate(AA)}

# Chou-Fasman conformational propensities (helix, strand, turn), centred at 1
_CF = {
    "A": (1.42, 0.83, 0.66), "R": (0.98, 0.93, 0.95), "N": (0.67, 0.89, 1.56), "D": (1.01, 0.54, 1.46),
    "C": (0.70, 1.19, 1.19), "Q": (1.11, 1.10, 0.98), "E": (1.51, 0.37, 0.74), "G": (0.57, 0.75, 1.56),
    "H": (1.00, 0.87, 0.95), "I": (1.08, 1.60, 0.47), "L": (1.21, 1.30, 0.59), "K": (1.16, 0.74, 1.01),
    "M": (1.45, 1.05, 0.60), "F": (1.13, 1.38, 0.60), "P": (0.57, 0.55, 1.52), "S": (0.77, 0.75, 1.43),
    "T": (0.83, 1.19, 0.96), "W": (1.08, 1.37, 0.96), "Y": (0.69, 1.47, 1.14), "V": (1.06, 1.70, 0.50),
}
SS = {a: np.array(v) - 1.0 for a, v in _CF.items()}

ZERO20, ZERO7, ZERO3 = np.zeros(20), np.zeros(7), np.zeros(3)


def flanks(win):
    assert len(win) == WIN and win[HALF] == "K", win
    return win[:HALF] + win[HALF + 1:]


def encode(win):
    f = flanks(win.upper())
    aac = np.array([f.count(a) for a in AA], float) / len(f)
    evo = np.concatenate([BLOSUM62.get(a, ZERO20) for a in f])
    phy = np.concatenate([PHY.get(a, ZERO7) for a in f])
    ss = np.concatenate([SS.get(a, ZERO3) for a in f])
    return np.concatenate([aac, evo, phy, ss])


def feature_groups():
    g = {"AAC": (0, 20), "EVO": (20, 620), "PHY": (620, 830), "SS": (830, 920)}
    return {k: np.arange(*v) for k, v in g.items()}


def encode_many(windows):
    return np.vstack([encode(w) for w in windows])


def centre_window(seq, half=HALF):
    """Cut a 31-mer from a longer odd-length window centred on K."""
    c = len(seq) // 2
    return seq[c - half:c + half + 1]
