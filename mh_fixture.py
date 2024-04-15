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
from mh_chess import MHChess

class MHFixture:
    def __init__(self, board, agent_white, agent_black, output_folder=None):
        self.board = board
        self.agent_white = agent_white
        self.agent_black = agent_black
        self.agent_white.color = 'white'
        self.agent_black.color = 'black'
        self.white_rnd_no = 0  ##  Number of random moves by white
        self.black_rnd_no = 0  ##  Number of random moves by black
        if output_folder is None:
            output_folder = f'{agent_white.name}_vs_{agent_black.name}'
            no = len(glob(f'{output_folder}*/'))
            output_folder = os.path.join('output', output_folder, f'_{no:02d}')
        self.output_folder = output_folder

    def play(self, verbose=0):
        verbose and print(self.board)
        self.board2Image()
        self.cnt = 0

        while not self.board.is_game_over():
            if self.board.currentPlayer() == chess.BLACK:
                move, ans = self.agent_black.makeMove(self.board)
                self.log(f'Black: {move} - {ans}')
                if move is None:  ##  If the move is invalid, do a random move...
                    print(f'Invalid move from black: {move} -> Random move')
                    self.black_rnd_no -=- 1
                    move = random.choice(self.board.getLegalMoves())
                self.board.makeMove(move)
                verbose and print('Black turn:\n' + str(self.board), '\n')
            else:
                move, ans = self.agent_white.makeMove(self.board)
                self.log(f'White: {move} - {ans}')
                if move is None:
                    print(f'Invalid move from white: {move} -> Random move')
                    self.white_rnd_no -=- 1
                    move = random.choice(self.board.getLegalMoves())
                self.board.makeMove(move)
                verbose and print('White turn:\n' + str(self.board), '\n')
            self.board2Image()
            self.cnt -=- 1

        print(f'Game over: {self.board.result()}')
        print(f'White random moves: {self.white_rnd_no}')
        print(f'Black random moves: {self.black_rnd_no}')
        ##  Save the result...
        match self.board.outcome().winner:
            case chess.WHITE:
                winner = self.agent_white.name
            case chess.BLACK:
                winner = self.agent_black.name
            case None:
                winner = 'Draw'
        with open(os.path.join('output', 'results.txt'), 'a') as f:
            f.write(f'{self.agent_white.name}, {self.agent_black.name}, {winner}, {self.white_rnd_no}, {self.black_rnd_no}, {self.cnt}\n')
            
    def getCaption(self):
        return f'White: {self.agent_white.name} - Black: {self.agent_black.name}'

    def board2Image(self):
        top_caption = self.getCaption()
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(os.path.join(self.output_folder, 'images'), exist_ok=True)
        no = len(os.listdir(os.path.join(self.output_folder, 'images')))
        output_file = os.path.join(self.output_folder, 'images', f'{no:04d}.png')
        self.board.board2Image(output_file, top_caption)

    def gif(self, output_gif_path=None, duration=0.5):
        if output_gif_path is None:
            filename = self.agent_white.name + '_vs_' + self.agent_black.name 
            no = len(glob(os.path.join('output', f'{filename}*.gif')))
            output_gif_path = os.path.join('output', filename + f'_{no:02d}.gif')

        img_folder = os.path.join(self.output_folder, 'images')
        images = sorted([img for img in os.listdir(img_folder) if img.endswith(".png")])
        frames = []
        for image_filename in tqdm(images):
            image_path = os.path.join(img_folder, image_filename)
            frames.append(imageio.imread(image_path))
        imageio.mimsave(output_gif_path, frames, duration=duration)

    def log(self, text):
        log_file = os.path.join(self.output_folder, 'moves.log')
        with open(log_file, 'a') as f:
            f.write(text + '\n')
            


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
    agent_flant5 = MHFLANT5('google/flan-t5-base')

    agent_white = agent_flant5
    agent_black = agent_random
    output_folder = f'{agent_white.name}_vs_{agent_black.name}'
    no = len(glob(f'{output_folder}*/'))
    output_folder += f'_{no:02d}'
    fixture = MHFixture(board, agent_white, agent_black)
    fixture.play(verbose=1)
    fixture.gif()
    