import random
from chess_engine.evaluator import ClassicEvaluator
from chess_engine.search import SearchEngine
import chess
import pygame


# setup
WIDTH, HEIGHT = 640, 640
SQUARE_SIZE = 80

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Engine Prototype")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 36, bold=True)
small_font = pygame.font.SysFont("arial", 24)

# load pieces png
pieces = {}
for p in ["wp", "wn", "wb", "wr", "wk", "wq",
          "bp", "bn", "bb", "br", "bk", "bq"]:
    pieces[p] = pygame.transform.scale(
        pygame.image.load(f"pieces/{p}.png"), (SQUARE_SIZE, SQUARE_SIZE)
    )
    
# --- Game state ---
board = chess.Board()
selected_square = None
running = True
game_over = False
message = ""
promotion_pending = None  # will store (from_square, to_square) when promotion is needed
promotion_choice = None   # will store the chosen piece type

# set up evaluator and search engine
evaluator = ClassicEvaluator()
engine = SearchEngine(evaluator)

# --- Helper functions ---
def draw_board():
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for rank in range(8):
        for file in range(8):
            color = colors[(rank + file) % 2]   # alternate colors
            pygame.draw.rect(screen, color,
                             pygame.Rect(file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
    # highlight selected square
    if selected_square is not None:
        file = chess.square_file(selected_square)
        rank = 7 - chess.square_rank(selected_square)
        highlight_color = pygame.Color(255, 255, 0, 100)  # semi-transparent yellow
        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(highlight_color)
        screen.blit(highlight_surface, (file * SQUARE_SIZE, rank * SQUARE_SIZE))

        # highlight legal moves
        for move in board.legal_moves:
            if move.from_square == selected_square:
                target_file = chess.square_file(move.to_square)
                target_rank = 7 - chess.square_rank(move.to_square)

                # draw circle for legal move
                center_x = target_file * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = target_rank * SQUARE_SIZE + SQUARE_SIZE // 2
                
                if board.piece_at(move.to_square):  # capture
                    pygame.draw.circle(screen, pygame.Color("red"), 
                                     (center_x, center_y), 10)
                else:  # normal move
                    pygame.draw.circle(screen, pygame.Color("green"), 
                                     (center_x, center_y), 8)


def draw_pieces():
    for square, piece in board.piece_map().items():
        file = chess.square_file(square)
        rank = 7 - chess.square_rank(square)
        piece_str = piece.symbol()
        color = 'w' if piece_str.isupper() else 'b'
        img = pieces[color + piece_str.lower()]
        screen.blit(img, (file * SQUARE_SIZE, rank * SQUARE_SIZE))


# def make_random_move():
#     legal_moves = list(board.legal_moves)
#     if legal_moves:
#         move = random.choice(legal_moves)
#         board.push(move)


def check_game_over():
    global game_over, message
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            message = "Checkmate. Black wins."
        else:
            message = "Checkmate. White wins."
        game_over = True
    elif board.is_stalemate():
        message = "Stalemate."
        game_over = True
    elif board.is_insufficient_material():
        message = "Draw – insufficient material."
        game_over = True
    elif board.is_seventyfive_moves():
        message = "Draw – 75 move rule."
        game_over = True
    elif board.is_fivefold_repetition():
        message = "Draw – fivefold repetition."
        game_over = True


def draw_promotion_dialog():
    """Draw promotion piece selection dialog"""
    global promotion_pending
    
    if promotion_pending is None:
        return None
    
    # semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    # dialog box
    dialog_width = 400
    dialog_height = 250
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2
    
    pygame.draw.rect(screen, pygame.Color("white"), 
                     pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height),
                     border_radius=10)
    pygame.draw.rect(screen, pygame.Color("black"), 
                     pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height),
                     3, border_radius=10)
    
    # title
    title_text = small_font.render("Choose Promotion Piece", True, pygame.Color("black"))
    title_rect = title_text.get_rect(center=(WIDTH // 2, dialog_y + 30))
    screen.blit(title_text, title_rect)
    
    # Determine color
    color = 'w' if board.turn == chess.WHITE else 'b'
    
    # Piece options: Queen, Rook, Bishop, Knight
    piece_types = [
        (chess.QUEEN, 'q'),
        (chess.ROOK, 'r'),
        (chess.BISHOP, 'b'),
        (chess.KNIGHT, 'n')
    ]
    
    piece_rects = []
    piece_size = 80
    spacing = 20
    start_x = dialog_x + (dialog_width - (4 * piece_size + 3 * spacing)) // 2
    piece_y = dialog_y + 80
    
    for i, (piece_type, piece_char) in enumerate(piece_types):
        piece_x = start_x + i * (piece_size + spacing)
        
        # draw button background
        button_rect = pygame.Rect(piece_x, piece_y, piece_size, piece_size)
        pygame.draw.rect(screen, pygame.Color("lightgray"), button_rect, border_radius=5)
        pygame.draw.rect(screen, pygame.Color("black"), button_rect, 2, border_radius=5)
        
        # draw piece image
        piece_img = pieces[color + piece_char]
        screen.blit(piece_img, (piece_x, piece_y))
        
        piece_rects.append((button_rect, piece_type))
    
    return piece_rects


def draw_message():
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        text = font.render(message, True, pygame.Color("white"))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        screen.blit(text, text_rect)

        button_text = font.render("Play Again", True, pygame.Color("black"))
        button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 60)
        pygame.draw.rect(screen, pygame.Color("white"), button_rect, border_radius=10)
        pygame.draw.rect(screen, pygame.Color("black"), button_rect, 3, border_radius=10)
        screen.blit(button_text, (button_rect.x + 25, button_rect.y + 10))

        return button_rect
    return None

def reset_game():
    """reset game state to start a new game"""
    global board, selected_square, game_over, message
    board = chess.Board()
    selected_square = None
    game_over = False
    message = ""
    promotion_pending = None
    promotion_choice = None


def is_promotion_move(from_square, to_square):
    """Check if the move is a pawn promotion"""
    piece = board.piece_at(from_square)
    if piece is None or piece.piece_type != chess.PAWN:
        return False
    
    to_rank = chess.square_rank(to_square)
    # white promotes on rank 7
    if piece.color == chess.WHITE and to_rank == 7:
        return True
    # black promotes on rank 0
    if piece.color == chess.BLACK and to_rank == 0:
        return True
    
    return False    


def make_computer_move():
    """Execute engine move"""
    global game_over

    if not game_over:
        best_move, score = engine.get_best_move(board, depth=4)
        board.push(best_move)
        check_game_over()


# --- Main loop ---
while running:
    draw_board()
    draw_pieces()

    # draw promotion dialog if needed
    promotion_rects = None
    if promotion_pending:
        promotion_rects = draw_promotion_dialog()
    
    # draw game over message if needed
    button_rect = draw_message()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif promotion_pending and event.type == pygame.MOUSEBUTTONDOWN:
            # handle promotion piece selection
            if promotion_rects:
                for rect, piece_type in promotion_rects:
                    if rect.collidepoint(event.pos):
                        # create the promotion move
                        from_square, to_square = promotion_pending
                        move = chess.Move(from_square, to_square, promotion=piece_type)

                        if move in board.legal_moves:
                            board.push(move)
                            check_game_over()

                            # computer move
                            make_computer_move()

                        # reset promotion state
                        promotion_pending = None
                        promotion_choice = None
                        break

        elif not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            file = x // SQUARE_SIZE
            rank = 7 - (y // SQUARE_SIZE)
            square = chess.square(file, rank)

            if selected_square is None:
                # select piece
                if board.piece_at(square) and board.piece_at(square).color == board.turn:
                    selected_square = square
            else:
                # try to move
                # check if it's a promotion move
                if is_promotion_move(selected_square, square):
                    # ensure move is legal first
                    test_move = chess.Move(selected_square, square, promotion=chess.QUEEN)
                    if test_move in board.legal_moves:
                        promotion_pending = (selected_square, square)
                        selected_square = None

                # normal move (non-promotion)
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        board.push(move)
                        selected_square = None
                        check_game_over()

                        # computer move
                        if not game_over:
                            make_computer_move()
                    else:
                        selected_square = None

        elif game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect and button_rect.collidepoint(event.pos):
                reset_game()

pygame.quit()
