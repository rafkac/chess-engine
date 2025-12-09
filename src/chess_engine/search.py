import chess
import time

class SearchEngine:
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.nodes_visited = 0
        self.best_move = None

        # move ordering heuristics
        self.piece_values = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, 
            chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
        }

    def order_moves(self, board, moves):
        """
        Sorts moves to improve Alpha-Beta pruning efficiency.
        Order:
        1. Captures (ordered by value difference)
        2. Promotions
        3. Quiet moves
        """
        score_moves = []
        for move in moves:
            score = 0
            # 1. Captures
            if board.is_capture(move):
                # MVV-LVA logic
                victim_type = board.piece_type_at(move.to_square)
                aggressor_type = board.piece_type_at(move.from_square)
                
                # en passant
                if board.is_en_passant(move):
                    victim_type = chess.PAWN
                
                if victim_type:
                    score = 10 * self.piece_values[victim_type] - self.piece_values[aggressor_type]
            
            # 2. Promotions
            if move.promotion:
                score += self.piece_values[move.promotion] * 10 # to match the capture scale

            score_moves.append((score, move))

        # sort moves descending by score
        score_moves.sort(key=lambda x: x[0], reverse=True)
        return [move for score, move in score_moves]
    

    def quiescence(self, board, alpha, beta):
        """
        Quiescence search to avoid horizon effect.
        Helps to make better trade decisions in volatile positions.
        """
        self.nodes_visited += 1
        
        # stand pat (static evaluation)
        stand_pat = self.evaluator.evaluate(board)

        # pruning based on turn
        if board.turn == chess.WHITE:
            # white maxiising 
            if stand_pat >= beta:
                return beta
            if stand_pat > alpha:
                alpha = stand_pat
        else:
            # black minimising
            if stand_pat <= alpha:
                return alpha
            if stand_pat < beta:
                beta = stand_pat

        # check captures
        moves = self.order_moves(board, [m for m in board.legal_moves if board.is_capture(m)])

        for move in moves:
            board.push(move)
            score = self.quiescence(board, alpha, beta)
            board.pop()

            if board.turn == chess.WHITE:
                if score >= beta: return beta
                if score > alpha: alpha = score
            else:
                if score <= alpha: return alpha
                if score < beta: beta = score

        if board.turn == chess.WHITE:
            return alpha
        else:
            return beta

    def minimax(self, board, depth, alpha, beta):
        self.nodes_visited += 1

        # termination condition
        if depth == 0:
            return self.quiescence(board, alpha, beta)
        
        if board.is_checkmate():
            # if white is mated, score is -infinity. If black is mated, score is +infinity.
            # we add 'depth' to prefer faster mates.
            if board.turn == chess.WHITE:
                return -99999 - depth # White lost
            else:
                return 99999 + depth  # Black lost
                
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        # move Generation
        moves = self.order_moves(board, list(board.legal_moves))

        # white maximising
        if board.turn == chess.WHITE:
            max_eval = -float('inf')
            for move in moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta)
                board.pop()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                # beta cutoff
                if beta <= alpha:
                    break
            return max_eval

        # black minimising
        else:
            min_eval = float('inf')
            for move in moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta)
                board.pop()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                # alpha cutoff
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board, depth=3):
        self.nodes_visited = 0
        self.best_move = None
        start_time = time.time()
        
        alpha = -float('inf')
        beta = float('inf')
        
        moves = self.order_moves(board, list(board.legal_moves))
        
        if board.turn == chess.WHITE:
            best_val = -float('inf')
            for move in moves:
                board.push(move)
                val = self.minimax(board, depth - 1, alpha, beta)
                board.pop()
                
                if val > best_val:
                    best_val = val
                    self.best_move = move
                alpha = max(alpha, best_val)
        else:
            best_val = float('inf')
            for move in moves:
                board.push(move)
                val = self.minimax(board, depth - 1, alpha, beta)
                board.pop()
                
                if val < best_val:
                    best_val = val
                    self.best_move = move
                beta = min(beta, best_val)

        elapsed = time.time() - start_time
        # print(f"Depth: {depth} | Nodes: {self.nodes_visited} | Time: {elapsed:.3f}s")
        # print(f"Best Move: {self.best_move} | Score: {best_val:.2f}")
        
        return self.best_move, best_val