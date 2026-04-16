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

        # =====================================================================
        # NEW FEATURE WEIGHTS (placeholder — to be tuned via regression)
        # All values in centipawns. Kept deliberately small so the engine
        # behaves almost identically before tuning.
        # =====================================================================

        # --- [NEW 1] King safety: pawn shield ---
        # Bonus per pawn on the 2nd/3rd rank directly in front of the castled king.
        # Only evaluated for kings that have castled (on files A-C or F-H).
        self.mg_pawn_shield = 1          # middlegame bonus per shield pawn
        self.eg_pawn_shield = 0          # irrelevant in endgame

        # --- [NEW 2] King safety: attack zone pressure ---
        # Accumulated penalty when enemy pieces attack squares adjacent to the king.
        # Weights per attacking piece type (heavier pieces count more).
        self.king_attack_weight = {
            chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 1,
            chess.ROOK: 1, chess.QUEEN: 2, chess.KING: 0
        }
        # The raw sum of attack weights is squared and multiplied by this factor.
        # Quadratic scaling means two attackers are more than twice as dangerous.
        self.mg_king_zone_factor = 1     # cp per (attack_units²)
        self.eg_king_zone_factor = 0

        # --- [NEW 3] Rook placement ---
        self.mg_rook_open_file      = 1  # rook on file with no pawns at all
        self.eg_rook_open_file      = 1
        self.mg_rook_semi_open_file = 1  # rook on file with no friendly pawns
        self.eg_rook_semi_open_file = 0
        self.mg_rook_seventh_rank   = 1  # rook on the 7th (2nd for black)
        self.eg_rook_seventh_rank   = 1

        # --- [NEW 4] Pawn structure: backward pawns ---
        # A backward pawn: no friendly pawn on adjacent files can advance to
        # support it, and the stop square is controlled by an enemy pawn.
        self.mg_backward_penalty = 1
        self.eg_backward_penalty = 1

        # --- [NEW 5] Pawn structure: connected pawns ---
        # A pawn defended by another friendly pawn (diagonally).
        self.mg_connected_bonus = 1
        self.eg_connected_bonus = 1

        # --- [NEW 6] Knight outposts ---
        # A knight on rank 4-6 (white) / 3-5 (black) that cannot be attacked
        # by any enemy pawn, and is supported by a friendly pawn.
        self.mg_knight_outpost = 1
        self.eg_knight_outpost = 1

        # --- [NEW 7] Bad bishop ---
        # Penalty per own pawn on the same colour square as own bishop.
        self.mg_bad_bishop_penalty = 1   # per pawn on same colour
        self.eg_bad_bishop_penalty = 1

        # --- [NEW 8] King-passer proximity (endgame) ---
        # In the endgame, the friendly king should escort its own passed pawns
        # and the enemy king should be far from them. Measured in file+rank
        # distance (Chebyshev / king-move distance).
        self.eg_king_friend_passer  = 1  # bonus: own king close to own passer
        self.eg_king_enemy_passer   = 1  # bonus: enemy king far from our passer

        # =====================================================================
        # Pre-built helper data for king zone lookup
        # king_zone[sq] = SquareSet of the 8 squares surrounding sq (+ sq itself)
        # =====================================================================
        self.king_zone = []
        for sq in range(64):
            zone = chess.SquareSet()
            kr = chess.square_rank(sq)
            kf = chess.square_file(sq)
            for dr in [-1, 0, 1]:
                for df in [-1, 0, 1]:
                    r2 = kr + dr
                    f2 = kf + df
                    if 0 <= r2 <= 7 and 0 <= f2 <= 7:
                        zone.add(chess.square(f2, r2))
            self.king_zone.append(zone)

        # Squares that are "light" (True) or "dark" (False).
        # A square is light if (file + rank) is even in chess convention.
        # chess.square_file(sq) + chess.square_rank(sq) even → light square
        self.is_light_square = [
            (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 0
            for sq in range(64)
        ]


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


        # Mobility bonuses
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

        # Track passed pawns for king-passer proximity (NEW 8)
        white_passers = []
        black_passers = []

        # white pawns
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
                white_passers.append(square)

            # --- [NEW 4] BACKWARD pawns ---
            # A pawn is backward if:
            #   1) no friendly pawn on adjacent files is on the same rank or behind
            #      (i.e. it can't be supported by advancing a neighbouring pawn)
            #   2) the stop square (one square ahead) is controlled by an enemy pawn
            if adjacent_files_mask:
                ranks_behind_or_equal = (1 << (8 * (rank + 1))) - 1
                has_support = (white_pawns_bb & adjacent_files_mask & ranks_behind_or_equal) != 0
                if not has_support:
                    stop_sq = square + 8  # one rank ahead for white
                    if stop_sq <= 63:
                        # is stop square attacked by an enemy pawn?
                        stop_file = chess.square_file(stop_sq)
                        stop_rank = chess.square_rank(stop_sq)
                        # enemy pawn attacks stop_sq from rank+1 on adjacent files
                        left_attacker = chess.square(stop_file - 1, stop_rank + 1) if stop_file > 0 and stop_rank < 7 else None
                        right_attacker = chess.square(stop_file + 1, stop_rank + 1) if stop_file < 7 and stop_rank < 7 else None
                        enemy_controls_stop = False
                        if left_attacker is not None and board.piece_at(left_attacker) == chess.Piece(chess.PAWN, chess.BLACK):
                            enemy_controls_stop = True
                        if right_attacker is not None and board.piece_at(right_attacker) == chess.Piece(chess.PAWN, chess.BLACK):
                            enemy_controls_stop = True
                        if enemy_controls_stop:
                            mg_score -= self.mg_backward_penalty
                            eg_score -= self.eg_backward_penalty

            # --- [NEW 5] CONNECTED pawns ---
            # Check if this pawn is defended by a friendly pawn (diagonally behind).
            defend_left  = chess.square(file - 1, rank - 1) if file > 0 and rank > 0 else None
            defend_right = chess.square(file + 1, rank - 1) if file < 7 and rank > 0 else None
            if (defend_left is not None and board.piece_at(defend_left) == chess.Piece(chess.PAWN, chess.WHITE)) or \
               (defend_right is not None and board.piece_at(defend_right) == chess.Piece(chess.PAWN, chess.WHITE)):
                mg_score += self.mg_connected_bonus
                eg_score += self.eg_connected_bonus

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
                black_passers.append(square)

            # --- [NEW 4] BACKWARD pawns (black) ---
            if adjacent_files_mask:
                ranks_above_or_equal = ~((1 << (8 * rank)) - 1) & 0xFFFFFFFFFFFFFFFF
                has_support = (black_pawns_bb & adjacent_files_mask & ranks_above_or_equal) != 0
                if not has_support:
                    stop_sq = square - 8  # one rank ahead for black (downward)
                    if stop_sq >= 0:
                        stop_file = chess.square_file(stop_sq)
                        stop_rank = chess.square_rank(stop_sq)
                        left_attacker = chess.square(stop_file - 1, stop_rank - 1) if stop_file > 0 and stop_rank > 0 else None
                        right_attacker = chess.square(stop_file + 1, stop_rank - 1) if stop_file < 7 and stop_rank > 0 else None
                        enemy_controls_stop = False
                        if left_attacker is not None and board.piece_at(left_attacker) == chess.Piece(chess.PAWN, chess.WHITE):
                            enemy_controls_stop = True
                        if right_attacker is not None and board.piece_at(right_attacker) == chess.Piece(chess.PAWN, chess.WHITE):
                            enemy_controls_stop = True
                        if enemy_controls_stop:
                            mg_score += self.mg_backward_penalty
                            eg_score += self.eg_backward_penalty

            # --- [NEW 5] CONNECTED pawns (black) ---
            defend_left  = chess.square(file - 1, rank + 1) if file > 0 and rank < 7 else None
            defend_right = chess.square(file + 1, rank + 1) if file < 7 and rank < 7 else None
            if (defend_left is not None and board.piece_at(defend_left) == chess.Piece(chess.PAWN, chess.BLACK)) or \
               (defend_right is not None and board.piece_at(defend_right) == chess.Piece(chess.PAWN, chess.BLACK)):
                mg_score -= self.mg_connected_bonus
                eg_score -= self.eg_connected_bonus

        # bishop pair bonus
        bishop_pair_bonus = 30
        white_bishops = len(board.pieces(chess.BISHOP, chess.WHITE))
        black_bishops = len(board.pieces(chess.BISHOP, chess.BLACK))
        
        if white_bishops == 2:
            mg_score += bishop_pair_bonus
            eg_score += bishop_pair_bonus
        if black_bishops == 2:
            mg_score -= bishop_pair_bonus
            eg_score -= bishop_pair_bonus


        # =================================================================
        # NEW FEATURES
        # =================================================================

        # --- [NEW 1] King safety: pawn shield ---
        # For a castled king (files a-c = queenside, files f-h = kingside),
        # count friendly pawns on the 2nd and 3rd ranks in front of the king.
        for color in [chess.WHITE, chess.BLACK]:
            king_sq = board.king(color)
            if king_sq is None:
                continue
            king_file = chess.square_file(king_sq)
            king_rank = chess.square_rank(king_sq)

            # Only evaluate shield if king is on a castled-looking position
            # (files 0-2 or 5-7, on the back two ranks for that colour)
            is_castled_zone = False
            if color == chess.WHITE and king_rank <= 1 and (king_file <= 2 or king_file >= 5):
                is_castled_zone = True
            elif color == chess.BLACK and king_rank >= 6 and (king_file <= 2 or king_file >= 5):
                is_castled_zone = True

            if is_castled_zone:
                shield_count = 0
                # Check the 3 files around the king (king_file-1, king_file, king_file+1)
                for f in range(max(0, king_file - 1), min(8, king_file + 2)):
                    if color == chess.WHITE:
                        # Pawns on ranks 1,2 (indices 1,2) shield the white king
                        for r in [1, 2]:
                            sq = chess.square(f, r)
                            if board.piece_at(sq) == chess.Piece(chess.PAWN, chess.WHITE):
                                shield_count += 1
                    else:
                        # Pawns on ranks 6,5 (indices 6,5) shield the black king
                        for r in [6, 5]:
                            sq = chess.square(f, r)
                            if board.piece_at(sq) == chess.Piece(chess.PAWN, chess.BLACK):
                                shield_count += 1

                val_mg = shield_count * self.mg_pawn_shield
                val_eg = shield_count * self.eg_pawn_shield
                if color == chess.WHITE:
                    mg_score += val_mg
                    eg_score += val_eg
                else:
                    mg_score -= val_mg
                    eg_score -= val_eg

        # --- [NEW 2] King safety: attack zone pressure ---
        # For each side, count how many enemy pieces attack the king zone.
        # Use quadratic scaling: danger = factor * (sum_of_weights)²
        for color in [chess.WHITE, chess.BLACK]:
            king_sq = board.king(color)
            if king_sq is None:
                continue
            zone = self.king_zone[king_sq]
            enemy = not color
            attack_units = 0

            for pt in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                for sq in board.pieces(pt, enemy):
                    piece_attacks = board.attacks(sq)
                    if piece_attacks & zone:
                        attack_units += self.king_attack_weight[pt]

            # Quadratic danger
            danger_mg = self.mg_king_zone_factor * (attack_units * attack_units)
            danger_eg = self.eg_king_zone_factor * (attack_units * attack_units)

            # This is a penalty for the side whose king is being attacked
            if color == chess.WHITE:
                mg_score -= danger_mg
                eg_score -= danger_eg
            else:
                mg_score += danger_mg
                eg_score += danger_eg


        # --- [NEW 3] Rook placement ---
        for color in [chess.WHITE, chess.BLACK]:
            sign = 1 if color == chess.WHITE else -1
            own_pawns = board.occupied_co[color] & board.pawns
            all_pawns = white_pawns_bb | black_pawns_bb

            for sq in board.pieces(chess.ROOK, color):
                f = chess.square_file(sq)
                r = chess.square_rank(sq)
                file_mask = chess.BB_FILES[f]

                # Open file: no pawns at all on this file
                if (all_pawns & file_mask) == 0:
                    mg_score += sign * self.mg_rook_open_file
                    eg_score += sign * self.eg_rook_open_file
                # Semi-open file: no friendly pawns on this file
                elif (own_pawns & file_mask) == 0:
                    mg_score += sign * self.mg_rook_semi_open_file
                    eg_score += sign * self.eg_rook_semi_open_file

                # Rook on 7th rank (rank 6 for white, rank 1 for black)
                if (color == chess.WHITE and r == 6) or (color == chess.BLACK and r == 1):
                    mg_score += sign * self.mg_rook_seventh_rank
                    eg_score += sign * self.eg_rook_seventh_rank


        # --- [NEW 6] Knight outposts ---
        # A knight on rank 4-6 (white) / 3-5 (black) that is:
        #   a) supported by a friendly pawn
        #   b) cannot be attacked by any enemy pawn (no enemy pawn on adjacent
        #      files that could advance to reach the knight's rank)
        for color in [chess.WHITE, chess.BLACK]:
            sign = 1 if color == chess.WHITE else -1
            enemy_pawns = black_pawns_bb if color == chess.WHITE else white_pawns_bb
            friendly_pawns = white_pawns_bb if color == chess.WHITE else black_pawns_bb

            for sq in board.pieces(chess.KNIGHT, color):
                f = chess.square_file(sq)
                r = chess.square_rank(sq)

                # Must be in the opponent's half
                if color == chess.WHITE and r < 3:
                    continue  # not deep enough
                if color == chess.BLACK and r > 4:
                    continue

                # Check: no enemy pawn on adjacent files can attack this square.
                # For white knight on (f, r): enemy black pawns attack from
                # (f±1, r+1). So any black pawn on adjacent files at rank > r
                # could potentially advance to attack.
                adj_files_mask = 0
                if f > 0: adj_files_mask |= chess.BB_FILES[f - 1]
                if f < 7: adj_files_mask |= chess.BB_FILES[f + 1]

                if color == chess.WHITE:
                    # enemy pawns on adjacent files at rank >= r that could
                    # advance down to attack: any black pawn on adj files with
                    # rank > r could reach (f±1, r+1) and attack our knight
                    ranks_that_threaten = ~((1 << (8 * (r + 1))) - 1)
                else:
                    ranks_that_threaten = (1 << (8 * r)) - 1

                can_be_attacked = (enemy_pawns & adj_files_mask & ranks_that_threaten) != 0
                if can_be_attacked:
                    continue  # not a safe outpost

                # Is the knight supported by a friendly pawn?
                if color == chess.WHITE:
                    sup_left  = chess.square(f - 1, r - 1) if f > 0 and r > 0 else None
                    sup_right = chess.square(f + 1, r - 1) if f < 7 and r > 0 else None
                    supported = False
                    if sup_left is not None and board.piece_at(sup_left) == chess.Piece(chess.PAWN, chess.WHITE):
                        supported = True
                    if sup_right is not None and board.piece_at(sup_right) == chess.Piece(chess.PAWN, chess.WHITE):
                        supported = True
                else:
                    sup_left  = chess.square(f - 1, r + 1) if f > 0 and r < 7 else None
                    sup_right = chess.square(f + 1, r + 1) if f < 7 and r < 7 else None
                    supported = False
                    if sup_left is not None and board.piece_at(sup_left) == chess.Piece(chess.PAWN, chess.BLACK):
                        supported = True
                    if sup_right is not None and board.piece_at(sup_right) == chess.Piece(chess.PAWN, chess.BLACK):
                        supported = True

                if supported:
                    mg_score += sign * self.mg_knight_outpost
                    eg_score += sign * self.eg_knight_outpost


        # --- [NEW 7] Bad bishop ---
        # For each bishop, count how many own pawns sit on the same colour square.
        for color in [chess.WHITE, chess.BLACK]:
            sign = 1 if color == chess.WHITE else -1
            for bishop_sq in board.pieces(chess.BISHOP, color):
                bishop_light = self.is_light_square[bishop_sq]
                bad_pawn_count = 0
                for pawn_sq in board.pieces(chess.PAWN, color):
                    if self.is_light_square[pawn_sq] == bishop_light:
                        bad_pawn_count += 1
                # Penalty: more own pawns on same colour = worse bishop
                mg_score -= sign * bad_pawn_count * self.mg_bad_bishop_penalty
                eg_score -= sign * bad_pawn_count * self.eg_bad_bishop_penalty


        # --- [NEW 8] King-passer proximity (endgame-only) ---
        # In the endgame the king should escort its own passers and
        # block the opponent's. We use Chebyshev distance (king-move distance).
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)

        if white_king is not None and black_king is not None:
            wk_file = chess.square_file(white_king)
            wk_rank = chess.square_rank(white_king)
            bk_file = chess.square_file(black_king)
            bk_rank = chess.square_rank(black_king)

            for passer in white_passers:
                pf = chess.square_file(passer)
                pr = chess.square_rank(passer)
                # Own king close to own passer: bonus (lower distance = better)
                friend_dist = max(abs(wk_file - pf), abs(wk_rank - pr))
                enemy_dist  = max(abs(bk_file - pf), abs(bk_rank - pr))
                # Bonus = (7 - friend_dist) means closer king → higher bonus
                eg_score += (7 - friend_dist) * self.eg_king_friend_passer
                # Bonus = enemy_dist means farther enemy king → higher bonus
                eg_score += enemy_dist * self.eg_king_enemy_passer

            for passer in black_passers:
                pf = chess.square_file(passer)
                pr = chess.square_rank(passer)
                friend_dist = max(abs(bk_file - pf), abs(bk_rank - pr))
                enemy_dist  = max(abs(wk_file - pf), abs(wk_rank - pr))
                eg_score -= (7 - friend_dist) * self.eg_king_friend_passer
                eg_score -= enemy_dist * self.eg_king_enemy_passer


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