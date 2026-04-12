import chess
import chess.engine
from eval import evaluate

stockfish = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")


def test_position(fen_string):
    print("...testing position:", fen_string)
    board = chess.Board(fen_string)
    if not board.is_valid():
        print("error - invalid FEN string.")
        return
    info = stockfish.analyse(board, chess.engine.Limit(depth=15))
    print("Stockfish evaluation:", info["score"])
    


test_positions = {
    "tactical": [
        # Simple tactics, one side clearly winning
        "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R w KQkq - 2 4",
        "r1bq1rk1/ppp2ppp/2n2n2/3pp3/1b1PP3/2NBBN2/PPPQ1PPP/2KR2NR w - - 6 10",
        "r1b2rk1/pp3ppp/2n1pn2/2b5/2B1P3/2N2N2/PPP2PPP/R1BR2K1 w - - 2 9",
    ],
    "positional": [
        # Mobility, space, minor piece placement
        "2rq1rk1/pp2bppp/2n1pn2/3p4/3P1B2/2NB1N2/PP3PPP/2RQ1RK1 w - - 2 12",
        "r1bq1rk1/1p2bppp/p1n1pn2/2pp4/3P4/2P1PN2/PP1N1PPP/R1BQ1RK1 w - - 0 9",
        "r1bq1rk1/pp3ppp/2n1pn2/2bp4/2P5/1PN1PN2/PB3PPP/R2QKB1R w KQ - 4 9",
    ],
    "pawn_structure": [
        # Isolated, doubled, passed pawns
        "rnbq1rk1/pp3ppp/4pn2/2bp4/3P4/2N1PN2/PP3PPP/R1BQKB1R w KQ - 0 9",
        "r1bqk2r/ppp2ppp/2n1pn2/3p4/2BP1P2/2N2N2/PPP3PP/R1BQ1RK1 b kq - 0 8",
        "r2q1rk1/pp2bppp/2n1pn2/3p4/3P4/2P1PN2/PP1NBPPP/R1BQ1RK1 w - - 3 10",
    ],
    "king_safety": [
        "r1bq1rk1/ppp2ppp/2n1pn2/3p4/3P1B2/2P1PN2/PP3PPP/RN1Q1RK1 w - - 1 8",
        "r1bq1rk1/1p3pp1/p1n2n1p/2pp4/3P4/2P1PN2/PP1N1PPP/R1BQ1RK1 b - - 3 10",
    ],
    "endgames": [
        "8/8/8/3k4/3P4/8/4K3/8 w - - 0 1",        # K+P vs K
        "8/4R3/8/3P4/3k4/8/5r2/6K1 w - - 0 1",    # Lucena position
        "8/6p1/5p2/4p3/1Bp1k3/6P1/5P2/4K3 w - - 4 60", # Opposite-colored bishops
        "8/P7/8/8/4k3/8/7p/4K3 b - - 0 60"       # Passed rook pawn, drawish
    ]
}



for category, fens in test_positions.items():
    print(f"\n{category.capitalize()}:")
    for fen in fens:
        test_position(fen)        
        board = chess.Board(fen)
        eval_score = evaluate(board)
        print("my evaluation:", eval_score)
    print("-" * 50)


stockfish.quit()
