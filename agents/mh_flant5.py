from transformers import T5Tokenizer, T5ForConditionalGeneration
from mh_agent import MHAgent
from mh_chess import MHChess
import torch

class MHFLANT5(MHAgent):
    def __init__(self, model_name='google/flan-t5-base', color='white'):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model_name = model_name
        self.model = T5ForConditionalGeneration.from_pretrained(model_name, device_map='auto')
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.name = self.getname()
        self.color = color

    def getname(self):
        return self.model_name.split('/')[-1]

    def makeMove(self, board):
        prompt = self.generatePrompt(board)
        ans = self.generateResponse(prompt)
        ##  Validate the move...
        legal_moves = board.getLegalMoves()
        for move in legal_moves:
            if move in ans:
                return move, ans
        return None, ans


    def generateResponse(self, input_text):
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids.to(self.device)
        res_ids = self.model.generate(input_ids, max_length=1000)
        ans = self.tokenizer.decode(res_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return ans

    def generatePrompt(self, board):
        template = '{system_message}. {message}'
        system_message = f"You are a professional chess player. You are playing a game of chess as {self.color}. P, N, B, R, Q and K represent white pieces. p, n, b, r, q and k represent black pieces. It's your turn to make a move. You will get a list of legal moves you can make. You should choose one of them. You should only output the UCI notation of the move you want to make with no additional text."
        message = "Here's the current board state:\n\n" + str(board) + "\n\n"
        message += "Here's a list of possible moves:\n- "
        message += "\n- ".join(board.getLegalMoves()) + "\n\n"
        message += "Please make a move by choosing one of the above options. You should only output the UCI notation of the move you want to make with no additional text."
        return template.format(system_message=system_message, message=message)


if __name__ == "__main__":
    mh_flant5 = MHFLANT5()
    board = MHChess()
    for i in range(10):
        move, ans = mh_flant5.makeMove(board)
        print(move, ans)
        board.makeMove(move)
    