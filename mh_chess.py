import chess
import chess.svg
import cairosvg
import random
import os
import io
import shutil as sh
import imageio
from PIL import Image, ImageDraw, ImageFont

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
        draw.text((x, y), top_caption, font=font, fill='white')
        ##  Bottom caption
        text_width, text_height = image.width, 10
        x = (image.width - text_width) / 2
        y = image.height - 10
        draw.text((x, y), bottom_caption, font=font, fill='white')

        image.save(output_file)
        



class MHFixture:
    def __init__(self, board, agent_white, agent_black):
        self.board = board
        self.agent_white = agent_white
        self.agent_black = agent_black
        self.white_rnd_no = 0
        self.black_rnd_no = 0

    def play(self, verbose=0, output_folder=None):
        verbose and print(self.board)
        output_folder and sh.rmtree(output_folder)
        output_folder and self.board2Image(output_folder)

        while not self.board.is_game_over():
            if self.board.currentPlayer() == chess.BLACK:
                move, valid, ans = self.agent_black.makeMove(self.board)
                if not valid:  ##  If the move is invalid, do a random move...
                    print(f'Invalid move from black: {move} -> Random move')
                    self.black_rnd_no -=- 1
                    move = random.choice(self.board.getLegalMoves())
                self.board.makeMove(move)
                verbose and print('Black turn:\n' + str(self.board), '\n')
            else:
                move, valid, ans = self.agent_white.makeMove(self.board)
                if not valid:
                    print(f'Invalid move from white: {move} -> Random move')
                    self.white_rnd_no -=- 1
                    move = random.choice(self.board.getLegalMoves())
                self.board.makeMove(move)
                verbose and print('White turn:\n' + str(self.board), '\n')
            output_folder and self.board2Image(output_folder)
        print(f'Game over: {self.board.result()}')
        print(f'White random moves: {self.white_rnd_no}')
        print(f'Black random moves: {self.black_rnd_no}')
        print(type(self.board.result()))

    def board2Image(self, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(os.path.join(output_folder, 'images'), exist_ok=True)
        no = len(os.listdir(os.path.join(output_folder, 'images')))
        output_file = os.path.join(output_folder, 'images', f'{no:04d}.png')
        self.board.board2Image(output_file)

    def gif(self, img_folder, output_gif_path='output.gif', duration=0.5):
        images = sorted([img for img in os.listdir(img_folder) if img.endswith(".png")])
        frames = []
        for image_filename in images:
            image_path = os.path.join(img_folder, image_filename)
            frames.append(imageio.imread(image_path))
        imageio.mimsave(output_gif_path, frames, duration=duration)



    

if __name__ == "__main__":
    from mh_random import MHRandom
    from mh_llama2 import MHLLama2

    board = MHChess()
    # moves = board.getLegalMoves()
    board.board2Image('test.png')
    # agent_random = MHRandom()
    # # # agent_llama2 = MHLLama2()
    # fixture = MHFixture(board, agent_random, agent_random)
    # fixture.play(verbose=0, output_folder='output')
    # fixture.gif('output/images', 'output.gif')
    



