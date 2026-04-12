"""
Match simulation: pits the NEW engine (ClassicEvaluator) against the OLD engine
(OldEvaluator) over a set of opening positions, playing each opening twice
(swapping colours) for fairness.

Usage:
    python match_simulate.py                  # default depth 3
    python match_simulate.py --depth 4        # deeper search
    python match_simulate.py --max-moves 150  # shorter games
    python match_simulate.py --verbose        # print every move
"""

import sys
import os
import time
import argparse

# ── make sure the chess_engine package is importable ──────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import chess
from chess_engine.evaluator import ClassicEvaluator
from chess_engine.old_evaluator import OldEvaluator
from chess_engine.search import SearchEngine


# ─────────────────────────────────────────────────────────────────────────
# Opening book – a diverse set of common positions after 3-5 moves.
# Each opening is played twice (new=white, then new=black).
# ─────────────────────────────────────────────────────────────────────────
OPENINGS = [
    ("Starting Position",
     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),

    ("Italian Game",
     "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"),

    ("Sicilian Najdorf",
     "rnbqkb1r/1p2pppp/p2p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6"),

    ("French Defence",
     "rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3"),

    ("Caro-Kann",
     "rnbqkbnr/pp2pppp/2p5/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3"),

    ("Queen's Gambit Declined",
     "rnbqkb1r/ppp1pppp/5n2/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 2 3"),

    ("King's Indian",
     "rnbqkb1r/pppppp1p/5np1/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3"),

    ("Ruy Lopez",
     "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"),

    ("English Opening",
     "rnbqkbnr/pppp1ppp/8/4p3/2P5/8/PP1PPPPP/RNBQKBNR w KQkq - 0 2"),

    ("Scandinavian",
     "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"),

    ("Pirc Defence",
     "rnbqkb1r/ppp1pp1p/3p1np1/8/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4"),

    ("Slav Defence",
     "rnbqkb1r/pp2pppp/2p2n2/3p4/2PP4/5N2/PP2PPPP/RNBQKB1R w KQkq - 2 4"),
]


# ─────────────────────────────────────────────────────────────────────────
# Single-game driver
# ─────────────────────────────────────────────────────────────────────────
def play_game(white_engine, black_engine, start_fen, max_moves=200, verbose=False):
    """
    Play one full game and return the result from White's perspective.

    Returns:
        result  :  1  = White wins
                   -1 = Black wins
                    0 = Draw
        reason  : str explaining the outcome
        moves   : int total half-moves played
    """
    board = chess.Board(start_fen)
    half_moves = 0

    while not board.is_game_over() and half_moves < max_moves * 2:
        engine = white_engine if board.turn == chess.WHITE else black_engine
        move, _score, _elapsed = engine.get_best_move(board, depth=engine._match_depth)
        if move is None:
            break
        if verbose:
            side = "W" if board.turn == chess.WHITE else "B"
            san = board.san(move)
            print(f"  {half_moves + 1:>4}. {side} {san:<8}", end="")
            if half_moves % 4 == 3:
                print()
        board.push(move)
        half_moves += 1

    if verbose and half_moves % 4 != 0:
        print()

    # determine outcome
    if board.is_checkmate():
        # the side to move is mated, so the other side won
        if board.turn == chess.WHITE:
            return -1, "checkmate (black wins)", half_moves
        else:
            return 1, "checkmate (white wins)", half_moves
    elif board.is_stalemate():
        return 0, "stalemate", half_moves
    elif board.is_insufficient_material():
        return 0, "insufficient material", half_moves
    elif board.is_seventyfive_moves():
        return 0, "75-move rule", half_moves
    elif board.is_fivefold_repetition():
        return 0, "fivefold repetition", half_moves
    elif board.can_claim_threefold_repetition():
        return 0, "threefold repetition (claimable)", half_moves
    elif board.can_claim_fifty_moves():
        return 0, "50-move rule (claimable)", half_moves
    elif half_moves >= max_moves * 2:
        return 0, f"move limit ({max_moves})", half_moves
    else:
        return 0, "unknown draw", half_moves


# ─────────────────────────────────────────────────────────────────────────
# Match simulation
# ─────────────────────────────────────────────────────────────────────────
def run_match(depth=3, max_moves=200, verbose=False):
    # build engines
    new_eval = ClassicEvaluator()
    old_eval = OldEvaluator()
    new_engine = SearchEngine(new_eval)
    old_engine = SearchEngine(old_eval)
    new_engine._match_depth = depth
    old_engine._match_depth = depth

    total_games = len(OPENINGS) * 2  # each opening played twice
    results = {
        "new_wins": 0,
        "old_wins": 0,
        "draws": 0,
    }
    game_log = []

    print("=" * 72)
    print(f"  MATCH: NEW (ClassicEvaluator) vs OLD (OldEvaluator)")
    print(f"  Search depth: {depth}  |  Max moves/game: {max_moves}")
    print(f"  Openings: {len(OPENINGS)}  |  Total games: {total_games}")
    print("=" * 72)
    print()

    match_start = time.time()
    game_num = 0

    for opening_name, fen in OPENINGS:
        for new_color in ["white", "black"]:
            game_num += 1

            if new_color == "white":
                white_eng, black_eng = new_engine, old_engine
                white_label, black_label = "NEW", "OLD"
            else:
                white_eng, black_eng = old_engine, new_engine
                white_label, black_label = "OLD", "NEW"

            print(f"Game {game_num}/{total_games}: {opening_name}  "
                  f"[W={white_label} vs B={black_label}]")

            t0 = time.time()
            result, reason, moves = play_game(
                white_eng, black_eng, fen, max_moves, verbose
            )
            elapsed = time.time() - t0

            # translate result to new/old perspective
            if new_color == "white":
                if result == 1:
                    outcome = "NEW wins"
                    results["new_wins"] += 1
                elif result == -1:
                    outcome = "OLD wins"
                    results["old_wins"] += 1
                else:
                    outcome = "Draw"
                    results["draws"] += 1
            else:  # new is black
                if result == -1:
                    outcome = "NEW wins"
                    results["new_wins"] += 1
                elif result == 1:
                    outcome = "OLD wins"
                    results["old_wins"] += 1
                else:
                    outcome = "Draw"
                    results["draws"] += 1

            game_log.append({
                "game": game_num,
                "opening": opening_name,
                "new_color": new_color,
                "outcome": outcome,
                "reason": reason,
                "moves": moves // 2,  # full moves
                "time": elapsed,
            })

            print(f"  → {outcome}  ({reason}, {moves // 2} moves, {elapsed:.1f}s)")
            print()

    match_elapsed = time.time() - match_start

    # ── Summary ──────────────────────────────────────────────────────────
    print()
    print("=" * 72)
    print("  MATCH RESULTS")
    print("=" * 72)
    print()

    # per-game table
    print(f"{'#':<4} {'Opening':<24} {'New as':<7} {'Outcome':<10} "
          f"{'Reason':<28} {'Moves':<6} {'Time':<6}")
    print("-" * 90)
    for g in game_log:
        print(f"{g['game']:<4} {g['opening']:<24} {g['new_color']:<7} "
              f"{g['outcome']:<10} {g['reason']:<28} {g['moves']:<6} "
              f"{g['time']:<6.1f}s")
    print("-" * 90)
    print()

    # aggregate
    new_w = results["new_wins"]
    old_w = results["old_wins"]
    draws = results["draws"]

    # Elo-style score: win=1, draw=0.5, loss=0
    new_score = new_w + 0.5 * draws
    old_score = old_w + 0.5 * draws

    print(f"  NEW engine:  {new_w} wins  |  score: {new_score:.1f} / {total_games}")
    print(f"  OLD engine:  {old_w} wins  |  score: {old_score:.1f} / {total_games}")
    print(f"  Draws:       {draws}")
    print()

    # win percentages
    new_pct = 100 * new_score / total_games
    old_pct = 100 * old_score / total_games
    print(f"  NEW win rate: {new_pct:.1f}%")
    print(f"  OLD win rate: {old_pct:.1f}%")
    print()

    # Elo difference estimate (logistic model)
    if 0 < new_pct < 100:
        import math
        elo_diff = -400 * math.log10((1 / (new_score / total_games)) - 1)
        print(f"  Estimated Elo difference (NEW − OLD): {elo_diff:+.0f}")
    elif new_pct == 100:
        print(f"  Estimated Elo difference: NEW is dominant (100% score)")
    else:
        print(f"  Estimated Elo difference: OLD is dominant (0% score for NEW)")

    print()
    print(f"  Total match time: {match_elapsed:.1f}s")
    print()

    # verdict
    if new_w > old_w:
        print("  ✓ NEW version is STRONGER")
    elif old_w > new_w:
        print("  ✗ OLD version was BETTER")
    else:
        print("  ≈ Engines are roughly EQUAL")

    print("=" * 72)

    return results


# ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chess engine match simulation")
    parser.add_argument("--depth", type=int, default=3,
                        help="Search depth for both engines (default: 3)")
    parser.add_argument("--max-moves", type=int, default=200,
                        help="Max full moves per game before adjudicating draw (default: 200)")
    parser.add_argument("--verbose", action="store_true",
                        help="Print every move during games")
    args = parser.parse_args()

    run_match(depth=args.depth, max_moves=args.max_moves, verbose=args.verbose)