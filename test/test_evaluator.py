import chess
import chess.engine
from chess_engine.evaluator import ClassicEvaluator

class TestSuite:
    def __init__(self, engine_path):
        self.evaluator = ClassicEvaluator()
        self.engine_path = engine_path
        self.fens = [
            # --- BASELINE ---
            ("starting position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),

            # gpt
            ("tactical #1", "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R w KQkq - 2 4"),
            ("tactical #2", "r1bq1rk1/ppp2ppp/2n2n2/3pp3/1b1PP3/2NBBN2/PPPQ1PPP/2KR2NR w - - 6 10"),
            ("tactical #3", "r1b2rk1/pp3ppp/2n1pn2/2b5/2B1P3/2N2N2/PPP2PPP/R1BR2K1 w - - 2 9"),
            ("positional #1", "2rq1rk1/pp2bppp/2n1pn2/3p4/3P1B2/2NB1N2/PP3PPP/2RQ1RK1 w - - 2 12"),
            ("positional #2", "r1bq1rk1/1p2bppp/p1n1pn2/2pp4/3P4/2P1PN2/PP1N1PPP/R1BQ1RK1 w - - 0 9"),
            ("positional #3", "r1bq1rk1/pp3ppp/2n1pn2/2bp4/2P5/1PN1PN2/PB3PPP/R2QKB1R w KQ - 4 9"),
            ("pawn structure #1", "rnbq1rk1/pp3ppp/4pn2/2bp4/3P4/2N1PN2/PP3PPP/R1BQKB1R w KQ - 0 9"),
            ("pawn structure #2", "r1bqk2r/ppp2ppp/2n1pn2/3p4/2BP1P2/2N2N2/PPP3PP/R1BQ1RK1 b kq - 0 8"),
            ("pawn structure #3", "r2q1rk1/pp2bppp/2n1pn2/3p4/3P4/2P1PN2/PP1NBPPP/R1BQ1RK1 w - - 3 10"),
            ("king safety #1", "r1bq1rk1/ppp2ppp/2n1pn2/3p4/3P1B2/2P1PN2/PP3PPP/RN1Q1RK1 w - - 1 8"),
            ("king safety #2", "r1bq1rk1/1p3pp1/p1n2n1p/2pp4/3P4/2P1PN2/PP1N1PPP/R1BQ1RK1 b - - 3 10"),
            ("endgame #1", "8/8/8/3k4/3P4/8/4K3/8 w - - 0 1"),
            ("endgame #2", "8/4R3/8/3P4/3k4/8/5r2/6K1 w - - 0 1"),
            ("endgame #3", "8/6p1/5p2/4p3/1Bp1k3/6P1/5P2/4K3 w - - 4 60"),
            ("endgame #4", "8/P7/8/8/4k3/8/7p/4K3 b - -  0 60"),

            # --- MATERIAL IMBALANCES ---
            ("white slight +", "r1bqkbnr/1ppp1ppp/p1n5/4p3/B3P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 1 4"),
            ("white up a pawn", "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"),
            ("white winning (+knight)", "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1"),
            ("black up a bishop", "rnbqk1nr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 2"),
            ("exchange sac (R vs N+P)", "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1"),

            # --- POSITIONAL / PAWN STRUCTURE ---
            ("tight mid-game", "r1bqkb1r/1p2pppp/p1np1n2/8/3NP3/2N1B3/PPP2PPP/R2QKB1R w KQkq - 2 7"),
            ("french def (space adv)", "rnbqk2r/pp2bppp/4pn2/2ppP3/3P4/2N2N2/PPP2PPP/R1BQKB1R b KQkq - 0 5"),
            ("isolated queen pawn", "rnbq1rk1/pp2bppp/4pn2/2pp4/2PP4/2N1PN2/PP2BPPP/R1BQ1RK1 w - - 0 1"),
            ("stonewall (closed)", "rnbqk2r/pp3ppp/4pn2/2pp4/2PP1P2/2N2N2/PP2P1PP/R1BQKB1R b KQkq - 0 1"),

            # --- KING SAFETY ---
            ("castled vs uncastled", "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R w KQ - 1 6"),

            # --- TACTICAL BLINDNESS ---
            ("hanging queen", "rnb1kbnr/ppp1pppp/8/3q4/2P5/8/PP1P1PPP/RNBQKBNR b KQkq - 0 3"),
            ("back rank mate threat", "6k1/5ppp/8/8/8/8/8/3R2K1 w - - 0 1"),

            # --- ENDGAME ---
            ("king centralization", "8/5k2/8/4K3/8/8/8/8 w - - 0 1"),
            ("lucena position (win)", "1R6/8/8/8/8/5k2/7p/K7 w - - 0 1"),
            ("philidor position (draw)", "2R5/8/8/8/4k3/8/r7/3K4 w - - 0 1"),
        ]


    def run(self):
        print(f"{'Position':<25} | {'My Eval':<8} |{'Stockfish':<8} | {'Diff':<8}")
        print("-" * 60)

        try:
            engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        except FileNotFoundError:
            print("ERROR: Stockfish engine not found. Check the path.")
            return

        # for analysis
        total_diff = 0
        count = 0
        max_diff = 0

        for name, fen in self.fens:
            board = chess.Board(fen)
            
            # my score
            my_score = self.evaluator.evaluate(board)
            
            # stockfish score
            # depth=0 for a 'static' eval, 
            limit = chess.engine.Limit(depth=0)
            info = engine.analyse(board, limit)
            
            sf_score_obj = info["score"].white()
            
            # Handle Mate scores (e.g., #3)
            if sf_score_obj.is_mate():
                sf_score = f"Mate {sf_score_obj.mate()}"
                diff = "N/A"
            else:
                # Convert centipawns to decimal (150 -> 1.50)
                sf_score = sf_score_obj.score() / 100.0
                diff = round(abs(my_score - sf_score), 2)
                total_diff += diff
                count += 1
                if diff > max_diff:
                    max_diff = diff

            print(f"{name:<25} | {my_score:<8.2f} | {sf_score:<8} | {diff:<8}")
        print("-" * 60)
        print(f"average diff: {round(total_diff / count, 2)}")
        print(f"max diff: {max_diff}")

        engine.quit()

# configuration
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish" 

if __name__ == "__main__":
    test = TestSuite(STOCKFISH_PATH)
    test.run()