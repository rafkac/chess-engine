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

# set up evaluator and search engine
evaluator = ClassicEvaluator()
engine = SearchEngine(evaluator)

# --- Helper functions ---
def draw_board():
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for rank in range(8):
        for file in range(8):
            color = colors[(rank + file) % 2]
            pygame.draw.rect(screen, color,
                             pygame.Rect(file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


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
    global board, selected_square, game_over, message
    board = chess.Board()
    selected_square = None
    game_over = False
    message = ""


# --- Main loop ---
while running:
    draw_board()
    draw_pieces()
    button_rect = draw_message()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            file = x // SQUARE_SIZE
            rank = 7 - (y // SQUARE_SIZE)
            square = chess.square(file, rank)

            if selected_square is None:
                # Select piece
                if board.piece_at(square) and board.piece_at(square).color == board.turn:
                    selected_square = square
            else:
                # Try to move
                move = chess.Move(selected_square, square)
                if move in board.legal_moves:
                    board.push(move)
                    selected_square = None
                    check_game_over
                    # Computer move
                    if not game_over:
                        best_move, score = engine.get_best_move(board, depth=3)
                        board.push(best_move)
                        check_game_over()
                else:
                    selected_square = None
        elif game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect and button_rect.collidepoint(event.pos):
                reset_game()
    # clock.tick(30)

pygame.quit()
