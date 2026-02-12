import chess
from chess_engine.evaluator import ClassicEvaluator
from chess_engine.search import SearchEngine
# from main import ChessBot
from chess_engine.evaluator import ClassicEvaluator
from chess_engine.search import SearchEngine
from chess_engine.search_timed import SearchEngineTimed


def simulate_match(engine_old, engine_new):
    """Play from multiple different openings"""
    # Standard opening positions (after 4-6 moves)
    openings = [
        ("Starting", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
        ("Italian", "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"),
        ("Sicilian", "rnbqkb1r/pp1ppppp/5n2/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"),
        ("French", "rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3"),
        ("Caro-Kann", "rnbqkbnr/pp2pppp/2p5/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3"),
        ("Queen's Gambit", "rnbqkb1r/ppp1pppp/5n2/3p4/2PP4/8/PP2PPPP/RNBQKBR w KQkq - 1 3"),
    ]
    
    results = {"new": 0, "old": 0, "draws": 0}
    
    for _, fen in openings:
        # Play with new engine as white
        result = play_game(engine_new, engine_old, fen)
        if result == 1:
            results["new"] += 1
        elif result == -1:
            results["old"] += 1
        else:
            results["draws"] += 1
        
        # Play with new engine as black
        result = play_game(engine_old, engine_new, fen)
        if result == -1:
            results["new"] += 1
        elif result == 1:
            results["old"] += 1
        else:
            results["draws"] += 1

    return results


def play_game(white_engine, black_engine, start_fen):
    """Returns 1 if white wins, -1 if black wins, 0 if draw"""
    board = chess.Board(start_fen)
    move_count = 0
    max_moves = 200  # Prevent infinite games
    
    while not board.is_game_over() and move_count < max_moves:
        engine = white_engine if board.turn == chess.WHITE else black_engine
        move, _, _ = engine.get_best_move(board, depth=1)
        board.push(move)
        move_count += 1
    
    if board.is_checkmate():
        return 1 if board.turn == chess.BLACK else -1
    return 0  # Draw


if __name__ == "__main__":
    # evaluator_old = ClassicEvaluator()  # old version
    # evaluator_new = ClassicEvaluator()     # new version
    
    # engine_old = SearchEngine(evaluator_old)
    # engine_new = SearchEngine(evaluator_new)
    
    # results = simulate_match(engine_old, engine_new)
    
    # print(f"Results over {len(openings) * 2} games:")
    # print(f"New engine: {results['new']} wins")
    # print(f"Old engine: {results['old']} wins")
    # print(f"Draws: {results['draws']}")
    
    # # Simple strength indicator
    # if results['new'] > results['old']:
    #     print("✓ New version is stronger!")
    # elif results['new'] < results['old']:
    #     print("✗ Old version was better")
    # else:
    #     print("≈ Similar strength")


    # visualise a game against itself in terminal
    board = chess.Board()
    evaluator = ClassicEvaluator()
    search = SearchEngine(evaluator)
    search_timed = SearchEngineTimed(evaluator)

    white = {'nodes': 0, 'time': 0.0}
    black = {'nodes': 0, 'time': 0.0}

    while not board.is_game_over():
        print(board)
        
        if board.turn == chess.WHITE:
            # AI Turn
            print("-" * 20)
            print("White bot...")

            best_move, score, nodes, time = search_timed.get_best_move_depth(board, depth=3) # depth limit
            white['nodes'] += nodes
            white['time'] += time
            board.push(best_move)
            print(f"After {time:.2f}s bot played: {best_move}")
        else:
            # AI Turn
            print("Black bot...")

            best_move, score, nodes, time = search_timed.get_best_move(board, time_limit=5.0) # time limit
            black['nodes'] += nodes
            black['time'] += time
            board.push(best_move)
            print(f"After {time:.2f}s bot played: {best_move}")
        
    print("Game Over!")
    print(board.outcome())
    print(f"White: {(white['nodes']/white['time']):.2f} nodes/s  ({white['nodes']} nodes in {white['time']:.2f}s)")
    print(f"Black: {(black['nodes']/black['time']):.2f} nodes/s  ({black['nodes']} nodes in {black['time']:.2f}s)")