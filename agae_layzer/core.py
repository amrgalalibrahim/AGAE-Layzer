"""AGAE-Layzer prediction core: input detection, translation, lysine windows, features and trained models."""
import os
import joblib
import numpy as np

from . import agae_translate as T
from .features import encode_many, HALF

MODEL_DIR = os.environ.get("AGAE_MODEL_DIR", os.path.join(os.path.dirname(__file__), "..", "models"))
MODEL_FILES = {"v1": "agae_layzer_v1.joblib", "v2": "agae_layzer_v2.joblib"}
_cache = {}


def load_model(version):
    version = version.lower()
    if version not in MODEL_FILES:
        raise ValueError("version must be 'v1' or 'v2'")
    if version not in _cache:
        _cache[version] = joblib.load(os.path.join(MODEL_DIR, MODEL_FILES[version]))
    return _cache[version]


def protein_windows(protein):
    p = T.clean(protein)
    for i, aa in enumerate(p):
        if aa == "K":
            yield i, p[max(0, i - HALF):i].rjust(HALF, "X") + "K" + p[i + 1:i + 1 + HALF].ljust(HALF, "X")


def lysine_records(seq_id, sequence, min_orf=30, require_atg=False, rna_double_stranded=False, cds=False):
    """Return one record per lysine with its window and coordinates (nucleic-acid input is translated)."""
    seq_type = T.detect_type(sequence)
    recs = []
    if seq_type == "PROTEIN":
        for i, w in protein_windows(sequence):
            recs.append(dict(seq_id=seq_id, input_type=seq_type, strand=".", frame=0, orf_aa_start=1,
                             k_pos_in_orf=i + 1, codon="", nt_start="", nt_end="", window=w))
    else:
        for orf in T.orfs(sequence, seq_type, min_orf, require_atg, rna_double_stranded, cds):
            for r in T.lysine_sites(orf):
                r.update(seq_id=seq_id, input_type=seq_type)
                recs.append(r)
    return seq_type, recs


def predict(records, version="v2", threshold=0.5):
    if not records:
        return records
    model = load_model(version)
    prob = model.predict_proba(encode_many([r["window"] for r in records]))[:, 1]
    for r, p in zip(records, prob):
        r["probability"] = round(float(p), 4)
        r["prediction"] = "Kla" if p >= threshold else "non-Kla"
        r["model"] = "AGAE-Layzer V1.0.0" if version == "v1" else "AGAE-Layzer V2.0.0"
    return records


def read_fasta_text(text):
    name, buf, out = None, [], []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if name is not None or buf:
                out.append((name or "query", "".join(buf)))
            name, buf = line[1:].split()[0] if len(line) > 1 else "query", []
        else:
            buf.append(line)
    if name is not None or buf:
        out.append((name or "query", "".join(buf)))
    return out


COLUMNS = ["seq_id", "input_type", "strand", "frame", "orf_aa_start", "k_pos_in_orf", "codon",
           "nt_start", "nt_end", "window", "probability", "prediction", "model"]
