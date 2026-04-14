"""
Learned Evaluator — drop-in replacement for ClassicEvaluator.

Computes:  score = fixed_pst_baseline(board) + dot(weights, features) + bias

The PST/material component uses the same PeSTO tables as ClassicEvaluator.
The weights for mobility, pawn structure, bishop pair, and tempo are loaded
from a JSON file produced by the training script.

Usage:
    from chess_engine.learned_evaluator import LearnedEvaluator
    evaluator = LearnedEvaluator("path/to/learned_weights.json")
    score = evaluator.evaluate(board)  # same interface as ClassicEvaluator
"""

import json
import os

import chess
import numpy as np

from chess_engine.features import (
    extract_features, compute_pst_baseline,
    FEATURE_NAMES, NUM_FEATURES
)


# Default weights (matching ClassicEvaluator's hand-tuned values, in pawns)
DEFAULT_WEIGHTS = {
    'knight_mobility': 0.04,  # 4cp per square
    'bishop_mobility': 0.05,
    'rook_mobility': 0.02,
    'queen_mobility': 0.01,
    'doubled_pawns': -0.15,   # penalty per doubled pawn
    'isolated_pawns': -0.20,  # penalty per isolated pawn
    'passed_pawn_count': 0.20,
    'passed_pawn_advancement': 0.10,
    'bishop_pair': 0.30,
    'tempo': 0.15,
}
DEFAULT_BIAS = 0.0


class LearnedEvaluator:
    """
    Position evaluator: fixed PST + learned feature weights.
    
    Drop-in replacement for ClassicEvaluator — same .evaluate(board) interface.
    """

    def __init__(self, weights_path: str = None):
        if weights_path and os.path.exists(weights_path):
            self._load_weights(weights_path)
            print(f"LearnedEvaluator: loaded weights from {weights_path}")
        else:
            self._use_defaults()
            if weights_path:
                print(f"LearnedEvaluator: {weights_path} not found, using defaults")
            else:
                print("LearnedEvaluator: using default weights")

    def _load_weights(self, path: str):
        with open(path, 'r') as f:
            data = json.load(f)
        self.weights = np.array(data['weights'], dtype=np.float64)
        self.bias = float(data['bias'])
        self.stats = data.get('stats', {})
        assert len(self.weights) == NUM_FEATURES, \
            f"Expected {NUM_FEATURES} weights, got {len(self.weights)}"

    def _use_defaults(self):
        self.weights = np.array(
            [DEFAULT_WEIGHTS[name] for name in FEATURE_NAMES],
            dtype=np.float64
        )
        self.bias = DEFAULT_BIAS
        self.stats = {}

    def evaluate(self, board: chess.Board) -> float:
        """
        Evaluate a position from White's perspective.
        
        Returns:
            float: Score in pawns. Positive = White advantage.
        """
        # Terminal positions
        if board.is_checkmate():
            return -9999.0 if board.turn == chess.WHITE else 9999.0
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0

        # Fixed PST/material baseline
        baseline = compute_pst_baseline(board)

        # Learned feature contribution
        features = extract_features(board)
        learned = float(np.dot(self.weights, features) + self.bias)

        return baseline + learned

    def get_weights_summary(self) -> dict:
        """Return readable summary of current weights."""
        summary = {}
        for name, w in zip(FEATURE_NAMES, self.weights):
            summary[name] = round(float(w), 4)
        summary['bias'] = round(self.bias, 4)
        if self.stats:
            summary['training_rmse'] = self.stats.get('rmse', 'N/A')
            summary['test_rmse'] = self.stats.get('test_rmse', 'N/A')
        return summary


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else None
    evaluator = LearnedEvaluator(path)

    test_fens = [
        ("startpos", chess.STARTING_FEN),
        ("italian", "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"),
        ("KP endgame", "8/8/8/3k4/3P4/8/4K3/8 w - - 0 1"),
    ]

    print(f"\n{'Position':<20} {'Baseline':>10} {'Learned':>10} {'Total':>10}")
    print("-" * 55)
    for name, fen in test_fens:
        board = chess.Board(fen)
        baseline = compute_pst_baseline(board)
        total = evaluator.evaluate(board)
        delta = total - baseline
        print(f"{name:<20} {baseline:>10.2f} {delta:>+10.2f} {total:>10.2f}")

    print("\nWeight summary:")
    for k, v in evaluator.get_weights_summary().items():
        print(f"  {k}: {v}")
