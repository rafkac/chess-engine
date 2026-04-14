#!/usr/bin/env python3
"""
Train evaluation weights using linear regression.

The PST/material component is FIXED.  We subtract it from the Stockfish
target, so the regression learns optimal weights for everything else:

    target_residual = stockfish_eval - pst_baseline(board)
    residual ≈ dot(weights, tunable_features) + bias

Usage:
    python train_weights.py --data data/training_set.csv \
                            --output ../src/chess_engine/learned_weights.json \
                            --alpha 1.0
"""

import argparse
import csv
import json
import os
import sys
import time

import numpy as np
import chess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from chess_engine.features import (
    extract_features, compute_pst_baseline,
    FEATURE_NAMES, NUM_FEATURES
)


def load_dataset(csv_path: str) -> tuple[list[str], np.ndarray]:
    """Load FENs and scores from the prepared CSV."""
    fens = []
    scores = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fens.append(row['fen'])
            scores.append(float(row['score']))
    return fens, np.array(scores, dtype=np.float64)


def extract_all(fens: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """
    For each position, extract:
      - tunable features  (N, NUM_FEATURES)
      - PST baseline      (N,)
    """
    N = len(fens)
    X = np.zeros((N, NUM_FEATURES), dtype=np.float64)
    baselines = np.zeros(N, dtype=np.float64)

    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        X[i] = extract_features(board)
        baselines[i] = compute_pst_baseline(board)

        if (i + 1) % 5000 == 0:
            print(f"  Extracted: {i+1}/{N}")

    return X, baselines


def train_ridge(X: np.ndarray, y: np.ndarray, alpha: float = 1.0):
    """
    Ridge regression:  w = argmin ||Xw - y||² + α||w||²
    
    Returns (weights, bias, stats).
    """
    N, D = X.shape

    # Add bias column
    X_b = np.hstack([X, np.ones((N, 1))])

    I = np.eye(D + 1)
    I[-1, -1] = 0  # don't regularise bias

    A = X_b.T @ X_b + alpha * I
    b = X_b.T @ y
    w = np.linalg.solve(A, b)

    weights = w[:-1]
    bias = w[-1]

    # Metrics
    y_pred = X_b @ w
    residuals = y - y_pred
    mse = float(np.mean(residuals ** 2))
    rmse = float(np.sqrt(mse))
    mae = float(np.mean(np.abs(residuals)))
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0

    stats = {
        'mse': mse, 'rmse': rmse, 'mae': mae, 'r2': r2,
        'n_samples': int(N), 'n_features': int(D),
    }
    return weights, bias, stats


def print_results(weights, bias, train_stats, test_stats):
    """Pretty-print learned weights and metrics."""

    # Hand-tuned defaults (from ClassicEvaluator, in centipawns → pawns)
    hand_tuned = {
        'knight_mobility': 0.04, 'bishop_mobility': 0.05,
        'rook_mobility': 0.02,   'queen_mobility': 0.01,
        'doubled_pawns': -0.15,  'isolated_pawns': -0.20,
        'passed_pawn_count': 0.20, 'passed_pawn_advancement': 0.10,
        'bishop_pair': 0.30,     'tempo': 0.15,
    }

    print("\n" + "=" * 70)
    print("LEARNED WEIGHTS  (PST/material fixed, tuning remaining features)")
    print("=" * 70)
    print(f"  {'Feature':<25} {'Hand-tuned':>10} {'Learned':>10} {'Change':>10}")
    print(f"  {'-'*55}")

    for name, w in zip(FEATURE_NAMES, weights):
        ht = hand_tuned.get(name, 0.0)
        delta = w - ht
        arrow = "↑" if delta > 0.001 else "↓" if delta < -0.001 else "≈"
        print(f"  {name:<25} {ht:>10.4f} {w:>10.4f} {arrow} {delta:>+8.4f}")

    print(f"  {'bias':<25} {'0.0':>10} {bias:>10.4f}")
    print(f"  {'-'*55}")

    print(f"\n  Training ({train_stats['n_samples']:,} samples):")
    print(f"    RMSE: {train_stats['rmse']:.4f} pawns")
    print(f"    MAE:  {train_stats['mae']:.4f} pawns")
    print(f"    R²:   {train_stats['r2']:.4f}")

    if test_stats:
        print(f"\n  Test ({test_stats['n_samples']} samples):")
        print(f"    RMSE: {test_stats['rmse']:.4f} pawns")
        print(f"    MAE:  {test_stats['mae']:.4f} pawns")
        print(f"    R²:   {test_stats['r2']:.4f}")

        abs_err = test_stats.get('abs_errors')
        if abs_err is not None:
            print(f"\n  Error distribution (test set):")
            for t in [0.25, 0.50, 1.00, 2.00]:
                pct = 100 * np.mean(abs_err < t)
                print(f"    Within ±{t:.2f} pawns: {pct:.1f}%")


def save_weights(weights, bias, stats, output_path):
    """Save weights to JSON."""
    data = {
        'feature_names': FEATURE_NAMES,
        'weights': weights.tolist(),
        'bias': float(bias),
        'stats': stats,
        'note': 'PST/material are fixed (PeSTO tables). These weights apply to tunable features only.',
    }
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nWeights saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Train eval weights via linear regression")
    parser.add_argument("--data", required=True, help="Path to prepared CSV (from load_dataset.py)")
    parser.add_argument("--output", default="src/chess_engine/learned_weights.json",
                        help="Output JSON path")
    parser.add_argument("--alpha", type=float, default=1.0,
                        help="L2 regularisation (0 = plain OLS, try 0.1–10)")
    parser.add_argument("--test-split", type=float, default=0.15,
                        help="Fraction held out for testing")
    args = parser.parse_args()

    print("=== Linear Regression Tuner ===")
    print(f"  PST/material: FIXED (PeSTO tables)")
    print(f"  Tuning: {NUM_FEATURES} features ({', '.join(FEATURE_NAMES)})")
    print()

    # Load
    print(f"Loading {args.data}...")
    fens, sf_scores = load_dataset(args.data)
    print(f"  {len(fens)} positions\n")

    # Extract features + baselines
    print(f"Extracting features...")
    start = time.time()
    X, baselines = extract_all(fens)
    print(f"  Done in {time.time() - start:.1f}s\n")

    # Compute residuals: what the tunable features need to explain
    residuals = sf_scores - baselines

    print(f"Residual stats (SF eval - PST baseline):")
    print(f"  Mean:   {np.mean(residuals):+.4f} pawns")
    print(f"  Std:    {np.std(residuals):.4f} pawns")
    print(f"  Min:    {np.min(residuals):+.4f}")
    print(f"  Max:    {np.max(residuals):+.4f}")

    # Train/test split
    N = len(fens)
    n_test = int(N * args.test_split)
    n_train = N - n_test

    idx = np.random.permutation(N)
    train_idx, test_idx = idx[:n_train], idx[n_train:]

    X_train, y_train = X[train_idx], residuals[train_idx]
    X_test, y_test = X[test_idx], residuals[test_idx]

    print(f"\nTraining on {n_train}, testing on {n_test} (α={args.alpha})...")
    weights, bias, train_stats = train_ridge(X_train, y_train, alpha=args.alpha)

    # Test evaluation
    y_pred_test = X_test @ weights + bias
    test_res = y_test - y_pred_test
    test_stats = {
        'n_samples': n_test,
        'rmse': float(np.sqrt(np.mean(test_res ** 2))),
        'mae': float(np.mean(np.abs(test_res))),
        'r2': float(1 - np.sum(test_res ** 2) / np.sum((y_test - np.mean(y_test)) ** 2)),
        'abs_errors': np.abs(test_res),
    }

    # Also compute end-to-end metrics (PST + learned vs Stockfish)
    sf_test = sf_scores[test_idx]
    baseline_test = baselines[test_idx]
    full_pred = baseline_test + y_pred_test
    full_res = sf_test - full_pred
    full_rmse = float(np.sqrt(np.mean(full_res ** 2)))

    # Compare against PST-only baseline
    pst_only_res = sf_test - baseline_test
    pst_rmse = float(np.sqrt(np.mean(pst_only_res ** 2)))

    print_results(weights, bias, train_stats, test_stats)

    print(f"\n  End-to-end comparison (test set):")
    print(f"    PST baseline only RMSE:       {pst_rmse:.4f} pawns")
    print(f"    PST + learned features RMSE:  {full_rmse:.4f} pawns")
    improvement = (pst_rmse - full_rmse) / pst_rmse * 100
    print(f"    Improvement:                  {improvement:+.1f}%")

    # Save (exclude numpy arrays from JSON)
    save_stats = {k: v for k, v in train_stats.items()}
    save_stats['test_rmse'] = test_stats['rmse']
    save_stats['test_mae'] = test_stats['mae']
    save_stats['test_r2'] = test_stats['r2']
    save_stats['pst_only_rmse'] = pst_rmse
    save_stats['full_rmse'] = full_rmse
    save_weights(weights, bias, save_stats, args.output)


if __name__ == "__main__":
    main()
