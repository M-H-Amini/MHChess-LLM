import chess
import chess.svg
import cairosvg
import random
import os
import io
import shutil as sh
import imageio
from PIL import Image, ImageDraw, ImageFont
from glob import glob
from tqdm import tqdm

class MHChess(chess.Board):
    def __init__(self, caption='MHChess'):
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

if __name__ == "__main__":
    from agents.mh_random import MHRandom
    from agents.mh_llama2 import MHLLama2
    from agents.mh_gpt import MHGPT
    from agents.mh_mistral import MHMistral
    from agents.mh_flant5 import MHFLANT5
    board = MHChess()
    # moves = board.getLegalMoves()
    # board.board2Image('test.png')
    agent_random = MHRandom()
    # agent_gpt = MHGPT()
    # agent_mistral = MHMistral()
    # agent_llama2 = MHLLama2()
    agent_flant5 = MHFLANT5('google/flan-t5-large')

    agent_white = agent_flant5
    agent_black = agent_random
    output_folder = f'{agent_white.name}_vs_{agent_black.name}'
    no = len(glob(f'{output_folder}*/'))
    output_folder += f'_{no:02d}'
    fixture = MHFixture(board, agent_white, agent_black)
    fixture.play(verbose=1)
    fixture.gif()
    