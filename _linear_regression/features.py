"""
Feature extraction for linear regression tuning.

Design principle: the PeSTO piece-square tables (including material values)
are already well-optimised and remain FIXED.  We compute them as a baseline
score, then learn weights only for the remaining evaluation terms:

    eval = fixed_pst_baseline(board) + dot(weights, tunable_features) + bias

Tunable features (10 total):
    0-3   knight / bishop / rook / queen mobility diff
    4     doubled pawn diff
    5     isolated pawn diff
    6     passed pawn count diff
    7     passed pawn advancement diff  (rank-weighted)
    8     bishop pair diff
    9     tempo
"""

import chess
import numpy as np

# ─────────────────────────────────────────────────────────────────────
# PeSTO Piece-Square Tables  (FIXED — not tuned by regression)
# Source: https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function
# ─────────────────────────────────────────────────────────────────────

_MG_TABLES_WHITE = {
    chess.PAWN: [
        0,0,0,0,0,0,0,0,
        -35,-1,-20,-23,-15,24,38,-22,
        -26,-4,-4,-10,3,3,33,-12,
        -27,-2,-5,12,17,6,10,-25,
        -14,13,6,21,23,12,17,-23,
        -6,7,26,31,65,56,25,-20,
        98,134,61,95,68,126,34,-11,
        0,0,0,0,0,0,0,0,
    ],
    chess.KNIGHT: [
        -105,-21,-58,-33,-17,-28,-19,-23,
        -29,-53,-12,-3,-1,18,-14,-19,
        -23,-9,12,10,19,17,25,-16,
        -13,4,16,13,28,19,21,-8,
        -9,17,19,53,37,69,18,22,
        -47,60,37,65,84,129,73,44,
        -73,-41,72,36,23,62,7,-17,
        -167,-89,-34,-49,61,-97,-15,-107,
    ],
    chess.BISHOP: [
        -33,-3,-14,-21,-13,-12,-39,-21,
        4,15,16,0,7,21,33,1,
        0,15,15,15,14,27,18,10,
        -6,13,13,26,34,12,10,4,
        -4,5,19,50,37,37,7,-2,
        -16,37,43,40,35,50,37,-2,
        -26,16,-18,-13,30,59,18,-47,
        -29,4,-82,-37,-25,-42,7,-8,
    ],
    chess.ROOK: [
        -19,-13,1,17,16,7,-37,-26,
        -44,-16,-20,-9,-1,11,-6,-71,
        -45,-25,-16,-17,3,0,-5,-33,
        -36,-26,-12,-1,9,-7,6,-23,
        -24,-11,7,26,24,35,-8,-20,
        -5,19,26,36,17,45,61,16,
        27,32,58,62,80,67,26,44,
        32,42,32,51,63,9,31,43,
    ],
    chess.QUEEN: [
        -1,-18,-9,-10,-15,-25,-31,-50,
        -35,-8,11,2,8,15,-3,1,
        -14,2,-11,-2,-5,2,14,5,
        -9,-26,-28,-10,-10,-11,-17,-9,
        -27,-27,-16,-16,-1,17,-2,1,
        -13,-17,7,8,29,56,47,57,
        -24,-39,-5,1,-16,57,28,54,
        -28,0,29,12,59,44,43,45,
    ],
    chess.KING: [
        -15,36,12,-54,8,-28,24,14,
        1,7,-8,-64,-43,-16,9,8,
        -14,-14,-22,-46,-44,-30,-15,-27,
        -49,-1,-27,-39,-46,-44,-33,-51,
        -17,-20,-12,-27,-30,-25,-14,-36,
        -9,24,2,-16,-20,6,22,-22,
        29,-1,-20,-7,-8,-4,-38,-29,
        -65,23,16,-15,-56,-34,2,13,
    ],
}

_EG_TABLES_WHITE = {
    chess.PAWN: [
        0,0,0,0,0,0,0,0,
        13,8,8,10,13,0,2,-7,
        4,7,-6,1,0,-5,-1,-8,
        13,9,-3,-7,-7,-8,3,-1,
        32,24,13,5,-2,4,17,17,
        94,100,85,67,56,53,82,84,
        178,173,158,134,147,132,165,187,
        0,0,0,0,0,0,0,0,
    ],
    chess.KNIGHT: [
        -29,-51,-23,-15,-22,-18,-50,-64,
        -42,-20,-10,-5,-2,-20,-23,-44,
        -23,-3,-1,15,10,-3,-20,-22,
        -18,-6,16,25,16,17,4,-18,
        -17,3,22,22,22,11,8,-18,
        -24,-20,10,9,-1,-9,-19,-41,
        -25,-8,-25,-2,-9,-25,-24,-52,
        -58,-38,-13,-28,-31,-27,-63,-99,
    ],
    chess.BISHOP: [
        -23,-18,-23,-18,-23,-9,-27,-22,
        -15,-4,-12,-4,-3,-6,-4,-16,
        -12,-3,5,10,1,6,-5,-11,
        -6,3,13,19,7,10,-3,-9,
        -3,9,12,9,14,10,3,2,
        2,-8,0,-1,-2,6,0,4,
        -8,-4,7,-12,-3,-13,-4,-14,
        -14,-21,-11,-8,-7,-9,-17,-24,
    ],
    chess.ROOK: [
        -9,2,3,-1,-5,-13,4,-20,
        -6,-6,0,2,-9,-9,-11,-3,
        -4,0,-5,-1,-7,-12,-8,-16,
        3,5,8,4,-5,-6,-8,-11,
        4,3,13,1,2,1,-1,2,
        7,7,7,5,4,-3,-5,-3,
        11,13,13,11,-3,3,8,3,
        13,10,18,15,12,12,8,5,
    ],
    chess.QUEEN: [
        -33,-28,-22,-43,-5,-32,-20,-41,
        -22,-23,-30,-16,-16,-23,-36,-32,
        -16,-27,15,6,9,17,10,5,
        -18,28,19,47,31,34,39,23,
        3,22,24,45,57,40,57,36,
        -20,6,9,49,47,35,19,9,
        -17,20,32,41,58,25,30,0,
        -9,22,22,27,27,19,10,20,
    ],
    chess.KING: [
        -53,-34,-21,-11,-28,-14,-24,-43,
        -27,-11,4,13,14,4,-5,-17,
        -19,-3,11,21,23,16,7,-9,
        -18,-4,21,24,27,23,9,-11,
        -8,22,24,27,26,33,26,3,
        10,17,23,15,20,45,44,13,
        -12,17,14,17,17,38,23,11,
        -74,-35,-18,-18,-11,15,4,-17,
    ],
}

# Mirror tables for black
_MG_TABLES_BLACK = {}
_EG_TABLES_BLACK = {}
for _pt in _MG_TABLES_WHITE:
    _MG_TABLES_BLACK[_pt] = [_MG_TABLES_WHITE[_pt][i ^ 56] for i in range(64)]
    _EG_TABLES_BLACK[_pt] = [_EG_TABLES_WHITE[_pt][i ^ 56] for i in range(64)]

# Unified lookup
TABLES = {}
for _pt in _MG_TABLES_WHITE:
    TABLES[_pt] = {
        chess.WHITE: {'mg': _MG_TABLES_WHITE[_pt], 'eg': _EG_TABLES_WHITE[_pt]},
        chess.BLACK: {'mg': _MG_TABLES_BLACK[_pt], 'eg': _EG_TABLES_BLACK[_pt]},
    }

# PeSTO material values (centipawns)
MG_VALUE = {
    chess.PAWN: 82, chess.KNIGHT: 337, chess.BISHOP: 365,
    chess.ROOK: 477, chess.QUEEN: 1025, chess.KING: 0
}
EG_VALUE = {
    chess.PAWN: 94, chess.KNIGHT: 281, chess.BISHOP: 297,
    chess.ROOK: 512, chess.QUEEN: 936, chess.KING: 0
}

GAME_PHASE_INC = {
    chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 1,
    chess.ROOK: 2, chess.QUEEN: 4, chess.KING: 0
}

# ─────────────────────────────────────────────────────────────────────
# Tunable feature definitions
# ─────────────────────────────────────────────────────────────────────
FEATURE_NAMES = [
    'knight_mobility', 'bishop_mobility', 'rook_mobility', 'queen_mobility',
    'doubled_pawns', 'isolated_pawns',
    'passed_pawn_count', 'passed_pawn_advancement',
    'bishop_pair', 'tempo',
]

NUM_FEATURES = len(FEATURE_NAMES)


def compute_pst_baseline(board: chess.Board) -> float:
    """
    Compute the FIXED PeSTO baseline: material + piece-square tables
    with tapered evaluation.  This is identical to the material + PST
    portion of ClassicEvaluator.evaluate(), returning score in pawns.
    """
    mg_score = 0
    eg_score = 0
    game_phase = 0

    for sq, piece in board.piece_map().items():
        pt = piece.piece_type
        color = piece.color

        mg_val = MG_VALUE[pt] + TABLES[pt][color]['mg'][sq]
        eg_val = EG_VALUE[pt] + TABLES[pt][color]['eg'][sq]

        if color == chess.WHITE:
            mg_score += mg_val
            eg_score += eg_val
        else:
            mg_score -= mg_val
            eg_score -= eg_val

        game_phase += GAME_PHASE_INC[pt]

    # Tapered evaluation
    mg_phase = min(game_phase, 24)
    eg_phase = 24 - mg_phase
    score_cp = (mg_score * mg_phase + eg_score * eg_phase) / 24

    return score_cp / 100.0


def extract_features(board: chess.Board) -> np.ndarray:
    """
    Extract TUNABLE features only (excludes PST/material which are fixed).
    
    Returns:
        numpy array of shape (NUM_FEATURES,) — one value per tunable feature.
    
    All features are from White's perspective (positive = good for White).
    """
    features = np.zeros(NUM_FEATURES, dtype=np.float64)

    # ── 0-3: Mobility diffs ─────────────────────────────────────────
    mob_pieces = [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
    for j, pt in enumerate(mob_pieces):
        mob = 0
        for sq in board.pieces(pt, chess.WHITE):
            mob += len(board.attacks(sq) & ~board.occupied_co[chess.WHITE])
        for sq in board.pieces(pt, chess.BLACK):
            mob -= len(board.attacks(sq) & ~board.occupied_co[chess.BLACK])
        features[j] = mob

    # ── 4-5: Doubled & isolated pawns ───────────────────────────────
    white_pawns = board.occupied_co[chess.WHITE] & board.pawns
    black_pawns = board.occupied_co[chess.BLACK] & board.pawns

    w_doubled = b_doubled = 0
    for f in range(8):
        mask = chess.BB_FILES[f]
        wc = (white_pawns & mask).bit_count()
        bc = (black_pawns & mask).bit_count()
        if wc > 1: w_doubled += wc - 1
        if bc > 1: b_doubled += bc - 1
    features[4] = w_doubled - b_doubled  # positive = white has more (bad for white)

    w_isolated = b_isolated = 0
    for sq in board.pieces(chess.PAWN, chess.WHITE):
        f = chess.square_file(sq)
        adj = 0
        if f > 0: adj |= chess.BB_FILES[f - 1]
        if f < 7: adj |= chess.BB_FILES[f + 1]
        if (white_pawns & adj) == 0:
            w_isolated += 1
    for sq in board.pieces(chess.PAWN, chess.BLACK):
        f = chess.square_file(sq)
        adj = 0
        if f > 0: adj |= chess.BB_FILES[f - 1]
        if f < 7: adj |= chess.BB_FILES[f + 1]
        if (black_pawns & adj) == 0:
            b_isolated += 1
    features[5] = w_isolated - b_isolated

    # ── 6-7: Passed pawns ───────────────────────────────────────────
    w_passed = w_rank_sum = 0
    for sq in board.pieces(chess.PAWN, chess.WHITE):
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        front = chess.BB_FILES[f]
        if f > 0: front |= chess.BB_FILES[f - 1]
        if f < 7: front |= chess.BB_FILES[f + 1]
        ahead = ~((1 << (8 * (r + 1))) - 1) & 0xFFFFFFFFFFFFFFFF
        if (black_pawns & front & ahead) == 0 and r > 0 and r < 7:
            w_passed += 1
            w_rank_sum += r

    b_passed = b_rank_sum = 0
    for sq in board.pieces(chess.PAWN, chess.BLACK):
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        front = chess.BB_FILES[f]
        if f > 0: front |= chess.BB_FILES[f - 1]
        if f < 7: front |= chess.BB_FILES[f + 1]
        below = ((1 << (8 * r)) - 1) & 0xFFFFFFFFFFFFFFFF
        if (white_pawns & front & below) == 0 and r > 0 and r < 7:
            b_passed += 1
            b_rank_sum += (7 - r)

    features[6] = w_passed - b_passed
    features[7] = w_rank_sum - b_rank_sum

    # ── 8: Bishop pair ──────────────────────────────────────────────
    w_bp = 1 if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2 else 0
    b_bp = 1 if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2 else 0
    features[8] = w_bp - b_bp

    # ── 9: Tempo ────────────────────────────────────────────────────
    features[9] = 1.0 if board.turn == chess.WHITE else -1.0

    return features
