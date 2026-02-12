import chess

class ClassicEvaluator:
    def __init__(self):
        # -------------------------------------------------------------------------
        # PeSTO Piece-Square Tables (Midgame and Endgame)
        # Standard localised values used in many engines (RofChade, etc)
        # Source: https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function
        # -------------------------------------------------------------------------

        # format A1..H1 (Rank 1), then A2..H2 (Rank 2), etc.
        # PAWN - MIDDLE GAME
        self.mg_pawn_white = [
            # A,   B,   C,   D,   E,   F,   G,   H
              0,   0,   0,   0,   0,   0,   0,   0, # rank 1
            -35,  -1, -20, -23, -15,  24,  38, -22, 
            -26,  -4,  -4, -10,   3,   3,  33, -12,
            -27,  -2,  -5,  12,  17,   6,  10, -25,
            -14,  13,   6,  21,  23,  12,  17, -23,
             -6,   7,  26,  31,  65,  56,  25, -20,
             98, 134,  61,  95,  68, 126,  34, -11, # rank 7 (promotion approach)
              0,   0,   0,   0,   0,   0,   0,   0, # rank 8 
        ]

        # PAWN - END GAME
        self.eg_pawn_white = [
              0,   0,   0,   0,   0,   0,   0,   0, # rank 1
             13,   8,   8,  10,  13,   0,   2,  -7,
              4,   7,  -6,   1,   0,  -5,  -1,  -8,
             13,   9,  -3,  -7,  -7,  -8,   3,  -1,
             32,  24,  13,   5,  -2,   4,  17,  17,
             94, 100,  85,  67,  56,  53,  82,  84,
            178, 173, 158, 134, 147, 132, 165, 187, # rank 7 (promotion approach)
              0,   0,   0,   0,   0,   0,   0,   0, # rank 8
        ]

        # KNIGHT - MIDDLE GAME
        self.mg_knight_white = [
           -105, -21, -58, -33, -17, -28, -19, -23,
            -29, -53, -12,  -3,  -1,  18, -14, -19,
            -23,  -9,  12,  10,  19,  17,  25, -16,
            -13,   4,  16,  13,  28,  19,  21,  -8,
             -9,  17,  19,  53,  37,  69,  18,  22,
            -47,  60,  37,  65,  84, 129,  73,  44,
            -73, -41,  72,  36,  23,  62,   7, -17,
           -167, -89, -34, -49,  61, -97, -15, -107,
        ]

        # KNIGHT - END GAME
        self.eg_knight_white = [
            -29, -51, -23, -15, -22, -18, -50, -64,
            -42, -20, -10,  -5,  -2, -20, -23, -44,
            -23,  -3,  -1,  15,  10,  -3, -20, -22,
            -18,  -6,  16,  25,  16,  17,   4, -18,
            -17,   3,  22,  22,  22,  11,   8, -18,
            -24, -20,  10,   9,  -1,  -9, -19, -41,
            -25,  -8, -25,  -2,  -9, -25, -24, -52,
            -58, -38, -13, -28, -31, -27, -63, -99,
        ]

        # BISHOP - MIDDLE GAME
        self.mg_bishop_white = [
            -33,  -3, -14, -21, -13, -12, -39, -21,
              4,  15,  16,   0,   7,  21,  33,   1,
              0,  15,  15,  15,  14,  27,  18,  10,
             -6,  13,  13,  26,  34,  12,  10,   4,
             -4,   5,  19,  50,  37,  37,   7,  -2,
            -16,  37,  43,  40,  35,  50,  37,  -2,
            -26,  16, -18, -13,  30,  59,  18, -47,
            -29,   4, -82, -37, -25, -42,   7,  -8,
        ]

        # BISHOP - END GAME
        self.eg_bishop_white = [
            -23, -18, -23, -18, -23, -9, -27, -22,
            -15,  -4, -12,  -4, -3,  -6,  -4, -16,
            -12,  -3,   5,  10,  1,   6,  -5, -11,
             -6,   3,  13,  19,  7,  10,  -3,  -9,
             -3,   9,  12,   9, 14,  10,   3,   2,
              2,  -8,   0,  -1, -2,   6,   0,   4,
             -8,  -4,   7, -12, -3, -13,  -4, -14,
            -14, -21, -11,  -8, -7,  -9, -17, -24,
        ]

        # ROOK - MIDDLE GAME
        self.mg_rook_white = [
            -19, -13,   1,  17, 16,   7, -37, -26,
            -44, -16, -20,  -9, -1,  11,  -6, -71,
            -45, -25, -16, -17,  3,   0,  -5, -33,
            -36, -26, -12,  -1,  9,  -7,   6, -23,
            -24, -11,   7,  26, 24,  35,  -8, -20,
             -5,  19,  26,  36, 17,  45,  61,  16,
             27,  32,  58,  62, 80,  67,  26,  44,
             32,  42,  32,  51, 63,   9,  31,  43,
        ]

        # ROOK - END GAME
        self.eg_rook_white = [
             -9,   2,   3,  -1,  -5, -13,   4, -20,
             -6,  -6,   0,   2,  -9,  -9, -11,  -3,
             -4,   0,  -5,  -1,  -7, -12,  -8, -16,
              3,   5,   8,   4,  -5,  -6,  -8, -11,
              4,   3,  13,   1,   2,   1,  -1,   2,
              7,   7,   7,   5,   4,  -3,  -5,  -3,
             11,  13,  13,  11,  -3,   3,   8,   3,
             13,  10,  18,  15,  12,  12,   8,   5,
        ]

        # QUEEN - MIDDLE GAME
        self.mg_queen_white = [
             -1, -18,  -9, -10, -15, -25, -31, -50,
            -35,  -8,  11,   2,   8,  15,  -3,   1,
            -14,   2, -11,  -2,  -5,   2,  14,   5,
             -9, -26, -28, -10, -10, -11, -17,  -9,
            -27, -27, -16, -16,  -1,  17,  -2,   1,
            -13, -17,   7,   8,  29,  56,  47,  57,
            -24, -39,  -5,   1, -16,  57,  28,  54,
            -28,   0,  29,  12,  59,  44,  43,  45,
        ]

        # QUEEN - END GAME
        self.eg_queen_white = [
            -33, -28, -22, -43,  -5, -32, -20, -41,
            -22, -23, -30, -16, -16, -23, -36, -32,
            -16, -27,  15,   6,   9,  17,  10,   5,
            -18,  28,  19,  47,  31,  34,  39,  23,
              3,  22,  24,  45,  57,  40,  57,  36,
            -20,   6,   9,  49,  47,  35,  19,   9,
            -17,  20,  32,  41,  58,  25,  30,   0,
             -9,  22,  22,  27,  27,  19,  10,  20,
        ]

        # KING - MIDDLE GAME
        self.mg_king_white = [
            -15,  36,  12, -54,   8, -28,  24,  14,
              1,   7,  -8, -64, -43, -16,   9,   8,
            -14, -14, -22, -46, -44, -30, -15, -27,
            -49,  -1, -27, -39, -46, -44, -33, -51,
            -17, -20, -12, -27, -30, -25, -14, -36,
             -9,  24,   2, -16, -20,   6,  22, -22,
             29,  -1, -20,  -7,  -8,  -4, -38, -29,
            -65,  23,  16, -15, -56, -34,   2,  13,
        ]

        # KING - END GAME
        self.eg_king_white = [
            -53, -34, -21, -11, -28, -14, -24, -43,
            -27, -11,   4,  13,  14,   4,  -5, -17,
            -19,  -3,  11,  21,  23,  16,   7,  -9,
            -18,  -4,  21,  24,  27,  23,   9, -11,
             -8,  22,  24,  27,  26,  33,  26,   3,
             10,  17,  23,  15,  20,  45,  44,  13,
            -12,  17,  14,  17,  17,  38,  23,  11,
            -74, -35, -18, -18, -11,  15,   4, -17,
        ]

        # Mirror the tables for black pieces
        # The expression 'i ^ 56' flips the rank (0->7, 1->6, etc) to reverse the perspective.  
        self.mg_pawn_black   = [self.mg_pawn_white[i ^ 56] for i in range(64)]
        self.eg_pawn_black   = [self.eg_pawn_white[i ^ 56] for i in range(64)]
        
        self.mg_knight_black = [self.mg_knight_white[i ^ 56] for i in range(64)]
        self.eg_knight_black = [self.eg_knight_white[i ^ 56] for i in range(64)]
        
        self.mg_bishop_black = [self.mg_bishop_white[i ^ 56] for i in range(64)]
        self.eg_bishop_black = [self.eg_bishop_white[i ^ 56] for i in range(64)]
        
        self.mg_rook_black   = [self.mg_rook_white[i ^ 56] for i in range(64)]
        self.eg_rook_black   = [self.eg_rook_white[i ^ 56] for i in range(64)]
        
        self.mg_queen_black  = [self.mg_queen_white[i ^ 56] for i in range(64)]
        self.eg_queen_black  = [self.eg_queen_white[i ^ 56] for i in range(64)]
        
        self.mg_king_black   = [self.mg_king_white[i ^ 56] for i in range(64)]
        self.eg_king_black   = [self.eg_king_white[i ^ 56] for i in range(64)]


        # -------------------------------------------------------------------------
        # Material Weights (Centipawns)
        # -------------------------------------------------------------------------
        self.mg_value = {
            chess.PAWN: 82, chess.KNIGHT: 337, chess.BISHOP: 365,
            chess.ROOK: 477, chess.QUEEN: 1025, chess.KING: 0
        }
        self.eg_value = {
            chess.PAWN: 94, chess.KNIGHT: 281, chess.BISHOP: 297,
            chess.ROOK: 512, chess.QUEEN: 936, chess.KING: 0
        }

        # -------------------------------------------------------------------------
        # one big pieces dictionary for Fast Lookup
        # -------------------------------------------------------------------------
        self.tables = {
            chess.PAWN: {
                chess.WHITE: {'mg': self.mg_pawn_white, 'eg': self.eg_pawn_white},
                chess.BLACK: {'mg': self.mg_pawn_black, 'eg': self.eg_pawn_black}
            },
            chess.KNIGHT: {
                chess.WHITE: {'mg': self.mg_knight_white, 'eg': self.eg_knight_white},
                chess.BLACK: {'mg': self.mg_knight_black, 'eg': self.eg_knight_black}
            },
            chess.BISHOP: {
                chess.WHITE: {'mg': self.mg_bishop_white, 'eg': self.eg_bishop_white},
                chess.BLACK: {'mg': self.mg_bishop_black, 'eg': self.eg_bishop_black}
            },
            chess.ROOK: {
                chess.WHITE: {'mg': self.mg_rook_white, 'eg': self.eg_rook_white},
                chess.BLACK: {'mg': self.mg_rook_black, 'eg': self.eg_rook_black}
            },
            chess.QUEEN: {
                chess.WHITE: {'mg': self.mg_queen_white, 'eg': self.eg_queen_white},
                chess.BLACK: {'mg': self.mg_queen_black, 'eg': self.eg_queen_black}
            },
            chess.KING: {
                chess.WHITE: {'mg': self.mg_king_white, 'eg': self.eg_king_white},
                chess.BLACK: {'mg': self.mg_king_black, 'eg': self.eg_king_black}
            }
        }


        # Game phase weights for tapered evaluation
        self.game_phase_inc = {
            chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 1,
            chess.ROOK: 2, chess.QUEEN: 4, chess.KING: 0
        }

    def evaluate(self, board: chess.Board):
        """
        Returns a decimal score from the perspective of White.
        (+) White winning, (-) Black winning.
        """
        # Check for game over conditions
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return -9999.0 # Black wins
            else:
                return 9999.0 # White wins
        if board.is_insufficient_material() or board.is_stalemate():
            return 0.0

        # Setup variables
        mg_score = 0
        eg_score = 0
        game_phase = 0

        # Iterate over all pieces to sum material + PST
        # Note: python-chess piece maps are faster than iterating all 64 squares
        for idx, piece in board.piece_map().items():
            pt = piece.piece_type
            color = piece.color

            # fast dictionary lookup
            mg_table = self.tables[pt][color]['mg']
            eg_table = self.tables[pt][color]['eg']

            # Calculate score: material + position
            mg_val = self.mg_value[pt] + mg_table[idx]
            eg_val = self.eg_value[pt] + eg_table[idx]

            if color == chess.WHITE:
                mg_score += mg_val
                eg_score += eg_val
            else:
                mg_score -= mg_val
                eg_score -= eg_val

            # Game Phase evaluation
            if pt != chess.PAWN and pt != chess.KING: 
                game_phase += self.game_phase_inc[pt]


        # Moblitiy bonuses
        mobility_bonus = {
            chess.KNIGHT: 4, # 4cp per square
            chess.BISHOP: 5,
            chess.ROOK: 2,
            chess.QUEEN: 1
        }
        for pt in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            # white pieces
            for square in board.pieces(pt, chess.WHITE):
                attacks = board.attacks(square)
                # logic fix: exclude squares occupied by own pieces
                mobility = len(attacks & ~board.occupied_co[chess.WHITE])
                val = mobility * mobility_bonus[pt]
                mg_score += val
                eg_score += val
            # black pieces
            for square in board.pieces(pt, chess.BLACK):
                attacks = board.attacks(square)
                mobility = len(attacks & ~board.occupied_co[chess.BLACK])
                val = mobility * mobility_bonus[pt]
                mg_score -= val
                eg_score -= val

        # PAWN STRUCTURE
        white_pawns_bb = board.occupied_co[chess.WHITE] & board.pawns
        black_pawns_bb = board.occupied_co[chess.BLACK] & board.pawns
        doubled_penalty = 15
        isolated_penalty = 20

        # passed pawns bonuses (by rank)
        passed_mg = [0, 5, 10, 20, 35, 60, 100, 0]
        passed_eg = [0, 10, 20, 40, 70, 120, 200, 0]     

        # whte pawns
        for square in board.pieces(chess.PAWN, chess.WHITE):
            file = chess.square_file(square)
            rank = chess.square_rank(square)

            # ISOLATED pawns
            adjacent_files_mask = 0
            if file > 0: adjacent_files_mask |= chess.BB_FILES[file - 1]
            if file < 7: adjacent_files_mask |= chess.BB_FILES[file + 1]
            if (white_pawns_bb & adjacent_files_mask) == 0:
                mg_score -= isolated_penalty
                eg_score -= isolated_penalty

            # DOUBLED pawns
            file_mask = chess.BB_FILES[file]
            if (white_pawns_bb & file_mask).bit_count() > 1:
                mg_score -= doubled_penalty
                eg_score -= doubled_penalty

            # PASSED pawns
            front_span_files = adjacent_files_mask | file_mask
            ranks_ahead_mask = ~((1 << (8 * (rank + 1))) - 1)
            is_passed = (black_pawns_bb & front_span_files & ranks_ahead_mask) == 0

            if is_passed:
                mg_score += passed_mg[rank]
                eg_score += passed_eg[rank]

        # black pawns
        for square in board.pieces(chess.PAWN, chess.BLACK):
            file = chess.square_file(square)
            rank = chess.square_rank(square)

            # ISOLATED pawns
            adjacent_files_mask = 0
            if file > 0: adjacent_files_mask |= chess.BB_FILES[file - 1]
            if file < 7: adjacent_files_mask |= chess.BB_FILES[file + 1]
            if (black_pawns_bb & adjacent_files_mask) == 0:
                mg_score += isolated_penalty
                eg_score += isolated_penalty

            # DOUBLED pawns
            file_mask = chess.BB_FILES[file]
            if (black_pawns_bb & file_mask).bit_count() > 1:
                mg_score += doubled_penalty
                eg_score += doubled_penalty

            # PASSED pawns
            front_span_files = adjacent_files_mask | file_mask
            ranks_below_mask = (1 << (8 * rank)) - 1
            is_passed = (white_pawns_bb & front_span_files & ranks_below_mask) == 0

            if is_passed:
                mg_score -= passed_mg[7 - rank]
                eg_score -= passed_eg[7 - rank]


        # Tapered evaluation formula
        # Total phase is roughly 24 (4*N + 4*B + 4*R + 2*Q). 
        # If phase > 24, cap it.
        mg_phase = game_phase
        if mg_phase > 24: mg_phase = 24
        eg_phase = 24 - mg_phase

        final_score = (mg_score * mg_phase + eg_score * eg_phase) / 24

        # tempo bonus (side to move)
        if board.turn == chess.WHITE:
            final_score += 15
        else:
            final_score -= 15

        # return decimal score
        return final_score / 100.0

# Usage Example
# if __name__ == "__main__":
#     evaluator = ClassicEvaluator()
    
#     # Starting position
#     board = chess.Board()
#     print(f"Start Pos: {evaluator.evaluate(board)}")

#     # Make some moves
#     board.push_san("e4")
#     board.push_san("d5") # Scandinavian
#     print(f"After e4 d5: {evaluator.evaluate(board)}")
    