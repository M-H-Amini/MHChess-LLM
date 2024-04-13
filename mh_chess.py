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

    def board2Image(self, output_file, top_caption=None):
        if top_caption is None:
            top_caption = 'MHChess - Github: M-H-Amini/MHChess'
        bottom_caption = 'MHChess - Github: M-H-Amini/MHChess'
        svg = chess.svg.board(self)
        # cairosvg.svg2png(bytestring=svg.encode('utf-8'), write_to=output_file)
        png_bytes = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
        image_org = Image.open(io.BytesIO(png_bytes))
        ##  Add a black rectangle of 20 rows to the top of the image
        image_rect = Image.new('RGB', (image_org.width, 20), color='black')
        image = Image.new('RGB', (image_org.width, image_org.height + 40), color='white')
        image.paste(image_rect, (0, 0))
        image.paste(image_org, (0, 20))
        image.paste(image_rect, (0, image_org.height + 20))
        draw = ImageDraw.Draw(image)
        font_path="arial.ttf"
        font_size=20
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        ##  Top caption
        text_width, text_height = image.width, 10
        x = (image.width - text_width) / 2
        y = 0 
        draw.text((x, y), top_caption, font=font, fill=(0, 255, 0))
        ##  Bottom caption
        text_width, text_height = image.width, 10
        x = (image.width - text_width) / 2
        y = image.height - 10
        draw.text((x, y), bottom_caption, font=font, fill='white')

        image.save(output_file)
        

class MHFixture:
    def __init__(self, board, agent_white, agent_black, output_folder=None):
        self.board = board
        self.agent_white = agent_white
        self.agent_black = agent_black
        self.white_rnd_no = 0
        self.black_rnd_no = 0
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
    from mh_random import MHRandom
    from mh_llama2 import MHLLama2
    from mh_gpt import MHGPT

    board = MHChess()
    # moves = board.getLegalMoves()
    # board.board2Image('test.png')
    agent_random = MHRandom()
    agent_gpt = MHGPT()
    # agent_llama2 = MHLLama2()
    agent_white = agent_random
    agent_black = agent_random
    output_folder = f'{agent_white.name}_vs_{agent_black.name}'
    no = len(glob(f'{output_folder}*/'))
    output_folder += f'_{no:02d}'
    fixture = MHFixture(board, agent_gpt, agent_random)
    fixture.play(verbose=1)
    fixture.gif()
    