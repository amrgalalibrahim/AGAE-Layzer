"""Command-line interface: python -m agae_layzer.cli input.fasta -o predictions.tsv --version v2"""
import argparse, csv, sys
from .core import lysine_records, predict, read_fasta_text, COLUMNS


def main():
    ap = argparse.ArgumentParser(description="AGAE-Layzer lysine lactylation site prediction")
    ap.add_argument("fasta")
    ap.add_argument("-o", "--out", default="agae_layzer_predictions.tsv")
    ap.add_argument("--version", choices=["v1", "v2"], default="v2")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--min-orf", type=int, default=30)
    ap.add_argument("--require-atg", action="store_true")
    ap.add_argument("--rna-double-stranded", action="store_true")
    ap.add_argument("--cds", action="store_true", help="nucleic-acid input is an annotated CDS (frame +1 only)")
    a = ap.parse_args()
    n = 0
    with open(a.fasta) as fh, open(a.out, "w", newline="") as out:
        w = csv.DictWriter(out, COLUMNS, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for sid, seq in read_fasta_text(fh.read()):
            _, recs = lysine_records(sid, seq, a.min_orf, a.require_atg, a.rna_double_stranded, a.cds)
            for r in predict(recs, a.version, a.threshold):
                w.writerow(r); n += 1
    print(f"{n} lysines written to {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
