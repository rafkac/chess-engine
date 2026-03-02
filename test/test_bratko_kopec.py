import chess
import chess.engine
from chess_engine.evaluator import ClassicEvaluator
from chess_engine.search import SearchEngine

# ─────────────────────────────────────────────────────────────
# The 24 standard Bratko-Kopec positions (EPD format)
# Each position has one or more "best moves" (bm) to find.
# source: https://www.chessprogramming.org/Bratko-Kopec_Test
# ─────────────────────────────────────────────────────────────

BK_POSITIONS = [
    "1k1r4/pp1b1R2/3q2pp/4p3/2B5/4Q3/PPP2B2/2K5 b - - bm Qd1+;",
    "3r1k2/4npp1/1ppr3p/p6P/P2PPPP1/1NR5/5K2/2R5 w - - bm d5;",
    "2q1rr1k/3bbnnp/p2p1pp1/2pPp3/PpP1P1P1/1P2BNNP/2BQ1PRK/7R b - - bm f5;",
    "rnbqkb1r/p3pppp/1p6/2ppP3/3N4/2P5/PPP1QPPP/R1B1KB1R w KQkq - bm e6;",
    "r1b2rk1/2q1b1pp/p2ppn2/1p6/3QP3/1BN1B3/PPP3PP/R4RK1 w - - bm Nd5 a4;",
    "2r3k1/pppR1pp1/4p3/4P1P1/5P2/1P4K1/P1P5/8 w - - bm g6;",
    "1nk1r1r1/pp2n1pp/4p3/q2pPp1N/b1pP1P2/B1P2R2/2P1B1PP/R2Q2K1 w - - bm Nf6;",
    "4b3/p3kp2/6p1/3pP2p/2pP1P2/4K1P1/P3N2P/8 w - - bm f5;",
    "2kr1bnr/pbpq4/2n1pp2/3p3p/3P1P1B/2N2N1Q/PPP3PP/2KR1B1R w - - bm f5;",
    "3rr1k1/pp3pp1/1qn2np1/8/3p4/PP1R1P2/2P1NQPP/R1B3K1 b - - bm Ne5;",
    "2r1nrk1/p2q1ppp/bp1p4/n1pPp3/P1P1P3/2PBB1N1/4QPPP/R4RK1 w - - bm f4;",
    "r3r1k1/ppqb1ppp/8/4p1NQ/8/2P5/PP3PPP/R3R1K1 b - - bm Bf5;",
    "r2q1rk1/4bppp/p2p4/2pP4/3pP3/3Q4/PP1B1PPP/R3R1K1 w - - bm b4;",
    "rnb2r1k/pp2p2p/2pp2p1/q2P1p2/8/1Pb2NP1/PB2PPBP/R2Q1RK1 w - - bm Qd2 Qe1;",
    "2r3k1/1p2q1pp/2b1pr2/p1pp4/6Q1/1P1PP1R1/P1PN2PP/5RK1 w - - bm Qxg7+;",
    "r1bqkb1r/4npp1/p1p4p/1p1pP1B1/8/1B6/PPPN1PPP/R2Q1RK1 w kq - bm Ne4;",
    "r2q1rk1/1ppnbppp/p2p1nb1/3Pp3/2P1P1P1/2N2N1P/PPB1QP2/R1B2RK1 b - - bm h5;",
    "r1bq1rk1/pp2ppbp/2np2p1/2n5/P3PP2/N1P2N2/1PB3PP/R1B1QRK1 b - - bm Nb3;",
    "3rr3/2pq2pk/p2p1pnp/8/2QBPP2/1P6/P5PP/4RRK1 b - - bm Rxe4;",
    "r4k2/pb2bp1r/1p1qp2p/3pNp2/3P1P2/2N3P1/PPP1Q2P/2KRR3 w - - bm g4;",
    "3rn2k/ppb2rpp/2ppqp2/5N2/2P1P3/1P5Q/PB3PPP/3RR1K1 w - - bm Nh6;",
    "2r2rk1/1bqnbpp1/1p1ppn1p/pP6/N1P1P3/P2B1N1P/1B2QPP1/R2R2K1 b - - bm Bxe4;",
    "r1bqk2r/pp2bppp/2p5/3pP3/P2Q1P2/2N1B3/1PP3PP/R4RK1 b kq - bm f6;",
    "r2qnrnk/p2b2b1/1p1p2pp/2pPpp2/1PP1P3/PRNBB3/3QNPPP/5RK1 w - - bm f4;"
]

SEARCH_DEPTH = 5

def run_bk_test(depth: int = SEARCH_DEPTH):
    evaluator = ClassicEvaluator()
    engine = SearchEngine(evaluator)

    solved_count = 0
    total = len(BK_POSITIONS)

    print(f"Bratko-Kopec Test  |  depth = {depth}")
    print("=" * 70)
    print(f"{'#':<4} {'Result':<8} {'Played':<10} {'Expected':<25} {'Score'}")
    print("-" * 70)

    for i, epd in enumerate(BK_POSITIONS, 1):
        board = chess.Board()

        # Parse EPD → board state + operations dict.
        # ops["bm"] gives a list of chess.Move objects for the best move(s).
        try:
            ops = board.set_epd(epd)
        except Exception as e:
            print(f"{i:<4} PARSE ERROR: {e}")
            continue

        if "bm" not in ops:
            print(f"{i:<4} SKIP       (no 'bm' in EPD)")
            continue

        expected_moves: list[chess.Move] = ops["bm"]

        # Run engine
        best_move, score, _elapsed = engine.get_best_move(board, depth=depth)

        solved = best_move in expected_moves
        if solved:
            solved_count += 1

        played_san   = board.san(best_move) if best_move else "None"
        expected_san = ", ".join(board.san(m) for m in expected_moves)
        result_str   = "✓ SOLVED" if solved else "✗ FAILED"
        score_str    = f"{score/100:.2f}" if isinstance(score, (int, float)) else str(score)

        print(f"{i:<4} {result_str:<8} {played_san:<10} {expected_san:<25} {score_str}")

    print("=" * 70)
    pct = 100 * solved_count / total
    print(f"Score: {solved_count} / {total}  ({pct:.1f}%)")
    print()

    # Rough rating estimate based on published BK benchmarks
    if solved_count >= 20:
        rating_band = "~2200+ (strong club / engine level)"
    elif solved_count >= 16:
        rating_band = "~1900–2200 (advanced club player)"
    elif solved_count >= 12:
        rating_band = "~1600–1900 (intermediate)"
    elif solved_count >= 8:
        rating_band = "~1300–1600 (beginner–intermediate)"
    else:
        rating_band = "<1300 (beginner)"

    print(f"Estimated strength: {rating_band}")

    return solved_count, total


if __name__ == "__main__":
    run_bk_test(depth=SEARCH_DEPTH)    
