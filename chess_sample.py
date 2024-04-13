import chess

board = chess.Board()

##  List all legal moves for the current player as a list of strings in UCI format.
legals = [move.uci() for move in board.legal_moves]

print(legals)

##  Make a move on the board.
board.push(chess.Move.from_uci('e2e4'))

##  Print the board.
print(board)

##  List all legal moves for the current player as a list of strings in UCI format.
legals = [move.uci() for move in board.legal_moves]

print(legals)