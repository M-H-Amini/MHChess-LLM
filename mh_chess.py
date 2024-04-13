import chess
import chess.svg
import cairosvg
import random
import os
import io

class MHChess(chess.Board):
    def __init__(self):
        super().__init__()

    def getLegalMoves(self):
        return [move.uci() for move in self.legal_moves]

    def makeMove(self, move):
        self.push(chess.Move.from_uci(move))

    def currentPlayer(self):
        return self.turn

    def board2Image(self, output_file):
        svg = chess.svg.board(self)
        cairosvg.svg2png(bytestring=svg.encode('utf-8'), write_to=output_file)



class MHFixture:
    def __init__(self, board, agent_white, agent_black):
        self.board = board
        self.agent_white = agent_white
        self.agent_black = agent_black

    def play(self, verbose=0):
        verbose and print(self.board)
        while not self.board.is_game_over():
            if self.board.currentPlayer() == chess.BLACK:
                move, valid, ans = self.agent_black.makeMove(self.board)
                if not valid:
                    print(f'Invalid move: {move}')
                    break
                self.board.makeMove(move)
                verbose and print('Black turn:\n' + str(self.board), '\n')
            else:
                move, valid, ans = self.agent_white.makeMove(self.board)
                if not valid:
                    print(f'Invalid move: {move}')
                    break
                self.board.makeMove(move)
                verbose and print('White turn:\n' + str(self.board), '\n')
        print(f'Game over: {self.board.result()}')
    

if __name__ == "__main__":
    from mh_random import MHRandom
    from mh_llama2 import MHLLama2

    board = MHChess()
    moves = board.getLegalMoves()
    board.board2Image('test.png')
    # agent_random = MHRandom()
    # agent_llama2 = MHLLama2()
    # fixture = MHFixture(board, agent_random, agent_llama2)
    # fixture.play(verbose=1)
    # board.fullRandomPlay()
    



