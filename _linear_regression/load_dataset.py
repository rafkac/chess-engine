#!/usr/bin/env python3
"""
Load and prepare chess evaluation datasets for training.

Supports three common formats:
  1. Kaggle "Chess Evaluations" (ronakbadhe) — CSV with 'FEN' and 'Evaluation' columns
  2. Lichess evaluation database — JSONL with 'fen' and 'evals' fields
  3. Generic CSV — any CSV with 'fen' and a centipawn or pawn-scale eval column

Usage:
    python load_dataset.py --input chessData.csv --format kaggle \
                           --output data/training_set.csv \
                           --sample 50000 --min-depth 10

See TUNING_README.md for which dataset to download.
"""

import argparse
import csv
import json
import os
import random
import sys
import time


def load_kaggle_csv(path: str, min_depth: int = 0) -> list[tuple[str, float]]:
    """
    Load the Kaggle "Chess Evaluations" dataset (ronakbadhe/chess-evaluations).
    
    Expected CSV columns: FEN, Evaluation
    Evaluation format: integer centipawns (e.g. 35) or mate string (e.g. #+3, #-5)
    
    Args:
        path: Path to the downloaded CSV (e.g. chessData.csv)
        min_depth: Not applicable for this dataset (no depth column), ignored.
    
    Returns:
        List of (fen, eval_in_pawns) tuples. Mate positions are excluded.
    """
    positions = []
    skipped_mate = 0
    skipped_parse = 0

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fen = row.get('FEN', '').strip()
            eval_str = row.get('Evaluation', '').strip()
            
            if not fen or not eval_str:
                skipped_parse += 1
                continue

            # Skip mate evaluations (start with # or contain 'mate')
            if eval_str.startswith('#') or 'mate' in eval_str.lower():
                skipped_mate += 1
                continue

            try:
                # Kaggle format: centipawns as integer
                cp = int(eval_str)
                score_pawns = cp / 100.0
            except ValueError:
                try:
                    score_pawns = float(eval_str)
                except ValueError:
                    skipped_parse += 1
                    continue

            # Clamp extreme evals
            score_pawns = max(-15.0, min(15.0, score_pawns))
            positions.append((fen, score_pawns))

    print(f"  Loaded: {len(positions)} positions")
    print(f"  Skipped: {skipped_mate} mate, {skipped_parse} parse errors")
    return positions


def load_lichess_jsonl(path: str, min_depth: int = 10) -> list[tuple[str, float]]:
    """
    Load the Lichess evaluation database (lichess_db_eval.jsonl).
    
    Each line is JSON:
      {"fen": "...", "evals": [{"knodes": ..., "depth": ..., "pvs": [{"cp": ...}]}]}
    
    Takes the deepest evaluation for each position.
    
    Args:
        path: Path to the JSONL file (can be decompressed)
        min_depth: Minimum Stockfish depth to include (default 10)
    
    Returns:
        List of (fen, eval_in_pawns) tuples.
    """
    positions = []
    skipped_depth = 0
    skipped_mate = 0
    skipped_parse = 0

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                skipped_parse += 1
                continue

            fen = data.get('fen', '')
            evals = data.get('evals', [])
            if not fen or not evals:
                skipped_parse += 1
                continue

            # Find the deepest evaluation
            best_eval = None
            best_depth = 0
            for ev in evals:
                depth = ev.get('depth', 0)
                if depth > best_depth:
                    pvs = ev.get('pvs', [])
                    if pvs and 'cp' in pvs[0]:
                        best_eval = pvs[0]['cp']
                        best_depth = depth
                    elif pvs and 'mate' in pvs[0]:
                        best_eval = None  # mate — skip
                        best_depth = depth

            if best_depth < min_depth:
                skipped_depth += 1
                continue
            if best_eval is None:
                skipped_mate += 1
                continue

            score_pawns = best_eval / 100.0
            score_pawns = max(-15.0, min(15.0, score_pawns))

            # Lichess FENs may be missing halfmove/fullmove clocks — add defaults
            if fen.count(' ') == 3:
                fen += ' 0 1'

            positions.append((fen, score_pawns))

    print(f"  Loaded: {len(positions)} positions (min depth {min_depth})")
    print(f"  Skipped: {skipped_mate} mate, {skipped_depth} low depth, {skipped_parse} parse errors")
    return positions


def load_generic_csv(path: str, fen_col: str = 'fen', eval_col: str = 'eval',
                     eval_scale: str = 'pawns', min_depth: int = 0) -> list[tuple[str, float]]:
    """
    Load any CSV with FEN and evaluation columns.
    
    Args:
        path: CSV path
        fen_col: Column name for FEN strings
        eval_col: Column name for evaluations
        eval_scale: 'pawns' (1.5 = 1.5 pawns) or 'centipawns' (150 = 1.5 pawns)
    """
    positions = []
    skipped = 0

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fen = row.get(fen_col, '').strip()
            eval_str = row.get(eval_col, '').strip()
            
            if not fen or not eval_str:
                skipped += 1
                continue

            # Skip mate strings
            if '#' in eval_str or 'mate' in eval_str.lower() or 'M' in eval_str:
                skipped += 1
                continue

            try:
                score = float(eval_str)
                if eval_scale == 'centipawns':
                    score /= 100.0
                score = max(-15.0, min(15.0, score))
                positions.append((fen, score))
            except ValueError:
                skipped += 1

    print(f"  Loaded: {len(positions)} positions")
    print(f"  Skipped: {skipped}")
    return positions


def save_prepared_dataset(positions: list[tuple[str, float]], output_path: str):
    """Save as a standardised CSV with 'fen' and 'score' columns (score in pawns)."""
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['fen', 'score'])
        for fen, score in positions:
            writer.writerow([fen, f"{score:.4f}"])
    print(f"  Saved: {len(positions)} positions to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Load and prepare chess evaluation datasets")
    parser.add_argument("--input", required=True, help="Path to input dataset file")
    parser.add_argument("--format", choices=['kaggle', 'lichess', 'csv'],
                        default='kaggle',
                        help="Dataset format: 'kaggle' (ronakbadhe CSV), "
                             "'lichess' (JSONL), 'csv' (generic)")
    parser.add_argument("--output", default="data/training_set.csv",
                        help="Output CSV path")
    parser.add_argument("--sample", type=int, default=50000,
                        help="Random sample size (0 = use all)")
    parser.add_argument("--min-depth", type=int, default=10,
                        help="Minimum Stockfish depth (Lichess format only)")
    parser.add_argument("--fen-col", default="fen",
                        help="FEN column name (generic CSV)")
    parser.add_argument("--eval-col", default="eval",
                        help="Eval column name (generic CSV)")
    parser.add_argument("--eval-scale", choices=['pawns', 'centipawns'],
                        default='pawns', help="Eval scale (generic CSV)")
    args = parser.parse_args()

    print(f"=== Loading Dataset ({args.format} format) ===")
    print(f"  Input: {args.input}")
    start = time.time()

    if args.format == 'kaggle':
        positions = load_kaggle_csv(args.input)
    elif args.format == 'lichess':
        positions = load_lichess_jsonl(args.input, min_depth=args.min_depth)
    elif args.format == 'csv':
        positions = load_generic_csv(args.input, args.fen_col, args.eval_col, args.eval_scale)

    # Random sample
    if args.sample > 0 and len(positions) > args.sample:
        print(f"\n  Sampling {args.sample} from {len(positions)} positions...")
        random.shuffle(positions)
        positions = positions[:args.sample]

    print(f"\n  Total time: {time.time() - start:.1f}s")
    save_prepared_dataset(positions, args.output)


if __name__ == "__main__":
    main()
