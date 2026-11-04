#!/usr/bin/env python3
"""
AGAE-Layzer - nucleic-acid handling module (revised, R1 point 1 / R3 point 4).

Rules
-----
* Protein input  -> used as is.
* RNA input (contains U, no T) -> 3 forward frames only (single-stranded, 5'->3').
  Six frames are produced ONLY if the user sets --rna-double-stranded (e.g. cDNA
  written with U), because an mRNA has no biologically meaningful reverse strand.
* DNA input -> 6 frames (3 forward + 3 on the reverse complement).
* Stop codons: each frame is split at stop codons ('*'). Every stop-to-stop
  segment >= --min-orf aa is kept as a candidate ORF (default 30 aa).
  With --require-atg the segment is trimmed to start at the first Met.
* Frame choice: all ORFs passing the filters are scored; the frame is NOT guessed.
  If --cds is given the sequence is treated as an annotated coding sequence and
  only frame +1 is used (translation stops at the first in-frame stop).
* Every lysine is reported with protein position, strand, frame, codon (AAA/AAG)
  and 1-based nucleotide coordinates on the input sequence, so predictions can be
  mapped back to genomic/transcript coordinates.
Standard genetic code (NCBI table 1); ambiguous codons -> 'X'.
"""
import argparse, csv, re, sys

BASES = "TCAG"
AAS = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
CODON = {a + b + c: AAS[16 * i + 4 * j + k]
         for i, a in enumerate(BASES) for j, b in enumerate(BASES) for k, c in enumerate(BASES)}
COMP = str.maketrans("ACGTN", "TGCAN")


def clean(seq):
    return re.sub(r"[^A-Za-z*]", "", seq).upper()


def detect_type(seq):
    s = clean(seq)
    nuc = sum(s.count(c) for c in "ACGTUN")
    if len(s) and nuc / len(s) >= 0.90:
        if "U" in s and "T" not in s:
            return "RNA"
        return "DNA"
    return "PROTEIN"


def revcomp(dna):
    return dna.translate(COMP)[::-1]


def translate(dna, offset=0):
    return "".join(CODON.get(dna[i:i + 3], "X") for i in range(offset, len(dna) - 2, 3))


def frames(seq, seq_type, rna_ds=False):
    """Yield (strand, frame_number, nucleotide_string_as_DNA)."""
    dna = clean(seq).replace("U", "T")
    for f in range(3):
        yield "+", f + 1, dna, f
    if seq_type == "DNA" or (seq_type == "RNA" and rna_ds):
        rc = revcomp(dna)
        for f in range(3):
            yield "-", f + 1, rc, f


def orfs(seq, seq_type, min_orf=30, require_atg=False, rna_ds=False, cds=False):
    """Return list of dicts: protein segment + mapping info."""
    L = len(clean(seq))
    out = []
    if cds:
        dna = clean(seq).replace("U", "T")
        prot = translate(dna, 0).split("*")[0]
        out.append(dict(strand="+", frame=1, aa_start=0, protein=prot, dna=dna, offset=0, L=L))
        return out
    for strand, fnum, dna, off in frames(seq, seq_type, rna_ds):
        prot = translate(dna, off)
        pos = 0
        for seg in prot.split("*"):
            start = pos
            s = seg
            if require_atg:
                m = s.find("M")
                s = s[m:] if m >= 0 else ""
                start = pos + (m if m >= 0 else 0)
            if len(s) >= min_orf:
                out.append(dict(strand=strand, frame=fnum, aa_start=start, protein=s, dna=dna, offset=off, L=L))
            pos += len(seg) + 1
    return out


def lysine_sites(orf, window=15):
    """Yield per-lysine records with 31-aa window (X padded) and nt coordinates."""
    p = orf["protein"]
    for i, aa in enumerate(p):
        if aa != "K":
            continue
        left = p[max(0, i - window):i].rjust(window, "X")
        right = p[i + 1:i + 1 + window].ljust(window, "X")
        codon_start = orf["offset"] + 3 * (orf["aa_start"] + i)      # 0-based on the strand used
        codon = orf["dna"][codon_start:codon_start + 3]
        if orf["strand"] == "+":
            nt_start, nt_end = codon_start + 1, codon_start + 3
        else:                                                         # back to input coordinates
            nt_end = orf["L"] - codon_start
            nt_start = nt_end - 2
        yield dict(strand=orf["strand"], frame=orf["frame"], orf_aa_start=orf["aa_start"] + 1,
                   k_pos_in_orf=i + 1, codon=codon, nt_start=nt_start, nt_end=nt_end,
                   window=left + "K" + right)


def read_fasta(path):
    name, buf = None, []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith(">"):
                if name is not None:
                    yield name, "".join(buf)
                name, buf = line[1:].split()[0], []
            elif line:
                buf.append(line)
    if name is not None:
        yield name, "".join(buf)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fasta")
    ap.add_argument("-o", "--out", default="lysine_windows.tsv")
    ap.add_argument("--min-orf", type=int, default=30)
    ap.add_argument("--require-atg", action="store_true")
    ap.add_argument("--rna-double-stranded", action="store_true")
    ap.add_argument("--cds", action="store_true", help="input is annotated CDS: frame +1 only")
    a = ap.parse_args()
    cols = ["seq_id", "input_type", "strand", "frame", "orf_aa_start", "k_pos_in_orf",
            "codon", "nt_start", "nt_end", "window"]
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, cols, delimiter="\t")
        w.writeheader()
        for sid, seq in read_fasta(a.fasta):
            t = detect_type(seq)
            if t == "PROTEIN":
                orf_list = [dict(strand=".", frame=0, aa_start=0, protein=clean(seq), dna="", offset=0, L=0)]
                for i, aa in enumerate(orf_list[0]["protein"]):
                    if aa == "K":
                        p = orf_list[0]["protein"]
                        win = p[max(0, i - 15):i].rjust(15, "X") + "K" + p[i + 1:i + 16].ljust(15, "X")
                        w.writerow(dict(seq_id=sid, input_type=t, strand=".", frame=0, orf_aa_start=1,
                                        k_pos_in_orf=i + 1, codon="", nt_start="", nt_end="", window=win))
                continue
            for orf in orfs(seq, t, a.min_orf, a.require_atg, a.rna_double_stranded, a.cds):
                for rec in lysine_sites(orf):
                    rec.update(seq_id=sid, input_type=t)
                    w.writerow(rec)
    print("written", a.out, file=sys.stderr)


if __name__ == "__main__":
    main()
