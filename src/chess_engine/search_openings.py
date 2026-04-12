import chess
import chess.polyglot
import time


"""
search with opening book implementation
"""


class SearchEngine:
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.nodes_visited = 0
        self.best_move = None

        # Transposition Table
        self.tt = {}
        self.TT_EXACT = 0  # exact score (PV node)
        self.TT_LOWER = 1  # fail-high (alpha raised, score >= beta)
        self.TT_UPPER = 2  # fail-low (beta lowered, score <= alpha)
        
        # TT Statistics for monitoring
        self.tt_hits = 0
        self.tt_probes = 0
        self.tt_cutoffs = 0
        
        # move ordering heuristics
        self.piece_values = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, 
            chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
        }

    def clear_tt(self):
        """Clear transposition table (optional between games)"""
        self.tt.clear()
        self.tt_hits = 0
        self.tt_probes = 0
        self.tt_cutoffs = 0


    def order_moves(self, board, moves, tt_move=None):
        """
        Sorts moves to improve Alpha-Beta pruning
        Order priority:
        1. TT move (best move from previous search at this position)
        1. Captures (ordered by value difference)
        2. Promotions
        3. Quiet moves
        """
        score_moves = []
        for move in moves:
            score = 0

            # 0. TT move gets highest priority
            if tt_move and move == tt_move:
                score = 10000
                        
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
        """
        Minimax with alpha-beta pruning and transposition table
        """
        self.nodes_visited += 1

        alpha_orig = alpha
	
        # === TRANSPOSITION TABLE PROBE ===
        # Uses chess.polyglot.zobrist_hash()
        zobrist = chess.polyglot.zobrist_hash(board)
        tt_move = None
        self.tt_probes += 1
        
        if zobrist in self.tt:
            tt_depth, tt_score, tt_flag, tt_move_stored = self.tt[zobrist]
            
            # Only use TT entry if it was searched to at least the same depth
            if tt_depth >= depth:
                self.tt_hits += 1
                
                if tt_flag == self.TT_EXACT:
                    self.tt_cutoffs += 1
                    return tt_score
                elif tt_flag == self.TT_LOWER:
                    alpha = max(alpha, tt_score)
                elif tt_flag == self.TT_UPPER:
                    beta = min(beta, tt_score)
                
                # Cutoff if bounds crossed
                if alpha >= beta:
                    self.tt_cutoffs += 1
                    return tt_score
            
            # Store TT move for move ordering even if depth is insufficient
            tt_move = tt_move_stored

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

        # move generation with TT move priority
        moves = self.order_moves(board, list(board.legal_moves), tt_move)

        best_move_this_node = None

        # === SEARCH ===
        # white maximising
        if board.turn == chess.WHITE:
            max_eval = -float('inf')
            for move in moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta)
                board.pop()
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move_this_node = move
                alpha = max(alpha, eval_score)
                
                # beta cutoff
                if beta <= alpha:
                    break
	
            # Store in transposition table
            tt_flag = self.TT_EXACT
            if max_eval <= alpha_orig:
                tt_flag = self.TT_UPPER
            elif max_eval >= beta:
                tt_flag = self.TT_LOWER
            self.tt[zobrist] = (depth, max_eval, tt_flag, best_move_this_node)
                            
            return max_eval

        # black minimising
        else:
            min_eval = float('inf')
            for move in moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta)
                board.pop()
                
                if eval_score < min_eval:
                    min_eval = eval_score
                beta = min(beta, eval_score)
                
                # alpha cutoff
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board, depth=3):
        self.nodes_visited = 0
        self.best_move = None
        self.tt_hits = 0
        self.tt_probes = 0
        self.tt_cutoffs = 0

        start_time = time.time()
        
        alpha = -float('inf')
        beta = float('inf')


        # Check TT for best move from previous search
        zobrist = chess.polyglot.zobrist_hash(board)
        tt_move = None
        if zobrist in self.tt:
            _, _, _, tt_move = self.tt[zobrist]


        moves = self.order_moves(board, list(board.legal_moves), tt_move)
        
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
        
        return self.best_move, best_val, elapsed