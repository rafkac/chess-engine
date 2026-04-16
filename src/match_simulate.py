"""
Match simulation: pits two engine configurations against each other
over a set of opening positions, playing each opening twice
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
from chess_engine.search_open_book import SearchEngineWithOpenings

#deeper opening
from chess_engine.search_open_book_deep import SearchEngineWithDeepOpenings


# ─────────────────────────────────────────────────────────────────────────
# PLAYER CONFIGURATION
# Change these to swap evaluators / search engines for future experiments.
# Each player dict has:
#   "label"     – short name shown in output
#   "evaluator" – callable that returns an evaluator instance
#   "search"    – callable(evaluator) that returns a search engine instance
# ─────────────────────────────────────────────────────────────────────────
PLAYER_1 = {
    "label": "Perfect2023.bin",
    "evaluator": ClassicEvaluator,
    "search": SearchEngine,
}

PLAYER_2 = {
    "label": "deep Cerebellum3Merge.bin",
    "evaluator": ClassicEvaluator,
    "search": SearchEngineWithOpenings,
}


# ─────────────────────────────────────────────────────────────────────────
# Opening book – a diverse set of common positions after 3-5 moves.
# Each opening is played twice (player2=white, then player2=black).
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


# helper: build an engine from a player config dict
def build_engine(player_cfg):
    evaluator = player_cfg["evaluator"]()
    engine = player_cfg["search"](evaluator)
    return engine


# ─────────────────────────────────────────────────────────────────────────
# Single-game driver
# ─────────────────────────────────────────────────────────────────────────
def play_game(white_engine, black_engine, start_fen, depth, max_moves=200, verbose=False):
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
        move, _score, _elapsed = engine.get_best_move(board, depth=depth)
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
        if board.turn == chess.WHITE:
            return -1, "checkmate (black wins)", half_moves
        else:
            return 1, "checkmate (white wins)", half_moves
    elif board.is_stalemate():
        return 0, "stalemate", half_moves
    elif board.is_insufficient_material():
        return 0, "insufficient material", half_moves
    # elif board.is_seventyfive_moves():
    #     return 0, "75-move rule", half_moves
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
    # build engines from global config
    p1_engine = build_engine(PLAYER_1)
    p2_engine = build_engine(PLAYER_2)

    p1_label = PLAYER_1["label"]
    p2_label = PLAYER_2["label"]

    total_games = len(OPENINGS) * 2  # each opening played twice
    results = {
        "p2_wins": 0,
        "p1_wins": 0,
        "draws": 0,
    }
    game_log = []

    print("=" * 72)
    print(f"  MATCH: Player 1 [{p1_label}]  vs  Player 2 [{p2_label}]")
    print(f"  Search depth: {depth}  |  Max moves/game: {max_moves}")
    print(f"  Openings: {len(OPENINGS)}  |  Total games: {total_games}")
    print("=" * 72)
    print()

    match_start = time.time()
    game_num = 0

    for opening_name, fen in OPENINGS:
        # Player 2 plays white first, then black
        for p2_color in ["white", "black"]:
            game_num += 1

            if p2_color == "white":
                white_eng, black_eng = p2_engine, p1_engine
                white_label, black_label = p2_label, p1_label
            else:
                white_eng, black_eng = p1_engine, p2_engine
                white_label, black_label = p1_label, p2_label

            print(f"Game {game_num}/{total_games}: {opening_name}  "
                  f"[W={white_label} vs B={black_label}]")

            t0 = time.time()
            result, reason, moves = play_game(
                white_eng, black_eng, fen, depth, max_moves, verbose
            )
            elapsed = time.time() - t0

            # translate result to p2/p1 perspective
            if p2_color == "white":
                if result == 1:
                    outcome = f"{p2_label} wins"
                    results["p2_wins"] += 1
                elif result == -1:
                    outcome = f"{p1_label} wins"
                    results["p1_wins"] += 1
                else:
                    outcome = "Draw"
                    results["draws"] += 1
            else:  # p2 is black
                if result == -1:
                    outcome = f"{p2_label} wins"
                    results["p2_wins"] += 1
                elif result == 1:
                    outcome = f"{p1_label} wins"
                    results["p1_wins"] += 1
                else:
                    outcome = "Draw"
                    results["draws"] += 1

            game_log.append({
                "game": game_num,
                "opening": opening_name,
                "p2_color": p2_color,
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
    print(f"{'#':<4} {'Opening':<24} {'P2 as':<7} {'Outcome':<28} "
          f"{'Reason':<28} {'Moves':<6} {'Time':<6}")
    print("-" * 105)
    for g in game_log:
        print(f"{g['game']:<4} {g['opening']:<24} {g['p2_color']:<7} "
              f"{g['outcome']:<28} {g['reason']:<28} {g['moves']:<6} "
              f"{g['time']:<6.1f}s")
    print("-" * 105)
    print()

    # aggregate
    p2_w = results["p2_wins"]
    p1_w = results["p1_wins"]
    draws = results["draws"]

    # Elo-style score: win=1, draw=0.5, loss=0
    p2_score = p2_w + 0.5 * draws
    p1_score = p1_w + 0.5 * draws

    print(f"  Player 1 [{p1_label}]:  {p1_w} wins  |  score: {p1_score:.1f} / {total_games}")
    print(f"  Player 2 [{p2_label}]:  {p2_w} wins  |  score: {p2_score:.1f} / {total_games}")
    print(f"  Draws:                   {draws}")
    print()

    # win percentages
    p2_pct = 100 * p2_score / total_games
    p1_pct = 100 * p1_score / total_games
    print(f"  Player 1 win rate: {p1_pct:.1f}%")
    print(f"  Player 2 win rate: {p2_pct:.1f}%")
    print()

    # Elo difference estimate (logistic model)
    if 0 < p2_pct < 100:
        import math
        elo_diff = -400 * math.log10((1 / (p2_score / total_games)) - 1)
        print(f"  Estimated Elo difference (P2 − P1): {elo_diff:+.0f}")
    elif p2_pct == 100:
        print(f"  Estimated Elo difference: P2 is dominant (100% score)")
    else:
        print(f"  Estimated Elo difference: P1 is dominant (0% score for P2)")

    print()
    print(f"  Total match time: {match_elapsed:.1f}s")
    print()

    # verdict
    if p2_w > p1_w:
        print(f"  ✓ Player 2 [{p2_label}] is STRONGER")
    elif p1_w > p2_w:
        print(f"  ✗ Player 1 [{p1_label}] was BETTER")
    else:
        print(f"  ≈ Engines are roughly EQUAL")

    print("=" * 72)

    return results


# ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chess engine match simulation")
    parser.add_argument("--depth", type=int, default=4, # default?
                        help="Search depth for both engines (default: 3)")
    parser.add_argument("--max-moves", type=int, default=200,
                        help="Max full moves per game before adjudicating draw (default: 200)")
    parser.add_argument("--verbose", action="store_true",
                        help="Print every move during games")
    args = parser.parse_args()

    run_match(depth=args.depth, max_moves=args.max_moves, verbose=args.verbose)