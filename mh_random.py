from mh_agent import MHAgent
from mh_chess import MHChess
import random

class MHRandom(MHAgent):
    def __init__(self):
        self.name = 'Random'

    def makeMove(self, board):
        legal_moves = board.getLegalMoves()
        return (move:=random.choice(legal_moves)), move

    def generateResponse(self, input_text):
        pass

    def generatePrompt(self, board):
        pass


if __name__ == "__main__":
    mh_random = MHRandom()
    board = MHChess()
    ans = mh_random.makeMove(board)
    print(ans)
    