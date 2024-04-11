import chess
import chess.svg
import random
# from cairosvg import svg2png
import os

class MHChess(chess.Board):
    def __init__(self):
        super().__init__()

    def getLegalMoves(self):
        return [move.uci() for move in self.legal_moves]

    def makeMove(self, move):
        self.push(chess.Move.from_uci(move))

    def currentPlayer(self):
        return self.turn

    def fullRandomPlay(self, output_folder=None):
        ##  If output_folder is not None, save the board pictures in each step to the output_folder.
        while not self.is_game_over():
            current_player = self.currentPlayer()
            move = random.choice(self.getLegalMoves())
            print(f'Current player: {current_player} - Move: {move}')
            self.makeMove(move)
            print(self)
        print(f'Game over: {self.result()}')
    

if __name__ == "__main__":
    board = MHChess()
    board.fullRandomPlay()
    



