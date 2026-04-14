#!/usr/bin/env python3
"""
Compare ClassicEvaluator vs LearnedEvaluator on the standard test suite.

Usage:
    python compare_evaluators.py --stockfish /opt/homebrew/bin/stockfish \
                                  --weights ../src/chess_engine/learned_weights.json
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import chess
import chess.engine
from chess_engine.evaluator import ClassicEvaluator
from chess_engine.learned_evaluator import LearnedEvaluator

POSITIONS = [
    ("starting position",         "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
    ("tactical #1",               "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R w KQkq - 2 4"),
    ("tactical #2",               "r1bq1rk1/ppp2ppp/2n2n2/3pp3/1b1PP3/2NBBN2/PPPQ1PPP/2KR2NR w - - 6 10"),
    ("tactical #3",               "r1b2rk1/pp3ppp/2n1pn2/2b5/2B1P3/2N2N2/PPP2PPP/R1BR2K1 w - - 2 9"),
    ("positional #1",             "2rq1rk1/pp2bppp/2n1pn2/3p4/3P1B2/2NB1N2/PP3PPP/2RQ1RK1 w - - 2 12"),
    ("positional #2",             "r1bq1rk1/1p2bppp/p1n1pn2/2pp4/3P4/2P1PN2/PP1N1PPP/R1BQ1RK1 w - - 0 9"),
    ("positional #3",             "r1bq1rk1/pp3ppp/2n1pn2/2bp4/2P5/1PN1PN2/PB3PPP/R2QKB1R w KQ - 4 9"),
    ("pawn structure #1",         "rnbq1rk1/pp3ppp/4pn2/2bp4/3P4/2N1PN2/PP3PPP/R1BQKB1R w KQ - 0 9"),
    ("pawn structure #2",         "r1bqk2r/ppp2ppp/2n1pn2/3p4/2BP1P2/2N2N2/PPP3PP/R1BQ1RK1 b kq - 0 8"),
    ("pawn structure #3",         "r2q1rk1/pp2bppp/2n1pn2/3p4/3P4/2P1PN2/PP1NBPPP/R1BQ1RK1 w - - 3 10"),
    ("king safety #1",            "r1bq1rk1/ppp2ppp/2n1pn2/3p4/3P1B2/2P1PN2/PP3PPP/RN1Q1RK1 w - - 1 8"),
    ("king safety #2",            "r1bq1rk1/1p3pp1/p1n2n1p/2pp4/3P4/2P1PN2/PP1N1PPP/R1BQ1RK1 b - - 3 10"),
    ("endgame #1",                "8/8/8/3k4/3P4/8/4K3/8 w - - 0 1"),
    ("endgame #2",                "8/4R3/8/3P4/3k4/8/5r2/6K1 w - - 0 1"),
    ("endgame #3",                "8/6p1/5p2/4p3/1Bp1k3/6P1/5P2/4K3 w - - 4 60"),
    ("endgame #4",                "8/P7/8/8/4k3/8/7p/4K3 b - -  0 60"),
    ("white slight +",            "r1bqkbnr/1ppp1ppp/p1n5/4p3/B3P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 1 4"),
    ("white up a pawn",           "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"),
    ("white winning (+knight)",   "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1"),
    ("black up a bishop",         "rnbqk1nr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 2"),
    ("exchange sac (R vs N+P)",   "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1"),
    ("tight mid-game",            "r1bqkb1r/1p2pppp/p1np1n2/8/3NP3/2N1B3/PPP2PPP/R2QKB1R w KQkq - 2 7"),
    ("french def (space adv)",    "rnbqk2r/pp2bppp/4pn2/2ppP3/3P4/2N2N2/PPP2PPP/R1BQKB1R b KQkq - 0 5"),
    ("isolated queen pawn",       "rnbq1rk1/pp2bppp/4pn2/2pp4/2PP4/2N1PN2/PP2BPPP/R1BQ1RK1 w - - 0 1"),
    ("stonewall (closed)",        "rnbqk2r/pp3ppp/4pn2/2pp4/2PP1P2/2N2N2/PP2P1PP/R1BQKB1R b KQkq - 0 1"),
    ("castled vs uncastled",      "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R w KQ - 1 6"),
    ("hanging queen",             "rnb1kbnr/ppp1pppp/8/3q4/2P5/8/PP1P1PPP/RNBQKBNR b KQkq - 0 3"),
    ("back rank mate threat",     "6k1/5ppp/8/8/8/8/8/3R2K1 w - - 0 1"),
    ("king centralization",       "8/5k2/8/4K3/8/8/8/8 w - - 0 1"),
    ("lucena position (win)",     "1R6/8/8/8/8/5k2/7p/K7 w - - 0 1"),
    ("philidor position (draw)",  "2R5/8/8/8/4k3/8/r7/3K4 w - - 0 1"),
]


def main():
    parser = argparse.ArgumentParser(description="Compare evaluators against Stockfish")
    parser.add_argument("--stockfish", default="/opt/homebrew/bin/stockfish")
    parser.add_argument("--weights", default="src/chess_engine/learned_weights.json")
    parser.add_argument("--sf-depth", type=int, default=0,
                        help="Stockfish depth (0 = static eval)")
    args = parser.parse_args()

    classic = ClassicEvaluator()
    learned = LearnedEvaluator(args.weights)

    try:
        sf_engine = chess.engine.SimpleEngine.popen_uci(args.stockfish)
    except FileNotFoundError:
        print(f"ERROR: Stockfish not found at {args.stockfish}")
        return

    print(f"\n{'Position':<25} | {'Classic':<8} | {'Learned':<8} | {'SF':<8} | {'Δ Classic':<9} | {'Δ Learned':<9}")
    print("-" * 85)

    classic_total = learned_total = 0
    classic_max = learned_max = 0
    count = 0
    classic_wins = learned_wins = 0

    for name, fen in POSITIONS:
        board = chess.Board(fen)

        c_score = classic.evaluate(board)
        l_score = learned.evaluate(board)

        info = sf_engine.analyse(board, chess.engine.Limit(depth=args.sf_depth))
        sf_obj = info["score"].white()

        if sf_obj.is_mate():
            sf_str = f"M{sf_obj.mate()}"
            print(f"{name:<25} | {c_score:<8.2f} | {l_score:<8.2f} | {sf_str:<8} | {'N/A':<9} | {'N/A':<9}")
            continue

        sf_score = sf_obj.score() / 100.0
        c_diff = abs(c_score - sf_score)
        l_diff = abs(l_score - sf_score)

        classic_total += c_diff
        learned_total += l_diff
        classic_max = max(classic_max, c_diff)
        learned_max = max(learned_max, l_diff)
        count += 1

        if c_diff < l_diff:
            classic_wins += 1
            c_marker = " *"
            l_marker = ""
        elif l_diff < c_diff:
            learned_wins += 1
            c_marker = ""
            l_marker = " *"
        else:
            c_marker = l_marker = ""

        print(f"{name:<25} | {c_score:<8.2f} | {l_score:<8.2f} | {sf_score:<8.2f} | {c_diff:<7.2f}{c_marker:<2} | {l_diff:<7.2f}{l_marker:<2}")

    print("-" * 85)

    if count > 0:
        c_avg = classic_total / count
        l_avg = learned_total / count
        ties = count - classic_wins - learned_wins

        print(f"\n  {'Metric':<25} {'Classic':>10} {'Learned':>10} {'Winner':>10}")
        print(f"  {'-'*55}")
        print(f"  {'Average diff vs SF':<25} {c_avg:>10.2f} {l_avg:>10.2f} {'Learned' if l_avg < c_avg else 'Classic':>10}")
        print(f"  {'Max diff vs SF':<25} {classic_max:>10.2f} {learned_max:>10.2f} {'Learned' if learned_max < classic_max else 'Classic':>10}")
        print(f"  {'Positions closer to SF':<25} {classic_wins:>10} {learned_wins:>10} (ties: {ties})")

        improvement = (c_avg - l_avg) / c_avg * 100 if c_avg > 0 else 0
        print(f"\n  Average error change: {improvement:+.1f}%")

    sf_engine.quit()


if __name__ == "__main__":
    main()
