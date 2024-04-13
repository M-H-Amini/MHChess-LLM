from mh_agent import MHAgent
from mh_chess import MHChess
from openai import OpenAI
import openai

class MHGPT(MHAgent):
    def __init__(self, model_name='gpt3', key_file='openai_key.txt'):
        self.model_name = model_name
        self.name = self.getname()
        self.openai_key = open(key_file).read().strip().rstrip()
        self.client = OpenAI(api_key=self.openai_key)
    
    def getname(self):
        return 'gpt-3.5-turbo-0125'

    def makeMove(self, board):
        prompt = self.generatePrompt(board)
        ans = self.generateResponse(prompt)
        legal_moves = board.getLegalMoves()
        for move in legal_moves:
            if move in ans:
                return move, ans
        return None, ans



    def generateResponse(self, prompt):
        system_message = "You are a professional chess player. You are playing a game of chess. It's your turn to make a move. You will get a list of legal moves you can make. You should choose one of them. You should only output the UCI notation of the move you want to make with no additional text."
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )
        ans = response.choices[0].message.content
        
        return ans

    def generatePrompt(self, board):
        message = "Here's the current board state:\n\n" + str(board) + "\n\n"
        message += "Here's a list of possible moves:\n- "
        message += "\n- ".join(board.getLegalMoves()) + "\n\n"
        message += "Please make a move by choosing one of the above options."
        return message

if __name__ == "__main__":
    mh_gpt = MHGPT()
    board = MHChess()
    print(mh_gpt.generatePrompt(board))
    move, status, ans = mh_gpt.makeMove(board)
    # for i in range(1):
    #     move, status, ans = mh_gpt.makeMove(board)
    #     print(ans, status)
    #     board.makeMove(move)
    