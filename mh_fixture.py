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
import numpy as np

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
            output_folder = os.path.join('output', f'{agent_white.name}_vs_{agent_black.name}')
            no = len(glob(f'{output_folder}/*/'))
            output_folder = os.path.join(output_folder, f'{no:02d}')
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
                self.winner = self.agent_white.name
            case chess.BLACK:
                self.winner = self.agent_black.name
            case None:
                self.winner = 'Draw'
        with open(os.path.join('output', 'results.txt'), 'a') as f:
            f.write(f'{self.agent_white.name}, {self.agent_black.name}, {self.winner}, {self.white_rnd_no}, {self.black_rnd_no}, {self.cnt}\n')
            
    def getCaption(self):
        return f'White: {self.agent_white.name} - Black: {self.agent_black.name}'

    def board2Image(self):
        top_caption = self.getCaption()
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(os.path.join(self.output_folder, 'images'), exist_ok=True)
        no = len(os.listdir(os.path.join(self.output_folder, 'images')))
        output_file = os.path.join(self.output_folder, 'images', f'{no:04d}.png')
        self.board.board2Image(output_file)

    def gif(self, output_gif_path=None, duration=0.5, top_caption=None):
        if output_gif_path is None:
            filename = self.agent_white.name + '_vs_' + self.agent_black.name 
            no = len(glob(os.path.join('output', f'{filename}*.gif')))
            output_gif_path = os.path.join('output', filename + f'_{no:02d}.gif')

        
        if top_caption is None:
            top_caption = f' White: {self.agent_white.name} - Black: {self.agent_black.name}'
        winner_caption = f' Winner: {self.winner}' if self.winner != 'Draw' else 'Result = Draw'
        bottom_caption = ' MHChess - Github: M-H-Amini/MHChess'

        img_folder = os.path.join(self.output_folder, 'images')
        images = sorted([img for img in os.listdir(img_folder) if img.endswith(".png")])
        frames = []
        for image_filename in tqdm(images):
            image_path = os.path.join(img_folder, image_filename)
            image = self.editImage(image_path, winner_caption, top_caption, bottom_caption)
            frames.append(image)
            # frames.append(imageio.imread(image_path))
        imageio.mimsave(output_gif_path, frames, duration=duration)

    def editImage(self, image_path, winner_caption=None, top_caption=None, bottom_caption=None):
        if top_caption is None:
            top_caption = 'MHChess - Github: M-H-Amini/MHChess'
        if bottom_caption is None:
            bottom_caption = 'MHChess - Github: M-H-Amini/MHChess'

        image_org = Image.open(image_path)
        ##  Adding a black rectangle of 20 rows to the top of the image...
        image_rect = Image.new('RGB', (image_org.width, 20), color='black')
        image = Image.new('RGB', (image_org.width, image_org.height + 60), color='white')
        image.paste(image_rect, (0, 0))
        image.paste(image_rect, (0, 20))
        image.paste(image_org, (0, 40))
        image.paste(image_rect, (0, image_org.height + 40))
        draw = ImageDraw.Draw(image)
        font_path="arial.ttf"
        font_size=40
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
        font.size=40

        ##  Winner caption...
        bbox = draw.textbbox((0, 0), winner_caption, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        # text_width, text_height = image.width, 20
        x = (image.width - text_width) / 2
        y = 0
        draw.text((x, y), winner_caption, font=font, fill=(0, 255, 0))
        ##  Top caption...
        bbox = draw.textbbox((0, 0), top_caption, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (image.width - text_width) / 2
        y = 20 
        draw.text((x, y), top_caption, font=font, fill=(255, 255, 255))
        ##  Bottom caption...
        bbox = draw.textbbox((0, 0), bottom_caption, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (image.width - text_width) / 2
        y = image.height - 15
        draw.text((x, y), bottom_caption, font=font, fill='white')
        image.save(image_path)
        return image

    def log(self, text):
        log_file = os.path.join(self.output_folder, 'moves.log')
        with open(log_file, 'a') as f:
            f.write(text + '\n')
            


if __name__ == "__main__":
    from agents.mh_random import MHRandom
    from agents.mh_llama2 import MHLLama2
    from agents.mh_llama3 import MHLLama3
    from agents.mh_gpt import MHGPT
    from agents.mh_mistral import MHMistral
    from agents.mh_flant5 import MHFLANT5
    from agents.mh_gemma import MHGemma
    
    n_fixtures = 5
    agent_random = MHRandom()
    # agent_mistral = MHMistral()
    # agent_llama2 = MHLLama2()
    # agent_llama2 = MHLLama2(model_name='meta-llama/Llama-2-70b-chat-hf')
    # agent_llama3 = MHLLama3()
    agent_llama3 = MHLLama3(model_name='meta-llama/Meta-Llama-3-70B-Instruct')
    # agent_flant5 = MHFLANT5('google/flan-t5-base')
    # agent_flant5 = MHFLANT5('google/flan-t5-large')
    # agent_flant5 = MHFLANT5('google/flan-t5-xl')
    # agent_flant5 = MHFLANT5('google/flan-t5-xxl')
    # agent_gemma = MHGemma()
    # agent_gpt = MHGPT()
    # agent_gpt = MHGPT(model_name='gpt-4-turbo')

    agent_white = agent_llama3
    agent_black = agent_random
    for i in range(n_fixtures):
        print(f'Fixture {i+1}/{n_fixtures}')
        board = MHChess()
        fixture = MHFixture(board, agent_white, agent_black)
        fixture.play(verbose=1)
        fixture.gif()
        