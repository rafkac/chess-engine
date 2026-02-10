import chess
from chess_engine.evaluator import ClassicEvaluator
from chess_engine.search import SearchEngine

class ChessBot:
    def __init__(self):
        self.board = chess.Board()
        self.evaluator = ClassicEvaluator()
        self.search_engine = SearchEngine(self.evaluator)

    def get_best_move(self, depth=3):
        """
        Calculates the best move using the SearchEngine.
        """
        # increase depth in the endgame
        game_phase_values = {
            chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 1,
            chess.ROOK: 2, chess.QUEEN: 4, chess.KING: 0
        }
        phase = 0
        for piece in self.board.piece_map().values():
            phase += game_phase_values[piece.piece_type]

        if 12 >= phase >= 6:
            depth += 1
        elif phase <= 5:
            depth += 2

        best_move = self.search_engine.get_best_move(self.board, depth)
        return best_move
    

def console_mode():
    bot = ChessBot()
    print(f"Welcome to chess bot!")
    print("Type 'quit' to exit.")
    print("Enter moves in UCI format (e.g., e2e4, a7a8q) or SAN (e.g., Nf3, O-O).")
    
    # Select Side
    while True:
        side = input("Choose side (white/black): ").lower()
        if side in ["white", "w"]:
            player_color = chess.WHITE
            break
        elif side in ["black", "b"]:
            player_color = chess.BLACK
            break
    
    while not bot.board.is_game_over():
        print(f"\n{bot.board}")
        print("-" * 20)
        
        if bot.board.turn == player_color:
            # Human Turn
            while True:
                move_str = input("Your move: ")
                if move_str == "quit": return
                
                try:
                    # Try parsing SAN first (e.g. "Nf3"), then UCI (e.g. "g1f3")
                    try:
                        move = bot.board.parse_san(move_str)
                    except:
                        move = chess.Move.from_uci(move_str)
                    
                    if move in bot.board.legal_moves:
                        bot.board.push(move)
                        break
                    else:
                        print("Illegal move, try again.")
                except:
                    print("Invalid format. Use SAN (Nf3) or UCI (e2e4).")
        else:
            # AI Turn
            print("Bot is thinking...")
            best_move, score, time = bot.get_best_move(depth=4) # depth
            bot.board.push(best_move)
            print(f"After {time:.2f}s bot played: {best_move}")

    print("Game Over!")
    print(bot.board.outcome())


if __name__ == "__main__":
    console_mode()