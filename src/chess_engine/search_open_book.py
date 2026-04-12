import chess
import chess.polyglot
import time


"""
search engine with opening book implementation
"""
BOOK_PATH = "opening_book/Perfect_2023.bin"

try:
    book_reader = chess.polyglot.open_reader(BOOK_PATH)
    print(f"Opening book loaded: {BOOK_PATH}")
except Exception as e:
    print(f"Could not load book: {e}")
    book_reader = None



class SearchEngineWithOpenings:
    ...